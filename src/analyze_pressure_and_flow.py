import wntr
from loader import load_network

def analyze_pressure_and_flow(wn_file, required_pressure):
    
    waterNetwork=load_network(wn_file)
    try:

        sim = wntr.sim.EpanetSimulator(waterNetwork)
        results = sim.run_sim()
    except wntr.epanet.toolkit.EpanetException as e:
        print(f"Error during simulation: {e}")
        return None, None
        
    pressure = results.node['pressure'].loc[:, waterNetwork.junction_name_list]
    low_pressure_junctions = pressure.mean(axis=0)[pressure.mean(axis=0) < required_pressure]
    
    flow = results.link['flowrate'].loc[:, waterNetwork.pipe_name_list]
    low_flow_pipes = flow.mean(axis=0)[flow.mean(axis=0) < 0.1] 
    
    return low_pressure_junctions, low_flow_pipes