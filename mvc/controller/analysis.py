import networkx as nx
import matplotlib
matplotlib.use('AGG')
import pylab as plt
import StringIO
import operator

class Communities:

    def __init__(self, graph):
        g = nx.Graph(graph)
        self.get_cliques(g)
        self.communities = self.Girvan_Newman_algorithm(g)

    def get_cliques(self, graph):
        self.cliques = list(nx.find_cliques(graph))

    """
    Girvan-Newman algorithm for community detection
    """
    def Girvan_Newman_algorithm(self, graph):
        communities = []
        while len(graph.edges()) != 0:
            edge_betweenness = nx.edge_betweenness_centrality(graph,
                                                              normalized = False,
                                                              weight = None)
            values = list(edge_betweenness.values())
            max_value = max(values)
            for edge in graph.edges():
                if(edge_betweenness[edge] == max_value):
                    graph.remove_edge(edge[0], edge[1])
            component = nx.connected_component_subgraphs(graph)
            if len(component) > 1:
                communities.append(component)
        return communities


class Ranking:
    def __init__(self, type, graphfile, color_measure = None, size_measure = None,
                 cmap = None, initial_size = None):
        self.type = type
        if(self.type == 'colorRanking'):
            self.cmap = cmap
            self.color_ranking = self.rank_nodes(color_measure, graphfile)
            self.colorbase = self.draw_color_base()
        elif(self.type == 'bothRanking'):
            self.cmap = cmap
            size_values = self.rank_nodes(size_measure, graphfile)
            color_values = self.rank_nodes(color_measure, graphfile)
            self.size_ranking = self.define_size_ranking(size_values, initial_size)
            self.color_ranking = self.get_sequence_of_nodes(color_values)
            self.colorbase = self.draw_color_base()
        else:
            self.size_ranking = self.define_size_ranking(self.rank_nodes(size_measure, graphfile),
                                                         initial_size)
    """
    Get requested values
    """
    def rank_nodes(self, measure, graphfile):
        ranking = []
        values = nx.get_node_attributes(graphfile.graph.graph, measure)
        if(self.type == 'colorRanking'):
            for node in graphfile.graph.graph.nodes():
                ranking.append(graphfile.graph.graph.node[node][measure])
            return ranking
        elif(self.type == 'sizeRanking' or self.type == 'bothRanking'):
            return values

    """
    Define size of node according to its values of a requested metric
    """
    def define_size_ranking(self, ranking, initial_size):

        sorted_ranking = sorted(ranking.items(), key=operator.itemgetter(1))
        size_ranking = []
        first_loop = True
        previous = None
        nodelist = []
        for t in sorted_ranking:
            nodelist.append(t[0])
            if(not first_loop):
                if(float(t[1]) > float(previous)):
                    sum = sum + 50
                    size_ranking.append(sum)
                else:
                    size_ranking.append(sum)
            else:
                sum = 50
                size_ranking.append(sum)
            first_loop = False
            previous = t[1]
        return [size_ranking, nodelist]
    """
    Order nodes according to their values
    """
    def get_sequence_of_nodes(self, values):
        new_nodelist = []
        for node in self.size_ranking[1]:
            new_nodelist.append(values.get(node))
        return new_nodelist

    def draw_color_base(self):
        fig = plt.figure()
        ax1 = fig.add_axes([0.05, 0.80, 0.9, 0.95])
        cmap = plt.get_cmap(self.cmap)
        norm = matplotlib.colors.Normalize(vmin=min(self.color_ranking),
                                           vmax=max(self.color_ranking))
        cb1 = matplotlib.colorbar.ColorbarBase(ax1, cmap=cmap,
                                           norm=norm,
                                           orientation='horizontal')
        return self.create_colorbase_url()

    def create_colorbase_url(self):
        try:
            rv = StringIO.StringIO()
            plt.savefig(rv, format="png")
            url =  "data:image/png;base64,%s" % rv.getvalue().encode("base64").strip()
        finally:
            plt.clf()
        return url

