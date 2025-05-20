import wntr

def add_tanks_with_correct_placement(waterNetwork, critical_junctions, max_tanks=2, tank_cost=20000):    
    tanks_added = 0
    total_cost = 0
    elevation_dict = {} 
    non_critical_elevations = {}

    for junction_name in waterNetwork.junction_name_list:
        node = waterNetwork.get_node(junction_name)
        elevation = node.elevation
        if junction_name in critical_junctions.index:
            elevation_dict[junction_name] = elevation
        else:
            non_critical_elevations[junction_name] = elevation

    sorted_critical_junctions = sorted(elevation_dict.items(), key=lambda x: x[1], reverse=True)


    for junction_name, elevation in sorted_critical_junctions:
        if tanks_added >= max_tanks:
            break

        tank_name = f'tank_{junction_name}'
        node = waterNetwork.get_node(junction_name)
        original_coords = node.coordinates
        
        waterNetwork.add_tank(
            name=tank_name,
            elevation=elevation,
            init_level=5.0,
            min_level=2.0,
            max_level=8.0,
            diameter=20.0
        )
        waterNetwork.get_node(tank_name).coordinates = original_coords
        
        print(f"Added tank '{tank_name}' at critical junction '{junction_name}' with elevation {elevation}")
        tanks_added += 1
        total_cost += tank_cost

    if tanks_added < max_tanks:

        sorted_non_critical_junctions = sorted(non_critical_elevations.items(), key=lambda x: x[1], reverse=True)
        
        for junction_name, elevation in sorted_non_critical_junctions:
            if tanks_added >= max_tanks:
                break

            tank_name = f'tank_{junction_name}'
            node = waterNetwork.get_node(junction_name)
            original_coords = node.coordinates
            
            waterNetwork.add_tank(
                name=tank_name,
                elevation=elevation,
                init_level=5.0,
                min_level=2.0,
                max_level=8.0,
                diameter=20.0
            )
            waterNetwork.get_node(tank_name).coordinates = original_coords
            
            print(f"Added tank '{tank_name}' at non-critical junction '{junction_name}' with elevation {elevation}")
            tanks_added += 1
            total_cost += tank_cost

    print(f"Total cost for adding {tanks_added} tanks: ${total_cost:.2f}")
    return waterNetwork, total_cost