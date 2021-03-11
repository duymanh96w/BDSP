from src.data_loader import load_data
from src.model import Network
from tqdm import tqdm


if __name__=='__main__':
    num_works, num_shifts, min_num_shifts, shifts = load_data(filename='r1')
    n = Network(num_works, num_shifts, shifts)
    for cl in n.clusters:
        cl.random_turn_on_node()
    
    while True:
        for cl in n.clusters:
            cl.repair()
        n.write_history()
        print(n.status_history[-1])
        if len(n.status_history) >= 2 and n.status_history[-1] == n.status_history[-2]:
            n.learn()
        
        if len(n.status_history) == 100:
            break

    for cl in n.clusters:
        node_id = cl.turned_on_node
        print(cl.nodes[node_id].get_input())