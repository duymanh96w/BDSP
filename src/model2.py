import random
from tqdm import tqdm


class Shift:
    def __init__(self, _id, pieces_of_work: list) -> None:
        self._id = _id
        self.pieces_of_work = pieces_of_work

    
    def __str__(self) -> str:
        return str(self._id) + ': ' + str(self.pieces_of_work)


class Node:
    def __init__(self, _id, cluster_id, shift, weight=None):
        self._id = _id
        self.cluster_id = cluster_id
        self.shift = shift
        # status: 0 -> off, 1 -> on
        self.status = 0
        self.weight = weight
        self.input = 0

    
    def turn_on(self):
        self.status = 1
    

    def turn_off(self):
        self.status = 0

    
    def get_input(self):
        return self.input

    
    def is_conflict(self, other):
        cluster_id1 = self.cluster_id
        cluster_id2 = other.cluster_id
        
        # if cluster_id1 in self.shift.pieces_of_work                                                                     \
        #     and cluster_id2 in self.shift.pieces_of_work                                                                \
        #     and (cluster_id1 not in other.shift.pieces_of_work or cluster_id2 not in other.shift.pieces_of_work):
        #     return True

        # if cluster_id1 in other.shift.pieces_of_work                                                                     \
        #     and cluster_id2 in other.shift.pieces_of_work                                                                \
        #     and (cluster_id1 not in self.shift.pieces_of_work or cluster_id2 not in self.shift.pieces_of_work):
        #     return True

        if self.shift == other.shift:
            return False 
        else:
            le = len(list(set(self.shift.pieces_of_work).intersection(other.shift.pieces_of_work)))
            return le != 0 and le != len(self.shift.pieces_of_work)

        if cluster_id2 in self.shift.pieces_of_work and cluster_id1 not in other.shift.pieces_of_work:
            return True

        if cluster_id2 not in self.shift.pieces_of_work and cluster_id1 in other.shift.pieces_of_work:
            return True

        if cluster_id1 in self.shift.pieces_of_work and cluster_id2 in self.shift.pieces_of_work            \
            and cluster_id1 in other.shift.pieces_of_work and cluster_id2 in other.shift.pieces_of_work     \
            and self.shift._id != other.shift._id:
            return True

        return False

    def __str__(self) -> str:
        return 'Node_id: %d, shift_id: %d' % (self._id, self.shift._id) 


