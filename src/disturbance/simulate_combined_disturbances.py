import wntr
import matplotlib.pyplot as plt
from .pump_control import add_pump_control
from src.criticaljunctions import get_critical_junctions
from src.loader import load_network
import os
def simulateCombinedDisturbances(wn_file, pump_names, shut_time, on_time, leak_factor, aging_factor, requiredPressure, threshold_population=100, threshold_wsa=0.8, title="WSA Before and After Combined Disturbances",figure_path=""):
    wn=load_network(wn_file)

    wn.options.time.duration=48*3600
    wn.options.hydraulic.demand_model = 'PDD'
    wn.options.hydraulic.required_pressure = requiredPressure

    sim_before = wntr.sim.EpanetSimulator(wn)
    results_before = sim_before.run_sim()

    expected_demand_before = wntr.metrics.expected_demand(wn)
    demand_before = results_before.node['demand'].loc[:, wn.junction_name_list]
    wsa_before = wntr.metrics.water_service_availability(expected_demand_before, demand_before)

    for pump_name in pump_names:
        add_pump_control(wn, pump_name, shut_time, on_time)

    critical_junctions = get_critical_junctions(wn, requiredPressure, threshold_population, threshold_wsa)

    critical_junctions = critical_junctions[critical_junctions.index.isin(wn.junction_name_list)]

    for pipe_name in wn.pipe_name_list:
        pipe = wn.get_link(pipe_name)
        start_node = pipe.start_node_name
        end_node = pipe.end_node_name

        if start_node in critical_junctions.index:
            wn.get_node(start_node).demand_timeseries_list[0].base_value *= leak_factor
        if end_node in critical_junctions.index:
            wn.get_node(end_node).demand_timeseries_list[0].base_value *= leak_factor

    for pipe_name in wn.pipe_name_list:
        pipe = wn.get_link(pipe_name)
        start_node = pipe.start_node_name
        end_node = pipe.end_node_name

        if start_node in critical_junctions.index or end_node in critical_junctions.index:
            pipe.diameter *= aging_factor

    sim_after = wntr.sim.EpanetSimulator(wn)
    results_after = sim_after.run_sim()

    expected_demand_after = wntr.metrics.expected_demand(wn)
    demand_after = results_after.node['demand'].loc[:, wn.junction_name_list]
    wsa_after = wntr.metrics.water_service_availability(expected_demand_after, demand_after)

    plt.figure(figsize=(12, 6))
    plt.plot(wsa_before.index / 3600, wsa_before.mean(axis=1), label='WSA Before', linestyle='--', marker='o')
    plt.plot(wsa_after.index / 3600, wsa_after.mean(axis=1), label='WSA After', linestyle='-', marker='x')
    plt.xlabel('Time (Hours)')
    plt.ylabel('Average Water Service Availability')
    plt.title(f'{title}')
    plt.legend()
    plt.grid(True)
    safe_title = title.replace(" ", "_").replace("/", "-")
    plt.savefig(os.path.join(figure_path, f"{safe_title}_combined_disturbances.jpg"))

    return wsa_before,wsa_after,results_after