class Path:
    def __init__(self, graph, source, target, path_type, weight):
        self.graph = graph
        if (weight == 'weighted'):
            self.weight = True
        else:
            self.weight = False
        if (self.graph.uploaded):
            self.source = source
            self.target = target
        else:
            self.source = int(source)
            self.target = int(target)
        self.path_length = None
        self.path_type = path_type
        self.path_sequence = self.calculate_path()


    def calculate_path(self):
        if(self.path_type == "shortest"):
            return self.find_shortest_paths()
        elif(self.path_type == "strongest"):
            return self.find_strongest_path()
        elif self.path_type == 'critical':
            return self.critical_path_detection()


    """
    Calculate all pairs of strongest paths using Floyd Warshall algorithm
    """

    def calculate_strongest_paths_Floyd_Warshall(self):
        s = {}
        pred = {}
        for u in self.graph.graph.nodes():
            for v in self.graph.graph.nodes():

                if (self.graph.graph.has_edge(u, v)):

                    s[(u, v)] = float(self.graph.graph.edge[u][v]['weight'])
                    pred[(u, v)] = u
                else:
                    s[(u, v)] = float('-inf')
                    pred[(u, v)] = None
        for node1 in self.graph.graph.nodes():
            for node2 in self.graph.graph.nodes():
                if (node1 != node2):
                    for node3 in self.graph.graph.nodes():
                        if (node3 != node2):
                            if (s[(node2, node3)] < min(s[(node2, node1)], s[(node1, node3)])):
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
        if (len(path_sequence[0]) == 1):
            return None
        else:
            self.path_length = pred[1][(self.source, self.target)]
            return path_sequence

    """
    Define nodes included in the strongest path between a source
    node and a target node
    """

    def find_shortest_paths(self):

        if (not self.weight):
            weight = None
        else:
            weight = 'weight'
        if (self.graph.has_negative_weights and self.graph.is_weighted):
            pred = nx.bellman_ford(self.graph.graph, self.source,
                                   weight='weight')
            sequen = [self.target]
            path_sequence = self.create_path_sequence(pred[0], self.target,
                                                      sequen)
            self.path_length = pred[1][self.target]
            return path_sequence
        else:
            paths = nx.all_shortest_paths(self.graph.graph, self.source, self.target,
                                          weight=weight)
            try:
                p = []
                for path in paths:
                    p.append(path)
            except nx.NetworkXNoPath:
                return None
            else:
                self.path_length = nx.shortest_path_length(self.graph.graph,
                                                           self.source, self.target,
                                                           weight=weight)
                return p

    """
    Use Bellman-Ford algorithm to find shortest paths in graphs
    with negative weights.
    """

    def critical_path_detection(self):
        path = self.bellman_ford_critical_path()
        sequence = [self.target]
        path_sequence = self.create_path_sequence(path[0], self.target,
                                                  sequence)
        if (len(path_sequence[0]) == 1):
            return None
        else:
            self.path_length = path[1][self.target]
            return path_sequence


    def bellman_ford_critical_path(self):
        pred = {}
        dist = {}
        for node in self.graph.graph.nodes():
            pred[node] = None
            if node != self.source:
                dist[node] = float('-inf')
            else:
                dist[node] = 0
        for i in range(0, self.graph.graph.number_of_nodes()):
            for u, v in self.graph.graph.edges():
                if self.weight:
                    length = dist[u] + self.graph.graph.edge[u][v]['weight']
                else:
                    length = dist[u] + 1
                if dist[v] < length:
                    dist[v] = length
                    pred[v] = u
        return pred, dist

    """
    Calculate the sequence of visited nodes in a path
    """

    def create_path_sequence(self, pred, target, sequence):
        while (pred[target] != None):
            sequence.append(pred[target])
            return self.create_path_sequence(pred, pred[target], sequence)
        sequence.reverse()
        path_sequence = [sequence]
        return path_sequence


    def calculate_path_vertices(self, path):
        path_vertices = []
        for s in range(0, len(path) - 1):
            if s != len(path) - 1:
                vertice = (path[s], path[s + 1])
                path_vertices.append(vertice)
        return path_vertices


    def get_nodes_which_are_not_in_path(self, graph, paths):
        rest_nodes = []
        for node in graph.nodes():
            is_in_path = False
            for path in paths:
                if node in path:
                    is_in_path = True
            if (not is_in_path):
                rest_nodes.append(node)
        return rest_nodes


    def get_edges_which_are_not_in_paths(self, graph, path_vertices):
        rest_edges = []
        for edge in graph.edges():
            is_in_path = False
            for p_edge in path_vertices:
                if edge in p_edge:
                    is_in_path = True
            if (not is_in_path):
                rest_edges.append(edge)
        return rest_edges
