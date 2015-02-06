import networkx as nx



class Path:

    def __init__(self, graph, source, target, path_type, weight):
        self.graph = graph
        if(weight == 'weighted'):
            self.weight = True
        else:
            self.weight = False
        if(self.graph.uploaded):
            self.source = source
            self.target = target
        else:
            self.source = int(source)
            self.target = int(target)
        self.path_length = None
        self.path_type = path_type
        self.path_sequence = self.calculate_path()
        
        
    def find_all_simple_paths(self, graph, source, target):
        paths = nx.all_simple_paths(graph, str(source), str(target))
        p = []
        for path in paths:
            p.append(path)
        return p


    def find_critical_path(self, graph, source, target):
        paths = self.find_all_simple_paths(graph.graph, source, target)
        if not paths:
            return None
        max_value = float("-inf")
        pos = []
        i = 0
        p = []
        path_length = []
        for path in paths:
            length = 0
            p.append(path)
            for counter in range(0, len(path) - 1):
                if(counter != len(path) - 1):
                    length = length + int(graph
                                .graph.edge[path[counter]][path[counter + 1]]['weight'])
            if(length >  max_value):
                max_value = length 
            path_length.append(length)
        for path in p:
            if(path_length[i] == max_value):
                pos.append(i)
            i = i + 1
        all_critical_paths = []
        for i in pos:
            all_critical_paths.append(p[i])
        return all_critical_paths
    
    
    def find_critical_path_based_on_path_length(self, graph, source, target):
        paths = self.find_all_simple_paths(graph.graph, source, target)
        if not paths:
            return None
        max_value = float("-inf")
        p = []
        pos = []
        i = 0
        for path in paths:
            p.append(path)
            if(len(path) - 1 > max_value):
                max_value = len(path) - 1
        for path in p:
            if(len(path) - 1 == max_value):
                pos.append(i)
            i = i + 1
        all_critical_paths = []
        for i in pos:
            all_critical_paths.append(p[i])
        return all_critical_paths
    
    """
    Calculate all pairs of strongest paths using Floyd Warshall algorithm
    """
    def calculate_strongest_paths_Floyd_Warshall(self):
        s = {}
        pred = {}
        for u in self.graph.graph.nodes():
            for v in self.graph.graph.nodes():
                
                    if(self.graph.graph.has_edge(u, v)):
                        
                        s[(u, v)] = float(self.graph.graph.edge[u][v]['weight'])
                        pred[(u, v)] = u
                    else:
                        s[(u, v)] = float('-inf')
                        pred[(u , v)] = None
        for node1 in self.graph.graph.nodes():
            for node2 in self.graph.graph.nodes():
                if(node1 != node2):
                    for node3 in self.graph.graph.nodes():
                        if(node3 != node2):
                                if(s[(node2, node3)] < min(s[(node2, node1)], s[(node1, node3)])):
                                    s[(node2, node3)] = min(s[(node2, node1)], s[(node1, node3)])
                                    pred[(node2, node3)] = pred[(node1, node3)]                         
        return pred, s
    
    
    """
    Define nodes included in the strongest path between a source
    node and a target node
    """
    def find_strongest_path(self):  
        pred = self.calculate_strongest_paths_Floyd_Warshall()
        predecessors = {}
        for node in self.graph.graph.nodes():
            predecessors[node] = pred[0][(self.source, node)]
        sequence = [self.target]
        path_sequence = self.create_path_sequence(predecessors, self.target, 
                                                  sequence)
        if(len(path_sequence[0]) == 1):
            return None
        else:
            self.path_length = pred[1][(self.source, self.target)]
            return path_sequence
              
    """
    Define nodes included in the strongest path between a source
    node and a target node
    """              
    def find_shortest_paths(self):
    
        if(not self.weight):
            weight = None
        else:
            weight = 'weight'
        if(self.graph.has_negative_weights and self.graph.is_weighted):
            if(self.graph.negative_cycle):
                return 'negative cycle'
            else:
                pred =  nx.bellman_ford(self.graph.graph, self.source, 
                                        weight = 'weight')
                sequen = [self.target]
                path_sequence = self.create_path_sequence(pred[0], self.target, 
                                                          sequen)
                self.path_length = pred[1][self.target]
                return path_sequence
        else:
            paths = nx.all_shortest_paths(self.graph.graph, self.source, self.target, 
                                          weight = weight)
            try:
                p = []
                for path in paths:
                    p.append(path)
            except nx.NetworkXNoPath:
                return None
            else:
                self.path_length = nx.shortest_path_length(self.graph.graph, 
                                                self.source, self.target, 
                                                weight = weight)
                return p
    """
    Use Bellman-Ford algorithm to find shortest paths in graphs
    with negative weights.
    """    
    def Bellman_Ford_algorithm(self, graph, source):
        dist = {}
        pred = {}
        for node in graph.nodes():
            pred[node] = None
            if(node != source):
                dist[node] = float('inf')
            else:
                dist[node] = 0
        
        for node in graph.nodes():
            for u, v in graph.edges():
                if(dist[v] > dist[u] + graph.edge[u][v]['weight']):
                    dist[v] = dist[u] + graph.edge[u][v]['weight']
                    pred[v] = u
        pred[source] = None
        return pred
    
    """
    Calculate the sequence of visited nodes in a path
    """
    def create_path_sequence(self, pred, target, sequence):
        while(pred[target] != None):
            sequence.append(pred[target])
            return self.create_path_sequence(pred, pred[target], sequence)
        sequence.reverse()
        path_sequence = [sequence]
        return path_sequence
    
    
    def calculate_path_vertices(self, path):
        path_vertices = []
        for s in range(0, len(path) - 1):
            if s != len(path) - 1:
                vertice = (path[s], path[s+1])
                path_vertices.append(vertice)
        return path_vertices
    
    
    def calculate_path(self):
        if(self.path_type == "shortest"):
            return self.find_shortest_paths()
        elif(self.path_type == "strongest"):
            return self.find_strongest_path()
        
        
    def get_nodes_which_are_not_in_path(self, graph, paths):
        rest_nodes = []
        for node in graph.nodes():
            is_in_path = False
            for path in paths:
                if node in path:
                    is_in_path = True
            if(not is_in_path):
                rest_nodes.append(node)
        return rest_nodes
    
    
    def get_edges_which_are_not_in_paths(self, graph, path_vertices):
        rest_edges = []
        for edge in graph.edges():
            is_in_path = False
            for p_edge in path_vertices:
                if edge in p_edge:
                    is_in_path = True
            if(not is_in_path):
                rest_edges.append(edge)
        return rest_edges 
