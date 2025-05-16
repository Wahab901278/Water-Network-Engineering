import wntr
def load_network(inp_file):
    """ Load a network model from an EPANET .inp file """
    wn = wntr.network.WaterNetworkModel(inp_file)
    return wn