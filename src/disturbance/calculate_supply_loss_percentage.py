from .simulate_combined_disturbances import simulateCombinedDisturbances
def calculate_supply_loss_percentage(
    wn_file, pump_names, shut_time, on_time, leak_factor, aging_factor,
    requiredPressure, threshold_population=100, threshold_wsa=0.8,
    title="WSA and Supply Loss Due to Disturbances", figure_path=""
):
    wsa_before, wsa_after, _ = simulateCombinedDisturbances(
        wn_file, pump_names, shut_time, on_time, leak_factor, aging_factor,
        requiredPressure, threshold_population, threshold_wsa,
        title, figure_path=figure_path 
    )

    total_expected_demand_before = wsa_before.mean(axis=1).sum()
    total_actual_demand_after = wsa_after.mean(axis=1).sum()

    supply_loss = total_expected_demand_before - total_actual_demand_after
    supply_loss_percentage = (supply_loss / total_expected_demand_before) * 100

    return wsa_before, wsa_after, supply_loss_percentage
