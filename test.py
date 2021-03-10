class Node:
    def __init__(self, _id, value):
        self._id = _id
        self.value = value
        self.connected_nodes = []

    def __str__(self) -> str:
        return '%s: %s' % (str(self._id), str(self.value))

    def make_connection(self, others: list):
        for other_node in others:
            if self.value == other_node.value:
                self.connected_nodes.append(other_node)


class Cluster:
    def __init__(self, _id):
        self._id = _id
        self.nodes = []


class Node:
    def __init__(self, _id, shift_id):
        self._id = _id
        self.shift_id = shift_id

    def __str__(self) -> str:
        return '%d %d' % (self._id, self.shift_id) 


class Network:
    def __init__(self, num_works, num_shifts, shifts):
        self.shifts = shifts
        self.clusters = []
        self.weight = None
        self.num_works = num_works
        self.num_nodes = 0

    
    def make_clusters(self):
        for i in range(self.num_works):
            cluster = Cluster(_id=i)
            self.clusters.append(cluster)

        for i in range(len(self.shifts)):
            for work in self.shifts[i]:
                node = Node(_id=self.num_nodes, shift_id=i)
                self.clusters[work].nodes.append(node)
                self.num_nodes += 1

