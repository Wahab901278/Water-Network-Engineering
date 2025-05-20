import wntr
def load_network(inp_file):
    """ Load a network model from an EPANET .inp file """
    wn = wntr.network.WaterNetworkModel(inp_file)
    return wn

def save_network_to_inp_file(waterNetwork, file_name):
    wntr.network.io.write_inpfile(waterNetwork, file_name)
    print(f"Network saved to {file_name}")