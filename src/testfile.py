from utils import load_network
import os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
inp_path = os.path.join(base_dir, 'data', 'Net2.inp')
if __name__ == "__main__":
    # Load the network model
    wn =load_network(inp_path)