class Cluster:
    def __init__(self, _id, weight):
        self._id = _id
        self.nodes = []
        self.turned_on_node = None
        self.conflict_clusters = []
        self.weight = weight
        self.constraint_nodes = []


    def random_turn_on_node(self):
        num = random.randint(0, len(self.nodes)-1)
        for i in range(len(self.nodes)):
            if i == num:
                self.nodes[i].status = 1
            else:
                self.nodes[i].status = 0

        self.turned_on_node = num


    def is_conflict(self, other):
        res = False
        if len(self.nodes) == 1 and len(other.nodes) == 1:
            return False
        else:
            # for node in self.nodes:
            #     if other._id in node.shift.pieces_of_work:
            #         return True
            
            # for node in other.nodes:
            #     if self._id in node.shift.pieces_of_work:
            #         return True
            for node in self.nodes:
                for other_node in other.nodes:
                    if node.is_conflict(other_node):
                        return True
        
        return res

    
    def update_nodes_input(self, other_node, constraint_node):
        for node in self.nodes:
            if node.is_conflict(other_node):
                node.input += self.weight[constraint_node]
            # else:
            #     node.input = 0


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

        # # change others input 
        # for cn in self.constraint_nodes:
        #     _id1 = self._id
        #     _id2 = cn
        #     if _id1 >= _id2:
        #         _id1, _id2 = _id2, _id1          

    
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
        self.is_over_cover = {}

        for i in range(len(shifts)):
            shift = Shift(i, shifts[i])
            self.shifts.append(shift)
        
        self.make_clusters()
        # self.make_conflicts()
        self.make_connections()        

    
    def make_clusters(self):
        for i in range(self.num_works):
            cluster = Cluster(_id=i, weight=self.weight)
            self.clusters.append(cluster)

        for i in range(len(self.shifts)):
            for work in self.shifts[i].pieces_of_work:
                node = Node(_id=self.num_nodes, cluster_id=work, shift=self.shifts[i], weight=self.weight)
                self.clusters[work].nodes.append(node)
                self.num_nodes += 1
                self.nodes.append(node)

    
    def get_status(self):
        s = 0
        for constraint_node in self.weight:
            _id1 = int(constraint_node.split('.')[0])
            _id2 = int(constraint_node.split('.')[1])

            cl_turned_on_node1 = self.clusters[_id1].turned_on_node
            cl_turned_on_node2 = self.clusters[_id2].turned_on_node
            node1 = self.clusters[_id1].nodes[cl_turned_on_node1]
            node2 = self.clusters[_id2].nodes[cl_turned_on_node2]
            if node1.is_conflict(node2):
                s += 1

        return s

    
    def get_status_list(self):
        conflict_list = []

        for constraint_node in self.weight:
            _id1 = int(constraint_node.split('.')[0])
            _id2 = int(constraint_node.split('.')[1])

            cl_turned_on_node1 = self.clusters[_id1].turned_on_node
            cl_turned_on_node2 = self.clusters[_id2].turned_on_node
            node1 = self.clusters[_id1].nodes[cl_turned_on_node1]
            node2 = self.clusters[_id2].nodes[cl_turned_on_node2]
            if node1.is_conflict(node2):
                conflict_list.append(constraint_node)

        return conflict_list

    
    def make_connections(self):
        for i in tqdm(range(len(self.clusters) - 1)):
            for j in range(i+1, len(self.clusters)):
                if self.clusters[i].is_conflict(self.clusters[j]):
                    self.weight['%d.%d' % (i, j)] = -1

                    self.clusters[i].conflict_clusters.append(int(j))
                    self.clusters[i].constraint_nodes.append('%d.%d' % (i, j))
                    
                    self.clusters[j].conflict_clusters.append(int(i))
                    self.clusters[j].constraint_nodes.append('%d.%d' % (i, j))                

    
    # def make_conflicts(self):
    #     for i in range(len(self.shifts) - 1):
    #         for j in range(i + 1, len(self.shifts)):
    #             if self.nodes[i].is_conflict(self.nodes[j]):
    #                 _id1 = self.shifts[i]._id
    #                 _id2 = self.shifts[j]._id
    #                 if _id1 >= _id2:
    #                     _id1, _id2 = _id2, _id1
    #                 self.is_over_cover['%d.%d' % (_id1, _id2)] = True

    
    def write_history(self):
        stt = []
        for cl in self.clusters:
            stt.append(str(cl.nodes[cl.turned_on_node].shift._id))
        
        self.status_history.append('.'.join(stt))

    
    # def repair(self, updated_cluster_id):
    #     cl_turned_on_node_id = self.clusters[updated_cluster_id].turned_on_node
    #     node = self.clusters[updated_cluster_id].nodes[cl_turned_on_node_id]
    #     related_clusters_id = self.clusters[updated_cluster_id].conflict_clusters
    #     for _id in related_clusters_id:
    #         _id1 = int(updated_cluster_id)
    #         _id2 = int(_id)
    #         if _id1 >= _id2:
    #             _id1, _id2 = _id2, _id1

    #         self.clusters[_id].update_nodes_input(node, '%d.%d' % (_id1, _id2))

            # cl_other_nod1ated_cluster_id].update_nodes_input(other_node, '%d.%d' % (_id1, _id2))

    
    def repair(self):
        for updated_cluster_id in range(len(self.clusters)):
            cl_turned_on_node_id = self.clusters[updated_cluster_id].turned_on_node
            node = self.clusters[updated_cluster_id].nodes[cl_turned_on_node_id]
            related_clusters_id = self.clusters[updated_cluster_id].conflict_clusters
            for _id in related_clusters_id:
                _id1 = int(updated_cluster_id)
                _id2 = int(_id)
                if _id1 >= _id2:
                    _id1, _id2 = _id2, _id1

                self.clusters[_id].update_nodes_input(node, '%d.%d' % (_id1, _id2))

    
    def learn(self):
        for constraint_node in self.weight:
            _id1 = int(constraint_node.split('.')[0])
            _id2 = int(constraint_node.split('.')[1])
            cl_turned_on_node1 = self.clusters[_id1].turned_on_node
            cl_turned_on_node2 = self.clusters[_id2].turned_on_node

            node1 = self.clusters[_id1].nodes[cl_turned_on_node1]
            node2 = self.clusters[_id2].nodes[cl_turned_on_node2]
            if node1.is_conflict(node2):
                self.weight[constraint_node] -= 1
                # node1.input -= 1
                # node2.input -= 1

            # self.clusters[_id1].update_nodes_input(node2, constraint_node)
            # self.clusters[_id2].update_nodes_input(node1, constraint_node)


    def create_init_solution(self, use_heuristic=False):
        if not use_heuristic:
            for cl in self.clusters:
                cl.random_turn_on_node()

        else:
            available_shifts = {w: [] for w in range(self.num_works)}
            assigned = [i for i in range(self.num_works)]
            while len(assigned) != 0:
                w = assigned[0]

                shift_id = -1
                max_common = 0
                for node in self.clusters[w].nodes:
                    le = len(list(set(assigned).intersection(set(node.shift.pieces_of_work))))
                    if le > max_common:
                        shift_id = node.shift._id
                        max_common = le

                for pow in self.shifts[shift_id].pieces_of_work:
                    try:
                        assigned.remove(pow)
                        available_shifts[pow].append(shift_id)
                    except:
                        continue
            
            for w in available_shifts:
                shift_id = random.choice(available_shifts[w])
                for cl_node_id in range(len(self.clusters[w].nodes)):
                    if self.clusters[w].nodes[cl_node_id].shift._id == shift_id:
                        self.clusters[w].nodes[cl_node_id].status = 1
                        self.clusters[w].turned_on_node = cl_node_id
