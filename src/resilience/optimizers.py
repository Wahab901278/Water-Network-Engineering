import random
from src.loader import load_network
from src.analyze_pressure_and_flow import analyze_pressure_and_flow
from disturbance.calculate_water_age import checkWaterAgeAfterDisturbances
from disturbance.calculate_supply_loss_percentage import calculate_supply_loss_percentage
from .add_adaptive_pumps import add_adaptive_pumps
from .add_loops_to_critical_areas import add_loops_to_critical_areas
from .add_tanks_with_replacement import add_tanks_with_correct_placement
from .install_prvs import install_prvs
from src.utils import save_network_to_inp_file
# from src.save_network_summary import save_network_to_inp_file

def evaluate_score(age_before, age_after, loss_before, loss_after, weight_age=1.5, weight_loss=1.0):
    """
    Higher score means better performance. Lower water age and supply loss are better.
    """
    age_drop = age_before - age_after
    loss_drop = loss_before - loss_after
    score = (age_drop * weight_age) + (loss_drop * weight_loss)
    return score

def search_best_resilience_parameters(network_path, age_before, loss_before, pump_names,low_pressure_junctions,low_flow_pipes,critical_junctions,high_pressure_junctions, trials=10):
    best_score = float('-inf')
    best_config = {}

    for i in range(trials):
        # Randomly generate trial parameters
        leak_factor = round(random.uniform(1.1, 1.5), 2)
        aging_factor = round(random.uniform(0.6, 0.9), 2)
        required_pressure = round(random.uniform(30, 60), 1)
        max_pumps = random.randint(3, 8)
        loop_count = random.randint(5, 10)

        print(f"\nTrial {i+1}: leak={leak_factor}, aging={aging_factor}, pressure={required_pressure}")

        # Load base network
        wn = load_network(network_path)

        # Apply resilience
        wn, _ = add_adaptive_pumps(wn, low_pressure_junctions, max_pumps)
        wn, _ = add_tanks_with_correct_placement(wn, critical_junctions)
        wn, _ = install_prvs(wn, high_pressure_junctions, required_pressure)
        wn, _ = add_loops_to_critical_areas(wn, critical_junctions, loop_count)

        # Save updated network
        temp_network_path = f"temp_network_trial_{i+1}.inp"
        save_network_to_inp_file(wn, temp_network_path)

        # Evaluate water age
        age_after = checkWaterAgeAfterDisturbances(
            temp_network_path,
            pump_names=pump_names,
            shut_time=5, on_time=20,
            leak_factor=leak_factor,
            aging_factor=aging_factor,
            requiredPressure=required_pressure,
            time_interval=24,
            threshold_population=100,
            threshold_wsa=0.8,
            title=f"Trial {i+1} - Water Age After",
            folder_path="visualizations/temp/"
        ).mean()

        # Evaluate supply loss
        _, _, loss_after = calculate_supply_loss_percentage(
            temp_network_path,
            pump_names=pump_names,
            shut_time=5, on_time=20,
            leak_factor=leak_factor,
            aging_factor=aging_factor,
            requiredPressure=required_pressure,
            threshold_population=100,
            threshold_wsa=0.8,
            title=f"Trial {i+1} - Supply Loss After"
        )

        # Score = lower age & loss → higher score
        score = evaluate_score(age_before, age_after, loss_before, loss_after)
        print(f"→ Trial Score: {score:.2f} | Age ↓ {age_before:.2f} → {age_after:.2f} | Loss ↓ {loss_before:.2f}% → {loss_after:.2f}%")

        if score > best_score:
            best_score = score
            best_config = {
                "leak_factor": leak_factor,
                "aging_factor": aging_factor,
                "required_pressure": required_pressure,
                "max_pumps": max_pumps,
                "loop_count": loop_count,
                "score": score,
                "age_after": age_after,
                "loss_after": loss_after
            }

    return best_config
