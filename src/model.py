import random
from tqdm import tqdm


class Shift:
    def __init__(self, _id, piece_of_works: list) -> None:
        self._id = _id
        self.piece_of_works = piece_of_works

    
    def __str__(self) -> str:
        return str(self._id) + ': ' + str(self.piece_of_works)


class Node:
    def __init__(self, _id, cluster_id, shift, weight=None):
        self._id = _id
        self.cluster_id = cluster_id
        self.shift = shift
        # 0 -> off, 1 -> on
        self.status = 0
        self.connected_nodes = []
        self.weight = weight

    
    def turn_on(self):
        self.status = 1
    

    def turn_off(self):
        self.status = 0

    
    def make_connections(self, others: list):
        for other_node in others:
            if self.shift == other_node.shift:
                continue
            else:
                # if self.cluster_id in other_node.shift.piece_of_works or other_node.cluster_id in self.shift.piece_of_works:
                #     self.connected_nodes.append(other_node)
                #     other_node.connected_nodes.append(self)
                if len(set(self.shift.piece_of_works).union(set(other_node.shift.piece_of_works))) != 0:
                    self.connected_nodes.append(other_node)
                    other_node.connected_nodes.append(self)

    
    def get_input(self):
        input = 0
        for other in self.connected_nodes:
            _id1 = self._id
            _id2 = other._id
            smaller_id = _id1 if _id1 <= _id2 else _id2
            bigger_id = _id1 if _id1 > _id2 else _id2
            input += self.weight['%d.%d' % (smaller_id, bigger_id)] * other.status

        return input


    def __str__(self) -> str:
        return 'Node_id: %d, shift_id: %d' % (self._id, self.shift._id) 


class Cluster:
    def __init__(self, _id):
        self._id = _id
        self.nodes = []
        self.turned_on_node = None


    def make_connections(self, other_cluster):
        for node in self.nodes:
            node.make_connections(other_cluster.nodes)


    def random_turn_on_node(self):
        num = random.randint(0, len(self.nodes)-1)
        for i in range(len(self.nodes)):
            if i == num:
                self.nodes[i].status = 1
            else:
                self.nodes[i].status = 0

        self.turned_on_node = num


    def repair(self):
        old_max_id = self.turned_on_node
        cur_max_id = 0
        max_ids = []
        if cur_max_id is None:
            return

        cur_max_input = -float('inf')
        for i in range(len(self.nodes)):
            self.nodes[i].turn_off()
            input = self.nodes[i].get_input()
            if input > cur_max_input:
                cur_max_id = i
                cur_max_input = input
                max_ids = []
                max_ids.append(i)
            elif input == cur_max_input:
                max_ids.append(i)
        
        if old_max_id in max_ids:
            max_id = old_max_id
        else:
            max_id = random.choice(max_ids)
        
        self.nodes[max_id].turn_on()
        self.turned_on_node = max_id

    
    def __str__(self) -> str:
        return 'Cluster %d' % self._id


class Network:
    def __init__(self, num_works, num_shifts, shifts):
        self.clusters = []
        self.weight = dict()
        self.num_works = num_works
        self.nodes = []
        self.num_nodes = 0
        self.shifts = []
        self.status_history = []

        for i in range(len(shifts)):
            shift = Shift(i, shifts[i])
            self.shifts.append(shift)
        
        self.make_clusters()
        self.make_connections()

    
    def make_clusters(self):
        for i in range(self.num_works):
            cluster = Cluster(_id=i)
            self.clusters.append(cluster)

        for i in range(len(self.shifts)):
            for work in self.shifts[i].piece_of_works:
                node = Node(_id=self.num_nodes, cluster_id=work, shift=self.shifts[i], weight=self.weight)
                self.clusters[work].nodes.append(node)
                self.num_nodes += 1
                self.nodes.append(node)

    
    def get_status(self):
        s = 0
        for cl in self.clusters:
            cl_node_id = cl.turned_on_node
            node_id = cl.nodes[cl_node_id]._id
            s += self.nodes[node_id].get_input()

        return s

    
    def make_connections(self):
        # for i in range(len(self.clusters) - 1):
        #     self.clusters[i].make_connections(self.clusters[i+1])


        for i in tqdm(range(len(self.nodes) - 1)):
            for j in range(i+1, len(self.nodes)):
                if self.nodes[i].shift == self.nodes[j].shift:
                    continue
                else:
                    if len(set(self.nodes[i].shift.piece_of_works).intersection(set(self.nodes[j].shift.piece_of_works))) != 0:
                        self.nodes[i].connected_nodes.append(self.nodes[j])
                        self.nodes[j].connected_nodes.append(self.nodes[i])
                        self.weight['%d.%d' % (i, j)] = -1
        

        # for node in self.nodes:
        #     for connected_node in node.connected_nodes:
        #         _id1 = node._id
        #         _id2 = connected_node._id
        #         smaller_id = _id1 if _id1 <= _id2 else _id2
        #         bigger_id = _id1 if _id1 > _id2 else _id2
        #         if '%d.%d' % (smaller_id, bigger_id) not in self.weight:
        #             self.weight['%d.%d' % (smaller_id, bigger_id)] = -1

    
    def write_history(self):
        stt = []
        for cl in self.clusters:
            stt.append(str(cl.nodes[cl.turned_on_node].shift._id))
        
        self.status_history.append('.'.join(stt))

    
    def learn(self):
        # for pair in self.weight:
        #     _id1 = int(pair.split('.')[0])
        #     _id2 = int(pair.split('.')[1])
        #     self.weight[pair] -= self.nodes[_id1].status * self.nodes[_id2].status
        nodes_id = [cl.nodes[cl.turned_on_node]._id for cl in self.clusters]
        for i in range(len(nodes_id) - 1):
            _id1 = nodes_id[i]
            for j in range(i+1, len(nodes_id)):
                _id2 = nodes_id[j]
                if '%d.%d' % (_id1, _id2) in self.weight:
                    self.weight['%d.%d' % (_id1, _id2)]  -= 1
                
                if '%d.%d' % (_id2, _id1) in self.weight:
                    self.weight['%d.%d' % (_id2, _id1)]  -= 1

