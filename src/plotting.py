import matplotlib.pyplot as plt
import wntr

def plot_water_age_over_time(wn,t,file_path):
    wn.options.quality.parameter = 'AGE'
    
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()

    age = results.node['quality']

    plt.figure(figsize=(10, 6))
    plt.plot(age.index / 3600, age.mean(axis=1))
    plt.xlabel('Time (hours)')
    plt.ylabel('Average Water Age (hours)')
    plt.title(t)
    plt.grid(True)
    plt.savefig(f"{file_path}water-age.jpg")
    return age

def plotWaterserviceAvailabilityOverTime(wn, t, requiredPressure,file_path):
    """Function to plot water service availability over time
       Parameters: 1) INP file 2) title 3) required pressure
       Returns: Time series plot of water service availability over time
    """
    
    wn.options.hydraulic.demand_model = 'PDD'
    wn.options.hydraulic.required_pressure = requiredPressure
    
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()

    expected_demand = wntr.metrics.expected_demand(wn)
    demand = results.node['demand'].loc[:, wn.junction_name_list]
    wsa_time_series = wntr.metrics.water_service_availability(expected_demand.sum(axis=0), demand)

    plt.figure(figsize=(10, 6))
    plt.plot(wsa_time_series.index / 3600, wsa_time_series.mean(axis=1))
    plt.xlabel('Time (hours)')
    plt.ylabel('Average Water Service Availability')
    plt.title(t)
    plt.grid(True)
    plt.savefig(f"{file_path}wsa.jpg")

    return wsa_time_series