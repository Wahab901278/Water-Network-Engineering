# Optimizer with smarter parameter control and scoring

import random
import os
import csv
from src.loader import load_network
from src.analyze_pressure_and_flow import analyze_pressure_and_flow
from disturbance.calculate_water_age import checkWaterAgeAfterDisturbances
from disturbance.calculate_supply_loss_percentage import calculate_supply_loss_percentage
from .add_adaptive_pumps import add_adaptive_pumps
from .add_loops_to_critical_areas import add_loops_to_critical_areas
from .add_tanks_with_replacement import add_tanks_with_correct_placement
from .install_prvs import install_prvs
from src.utils import save_network_to_inp_file
from src.config import REV_CITY_ZONE_AGING_FACTOR,REV_CITY_ZONE_LEAK_FACTOR,REV_CITY_ZONE_LOOP_COUNT,REV_CITY_ZONE_MAX_PUMPS,REV_CITY_ZONE_MAX_TANKS,REV_CITY_ZONE_REQUIRED_PRESSURE
from src.config import RURAL_SIMPLE_AGING_FACTOR,RURAL_SIMPLE_LEAK_FACTOR,RURAL_SIMPLE_LOOP_COUNT,RURAL_SIMPLE_MAX_PUMPS,RURAL_SIMPLE_MAX_TANKS,RURAL_SIMPLE_REQUIRED_PRESSURE
from src.config import REV_SIMPLE_REQUIRED_PRESSURE,REV_SIMPLE_AGING_FACTOR,REV_SIMPLE_LEAK_FACTOR,REV_SIMPLE_LOOP_COUNT,REV_SIMPLE_MAX_PUMPS,REV_SIMPLE_MAX_TANKS
def evaluate_score(age_before, age_after, loss_before, loss_after):
    age_reduction_pct = ((age_before - age_after) / age_before) * 100
    loss_reduction_pct = ((loss_before - loss_after) / loss_before) * 100
    return age_reduction_pct + loss_reduction_pct

def search_best_resilience_parameters(network_path, age_before, loss_before, pump_names, low_pressure_junctions, low_flow_pipes, critical_junctions, high_pressure_junctions, base_required_pressure, trials=10):
    best_score = float('-inf')
    best_config = {}
    temp_network_dir = "temp_networks"
    os.makedirs(temp_network_dir, exist_ok=True)

    results_csv = os.path.join(temp_network_dir, "trial_results.csv")
    with open(results_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Trial", "AgeBefore", "AgeAfter", "LossBefore", "LossAfter", "Score"])

        for i in range(trials):
            wn = load_network(network_path)
            node_count = len(wn.junction_name_list)

            # Param bounds based on network size
            if node_count < 50:
                leak_factor = 1.05
                aging_factor = 0.95
                pressure_range = (20, 35)
                max_pump_range = (0, 2)
                max_tanks = random.randint(0, 2)
                loop_count = random.randint(0, 3)
                threshold_population = 25
            elif node_count < 100:
                leak_factor = 1.2
                aging_factor = 0.9
                pressure_range = (30, 50)
                max_pump_range = (1, 4)
                max_tanks = random.randint(0, 4)
                loop_count = random.randint(2, 6)
                threshold_population = 50
            else:
                leak_factor = 1.4
                aging_factor = 0.8
                pressure_range = (30, 70)
                max_pump_range = (3, 8)
                max_tanks = random.randint(1, 6)
                loop_count = random.randint(5, 12)
                threshold_population = 100

            required_pressure = round(random.uniform(*pressure_range), 1)
            max_pumps = random.randint(*max_pump_range)

            print(f"\nTrial {i+1}: leak={leak_factor}, aging={aging_factor}, pressure={required_pressure}, pumps={max_pumps}, loops={loop_count}, tanks={max_tanks}")

            wn, _ = add_adaptive_pumps(wn, low_pressure_junctions, max_pumps)
            wn, _ = add_tanks_with_correct_placement(wn, critical_junctions, max_tanks)
            wn, _ = install_prvs(wn, high_pressure_junctions, required_pressure)
            wn, _ = add_loops_to_critical_areas(wn, critical_junctions, loop_count)

            temp_network_path = f"{temp_network_dir}/temp_network_trial_{i+1}.inp"
            save_network_to_inp_file(wn, temp_network_path)

            age_after = checkWaterAgeAfterDisturbances(
                temp_network_path,
                pump_names=pump_names,
                shut_time=5, on_time=20,
                leak_factor=leak_factor,
                aging_factor=aging_factor,
                requiredPressure=required_pressure,
                time_interval=24,
                threshold_population=threshold_population,
                threshold_wsa=0.8,
                title=f"Trial {i+1} - Water Age After",
                folder_path="visualizations/temp/"
            ).mean()

            _, _, loss_after = calculate_supply_loss_percentage(
                temp_network_path,
                pump_names=pump_names,
                shut_time=5, on_time=20,
                leak_factor=leak_factor,
                aging_factor=aging_factor,
                requiredPressure=required_pressure,
                threshold_population=threshold_population,
                threshold_wsa=0.8,
                title=f"Trial {i+1} - Supply Loss After",
                figure_path="visualizations/after-resilience"
            )

            score = evaluate_score(age_before, age_after, loss_before, loss_after)
            print(f"→ Trial Score: {score:.2f} | Age ↓ {age_before:.2f} → {age_after:.2f} | Loss ↓ {loss_before:.2f}% → {loss_after:.2f}%")
            writer.writerow([i+1, age_before, age_after, loss_before, loss_after, score])

            if score > best_score:
                best_score = score
                best_config = {
                    "leak_factor": leak_factor,
                    "aging_factor": aging_factor,
                    "required_pressure": required_pressure,
                    "max_pumps": max_pumps,
                    "loop_count": loop_count,
                    "max_tanks": max_tanks,
                    "score": score,
                    "age_after": age_after,
                    "loss_after": loss_after,
                    "age_before": age_before,
                    "loss_before": loss_before
                }
                best_wn = wn

        if best_config:
            best_path = f"{temp_network_dir}/best_network_configuration.inp"
            save_network_to_inp_file(best_wn, best_path)
            print(f"\n✅ Best network configuration saved to: {best_path}")

    return best_config
