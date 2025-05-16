import wntr

def load_network(inp_file):
    return wntr.network.WaterNetworkModel(inp_file)

def describe_network(wn):
    return wn.describe()
