import wntr
from .pump_control import add_pump_control
import matplotlib.pyplot as plt
def simulatePumpControl(wn, pump_names, shut_time, on_time, requiredPressure, title_before, title_after,figure_path):

    wn.options.hydraulic.demand_model = 'PDD'
    wn.options.hydraulic.required_pressure = requiredPressure

    sim_before = wntr.sim.EpanetSimulator(wn)
    results_before = sim_before.run_sim()

    expected_demand_before = wntr.metrics.expected_demand(wn)
    demand_before = results_before.node['demand'].loc[:, wn.junction_name_list]
    wsa_before = wntr.metrics.water_service_availability(expected_demand_before, demand_before)

    for pump_name in pump_names:
        add_pump_control(wn, pump_name, shut_time, on_time)

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
    plt.title(f'Comparison of WSA Before and After Pump Control ({title_after})')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'{figure_path}/wsa_before_&_after_pump_control.jpg')