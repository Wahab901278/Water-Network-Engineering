def install_prvs(waterNetwork, high_pressure_junctions, requiredPressure):
    total_cost = 0
    automated_valve_cost = 5000 

    tank_names = set(waterNetwork.tank_name_list)
    reservoir_names = set(waterNetwork.reservoir_name_list)

    for junction_name in high_pressure_junctions:
        valve_name = f'PRV_{junction_name}'

        try:
            connected_links = waterNetwork.get_links_for_node(junction_name)

            # Find a valid pipe not connected to tank/reservoir
            selected_pipe = None
            for pipe_name in connected_links:
                pipe = waterNetwork.get_link(pipe_name)
                start = pipe.start_node_name
                end = pipe.end_node_name

                # If this pipe connects to a tank or reservoir, skip
                if start in tank_names or end in tank_names:
                    print(f"Skipping PRV at {junction_name} due to tank connection.")
                    continue
                if start in reservoir_names or end in reservoir_names:
                    print(f"Skipping PRV at {junction_name} due to reservoir connection.")
                    continue

                selected_pipe = pipe
                break

            if selected_pipe is None:
                print(f"No valid pipe for PRV installation at junction {junction_name}")
                continue

            # Add valve on selected pipe
            waterNetwork.add_valve(
                name=valve_name,
                start_node_name=selected_pipe.start_node_name,
                end_node_name=selected_pipe.end_node_name,
                valve_type='PRV',
                diameter=0.5
            )
            waterNetwork.get_link(valve_name).initial_setting = requiredPressure
            total_cost += automated_valve_cost

        except Exception as e:
            print(f"Skipped PRV at {junction_name} due to error: {e}")
            continue

    print(f"Total cost of PRV installation: ${total_cost:.2f}")
    return waterNetwork, total_cost
