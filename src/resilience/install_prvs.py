def install_prvs(waterNetwork, high_pressure_junctions, requiredPressure):

    total_cost = 0
    automated_valve_cost = 5000 


    reservoir_names = waterNetwork.reservoir_name_list
    
    for junction_name in high_pressure_junctions:
        valve_name = f'PRV_{junction_name}'

        node = waterNetwork.get_node(junction_name)
        connected_links = waterNetwork.get_links_for_node(junction_name)
    
        skip = False
        for pipe_name in connected_links:
            pipe = waterNetwork.get_link(pipe_name)
            if pipe.start_node_name in reservoir_names or pipe.end_node_name in reservoir_names:
                print(f"Skipping PRV at junction {junction_name} due to connection with reservoir")
                skip = True
                break
        
        if skip:
            continue
        
        pipe_name = connected_links[0]
        pipe = waterNetwork.get_link(pipe_name)
        
        waterNetwork.add_valve(
            name=valve_name, 
            start_node_name=pipe.start_node_name, 
            end_node_name=pipe.end_node_name, 
            valve_type='PRV', 
            diameter=0.5
        )

        waterNetwork.get_link(valve_name).initial_setting = requiredPressure
        
        total_cost += automated_valve_cost

    print(f"Total cost of PRV installation: ${total_cost:.2f}")
    return waterNetwork, total_cost