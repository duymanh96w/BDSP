from src.data_loader import load_data
from src.model import Network


if __name__=='__main__':
    num_works, num_shifts, min_num_shifts, shifts = load_data(filename='t1')
    n = Network(num_works, num_shifts, shifts)
    for cl in n.clusters:
        cl.random_turn_on_node()
    
    for node in n.nodes:
        print(node, node.get_input())

    