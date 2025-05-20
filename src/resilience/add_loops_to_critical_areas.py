import wntr
def add_loops_to_critical_areas(waterNetwork, critical_junctions, loop_count=3, pipe_cost_per_meter=100, fixed_installation_cost=500):

    total_cost = 0
    pipes_to_loop = []
    
    for pipe_name in waterNetwork.pipe_name_list:
        pipe = waterNetwork.get_link(pipe_name)
        start_node = waterNetwork.get_node(pipe.start_node_name)
        end_node = waterNetwork.get_node(pipe.end_node_name)
        
        if isinstance(start_node, wntr.network.Junction) and isinstance(end_node, wntr.network.Junction):
            if start_node.name in critical_junctions.index or end_node.name in critical_junctions.index:
                pipes_to_loop.append(pipe_name)
                
    new_pipes_added = 0
    for pipe_name in pipes_to_loop:
        if new_pipes_added >= loop_count:
            break
        
        pipe = waterNetwork.get_link(pipe_name)
        start_node = waterNetwork.get_node(pipe.start_node_name)
        end_node = waterNetwork.get_node(pipe.end_node_name)
        
        for neighbor_pipe_name in waterNetwork.pipe_name_list:
            if neighbor_pipe_name == pipe_name:
                continue
            neighbor_pipe = waterNetwork.get_link(neighbor_pipe_name)
            neighbor_start_node = waterNetwork.get_node(neighbor_pipe.start_node_name)
            neighbor_end_node = waterNetwork.get_node(neighbor_pipe.end_node_name)
        
            if isinstance(neighbor_start_node, wntr.network.Junction):
                if start_node.name != neighbor_start_node.name and end_node.name != neighbor_start_node.name:
                    new_pipe_name = f'new_pipe_{start_node.name}_{neighbor_start_node.name}'
                    print(f"Adding pipe {new_pipe_name} to create a loop.")
            
                    length = 300 
                    diameter = 0.3  
                    waterNetwork.add_pipe(new_pipe_name, start_node.name, neighbor_start_node.name, length=length, diameter=diameter)
                    new_pipes_added += 1
            
                    pipe_cost = length * pipe_cost_per_meter + fixed_installation_cost
                    total_cost += pipe_cost
                    print(f"Added {new_pipe_name} with a cost of ${pipe_cost:.2f}.")
                    break

    print(f"Total cost of adding loops: ${total_cost:.2f}")
    return waterNetwork, total_cost