import json
import os
from loader import load_network 

def save_network_summary(wn_file, output_path="network_summary.json"):
    """
    Saves a summary of the water network to a JSON file in the project root.
    """
    wn = load_network(wn_file)
    
    summary = {
        "Junctions": len(wn.junction_name_list),
        "Pipes": len(wn.pipe_name_list),
        "Tanks": len(wn.tank_name_list),
        "Pumps": len(wn.pump_name_list),
        "Tanks_Details": {},
        "Pumps_Details": {}
    }

    for tank_name in wn.tank_name_list:
        tank = wn.get_node(tank_name)
        summary["Tanks_Details"][tank_name] = {
            "elevation": tank.elevation,
            "init_level": tank.init_level,
            "max_level": tank.max_level
        }

    for pump_name in wn.pump_name_list:
        pump = wn.get_link(pump_name)
        summary["Pumps_Details"][pump_name] = {
            "power": str(pump)  # or use `pump.power` if available
        }

    # Save to JSON in the main folder
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=4)
    
    print(f"Network summary saved to {output_path}")
