from src.data_loader import load_data
from src.model2 import Network
from tqdm import tqdm
import random


def random_combination(iterable, r):
    "Random selection from itertools.combinations(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.sample(range(n), r))
    return tuple(pool[i] for i in indices)

if __name__=='__main__':
    num_works, num_shifts, min_num_shifts, shifts = load_data(filename='r1')
    n = Network(num_works, num_shifts, shifts)

    n.create_init_solution(use_heuristic=True)
    
    it = 0
    clusters_id = [i for i in range(len(n.clusters))]
    while True:
    # for i in range(1):
        # random_order = random_combination(clusters_id, len(clusters_id))
        # for i in random_order:
        #     n.repair(updated_cluster_id=i)
        #     n.clusters[i].repair()

        for i in range(len(n.clusters)):
            # n.repair(updated_cluster_id=i)
            n.clusters[i].repair()
            # n.repair(updated_cluster_id=i)
        n.repair()

        n.write_history()
        print(it, ': ', n.status_history[-1])
        if len(n.status_history) >= 2 and n.status_history[-1] == n.status_history[-2]:
            n.learn()
        
        if n.get_status() == 0:
            break

        it += 1

    for cl in n.clusters:
        node_id = cl.turned_on_node
        print(cl.nodes[node_id].get_input())

    for cl in n.clusters:
        node_id = cl.turned_on_node
        print(cl._id, cl.nodes[node_id]._id)
        print(cl.nodes[node_id].shift)
    
    
    # for no in n.nodes:
    #     print(no.get_input())