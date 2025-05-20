import wntr
from loader import load_network
def check_pressure_trend_with_sorted_average(wn_file, duration_hours=48, time_step_seconds=3600):
    
    waterNetwork = load_network(wn_file)
    waterNetwork.options.time.duration = duration_hours * 3600 
    
    sim = wntr.sim.EpanetSimulator(waterNetwork)
    results = sim.run_sim()

    pressure = results.node['pressure']

    avg_pressures = {}

    for junction in waterNetwork.junction_name_list:
        avg_pressures[junction] = pressure[junction].mean()
    
    sorted_pressures = sorted(avg_pressures.items(), key=lambda x: x[1], reverse=True)

    sorted_junction_names = [junction for junction, avg_pressure in sorted_pressures]
    

    print("Junctions sorted by average pressure:")
    for junction in sorted_junction_names:
        print(f"Junction {junction}")
    


    return sorted_junction_names