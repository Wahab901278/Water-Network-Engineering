import wntr
from src.loader import load_network

def add_adaptive_pumps(wn, low_pressure_junctions, max_pumps=6, pump_cost=10000, junction_cost=2000, min_pressure=20, max_pressure=50):
    pumps_added = 0
    total_cost = 0

    if 'pump_curve' not in wn.curve_name_list:
        pump_curve = [
            (0, 50),   # At zero flow, the pump provides 50 meters of head
            (50, 40),  # At 50 m³/h, the pump provides 40 meters of head
            (100, 25), # At 100 m³/h, the pump provides 25 meters of head
            (150, 10)  # At 150 m³/h, the pump provides 10 meters of head
        ]
        wn.add_curve('pump_curve', 'HEAD', pump_curve)

    # Run hydraulic simulation to get the head and pressure values
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()

    sorted_junctions = low_pressure_junctions.sort_values()
    for junction_name in sorted_junctions.index:
        if pumps_added >= max_pumps:
            break

        pump_name = f'pump_{junction_name}'
        new_junction_name = f'new_junction_{junction_name}'

        node = wn.get_node(junction_name)
        original_coords = node.coordinates

        neighbor_coords = None
        for pipe_name in wn.pipe_name_list:
            pipe = wn.get_link(pipe_name)
            if pipe.start_node_name == junction_name:
                neighbor_name = pipe.end_node_name
            elif pipe.end_node_name == junction_name:
                neighbor_name = pipe.start_node_name
            else:
                continue

            neighbor_coords = wn.get_node(neighbor_name).coordinates
            break

        if neighbor_coords:
            new_junction_coords = (
                (original_coords[0] + neighbor_coords[0]) / 2,
                (original_coords[1] + neighbor_coords[1]) / 2
            )
        else:
            new_junction_coords = (original_coords[0] + 1, original_coords[1] + 1)

        wn.add_junction(new_junction_name, elevation=node.elevation)
        wn.get_node(new_junction_name).coordinates = new_junction_coords

        wn.add_pump(
            name=pump_name,
            start_node_name=new_junction_name,
            end_node_name=junction_name,
            pump_type='HEAD',
            pump_parameter='pump_curve'
        )

        node_head = results.node['head'].loc[:, junction_name].mean()
        initial_pressure = node_head - node.elevation

        if initial_pressure < min_pressure:
            wn.get_link(pump_name).initial_status = 'OPEN'
        elif initial_pressure > max_pressure:
            wn.get_link(pump_name).initial_status = 'CLOSED'

        print(f"Pump '{pump_name}' status: {wn.get_link(pump_name).initial_status} based on initial pressure: {initial_pressure}")

        total_cost += pump_cost + junction_cost
        pumps_added += 1

    print(f"Total cost for adding {pumps_added} pumps: ${total_cost:.2f}")
    return wn, total_cost