import wntr
from src.criticaljunctions import get_critical_junctions
from src.loader import load_network
from .pump_control import add_pump_control
import os
def checkWaterAgeAfterDisturbances(wn_file, pump_names, shut_time, on_time, leak_factor, aging_factor, requiredPressure, time_interval, threshold_population=100, threshold_wsa=0.8, title="Water Age After Disturbances",folder_path=""):    
    waterNetwork = load_network(wn_file)
    waterNetwork.options.time.duration = 48 * 3600
    waterNetwork.options.quality.parameter = 'AGE'
    waterNetwork.options.hydraulic.demand_model = 'PDD'
    waterNetwork.options.hydraulic.required_pressure = requiredPressure

    sim_before = wntr.sim.EpanetSimulator(waterNetwork)
    results_before = sim_before.run_sim()

    expected_demand_before = wntr.metrics.expected_demand(waterNetwork)
    demand_before = results_before.node['demand'].loc[:, waterNetwork.junction_name_list]
    wsa_before = wntr.metrics.water_service_availability(expected_demand_before, demand_before)

    for pump_name in pump_names:
        add_pump_control(waterNetwork, pump_name, shut_time, on_time)
    critical_junctions = get_critical_junctions(waterNetwork, requiredPressure, threshold_population, threshold_wsa)

    for pipe_name in waterNetwork.pipe_name_list:
        pipe = waterNetwork.get_link(pipe_name)
        start_node = pipe.start_node_name
        end_node = pipe.end_node_name

        if start_node in critical_junctions.index:
            waterNetwork.get_node(start_node).demand_timeseries_list[0].base_value *= leak_factor
        if end_node in critical_junctions.index:
            waterNetwork.get_node(end_node).demand_timeseries_list[0].base_value *= leak_factor
        if start_node in critical_junctions.index or end_node in critical_junctions.index:
            pipe.diameter *= aging_factor

    sim_after = wntr.sim.EpanetSimulator(waterNetwork)
    results_after = sim_after.run_sim()

    age = results_after.node['quality']
    age_in_interval = age.loc[age.index[-1] - time_interval * 3600 : age.index[-1]]  
    average_age_after_disturbance = age_in_interval.mean() / 3600 

    ax = wntr.graphics.plot_network(waterNetwork, node_attribute=average_age_after_disturbance, title=title)
    fig = ax.get_figure()
    file_name="waterage_after_disturbance_graph.jpg"
    file_path = os.path.join(folder_path, file_name)
    fig.savefig(file_path, dpi=300, bbox_inches='tight') 
    return average_age_after_disturbance

