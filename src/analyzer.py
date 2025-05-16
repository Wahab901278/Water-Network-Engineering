import wntr
import matplotlib.pyplot as plt
import os
def average_pressure_cv(wn):
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()
    pressure = results.node['pressure']
    pressure_range = pressure.max(axis=0) - pressure.min(axis=0)
    pressure_var = pressure.std(axis=0)
    pressure_mean = pressure.mean(axis=0)
    pressure_cv = (pressure_var / pressure_mean) * 100

    return {
        'average_pressure': pressure_mean.mean(),
        'cv': pressure_cv.mean(),
        'range': pressure_range.mean(),
        'std': pressure_var.mean()
    }


def checkWaterserviceAvalibility(wn,t,requiredPressure,folder_path):
    wn.options.hydraulic.demand_model = 'PDD'
    wn.options.hydraulic.required_pressure = requiredPressure
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()
    expected_demand = wntr.metrics.expected_demand(wn)
    demand = results.node['demand'].loc[:,wn.junction_name_list]
    wsa = wntr.metrics.water_service_availability(expected_demand.sum(axis=0), demand.sum(axis=0))
    ax = wntr.graphics.plot_network(wn, node_attribute=wsa, title=t)
    fig = ax.get_figure()
    file_name="wsa-graph-jpg"
    file_path = os.path.join(folder_path, file_name)
    fig.savefig(file_path, dpi=300, bbox_inches='tight') 
    return wsa

def checkWaterage(wn,t,timeinterval,folder_path):
    wn.options.quality.parameter = 'AGE'
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()
    age = results.node['quality']
    age_in_that_interval = age.loc[age.index[-1]-timeinterval*3600:age.index[-1]] #change this based on network size
    average_age = age_in_that_interval.mean()/3600 
    ax = wntr.graphics.plot_network(wn, node_attribute=average_age, title=t)
    fig = ax.get_figure()
    file_name="waterage-graph-jpg"
    file_path = os.path.join(folder_path, file_name)
    fig.savefig(file_path, dpi=300, bbox_inches='tight') 
    return average_age



