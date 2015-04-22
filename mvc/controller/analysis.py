"""
This module contains classes that represent entities that results from the
graph analysis. Includes methods, techniques and widely known algorithms
for that purpose.

For example, such algorithms are Bellman-Ford algorithms for shortest path
detection, Girvan - Newman algorithm for community detection, etc.
"""
__author__ = 'Thodoris Sotiropoulos'


import networkx as nx
import matplotlib as mat

mat.use('AGG')
import operator


def _remove_max_edge(G, weight=None):
    """
    Removes edge with the highest value on betweenness centrality.

    Repeat this step until more connected components than the connected
    components of the original graph are detected.

    It is part of Girvan-Newman algorithm.

    :param G: NetworkX graph
    :param weight: string, optional (default=None) Edge data key corresponding
    to the edge weight.
    """
    number_components = nx.number_connected_components(G)
    while nx.number_connected_components(G) <= number_components:
        betweenness = nx.edge_betweenness_centrality(G, weight=weight)
        max_value = max(betweenness.values())
        for edge in G.edges():
            if betweenness[edge] == max_value:
                G.remove_edge(*edge)


def girvan_newman_algorithm(graph, weight='weight'):
    """
    Implementation of Girvan - Newman algorithm for community detection.

    :param graph Graph object to check for communities.
    :return List of communities which are detected.
    """
    g = graph.copy().to_undirected()
    components = []
    while g.number_of_edges() > 0:
        _remove_max_edge(g, weight)
        components.append(nx.connected_component_subgraphs(g))
    return components


class Community:
    """
    This class represents clusters that can be detected on a graph such as
    communities and cliques.
    """
    def __init__(self, graph):
        """
        Detects both cliques and communities of graph.

        :param graph Graph object to be analyzed.
        """
        g = nx.Graph(graph)
        self.cliques = self.get_cliques(g)
        self.communities = girvan_newman_algorithm(g)

    def get_cliques(self, graph):
        """ Detects maximal cliques of graph. """
        return list(nx.find_cliques(graph))


def define_size_ranking(ranking):
    """
    Algorithm that sizes nodes of a graph according to its value from a measure
    such as closeness centrality, clustering coefficient, etc.

    For example, nodes with higher values on this specific measure, they are
    depicted with a bigger size.
    """
    sorted_ranking = sorted(ranking.items(), key=operator.itemgetter(1))
    size_ranking = []
    first_loop = True
    previous = None
    nodelist = []
    sumary = 0
    variance = 50
    for t in sorted_ranking:
        nodelist.append(t[0])
        if not first_loop:
            if float(t[1]) > float(previous):
                sumary += variance
                size_ranking.append(sumary)
            else:
                size_ranking.append(sumary)
        else:
            sumary = variance
            size_ranking.append(sumary)
        first_loop = False
        previous = t[1]
    return [size_ranking, nodelist]


class Ranking:
    """
    This class represents the ranking of nodes according to their value from
    a specific measure such as closeness centrality, clustering coefficient, etc.

    Rankings of nodes can be done with the following three ways:
    Color Ranking, in this way, nodes are colored according to their value on a
    specific measure as mentioned above.
    Size Ranking, in this way, values of nodes define the size of nodes.
    Hybrid Ranking, in this way both color and size ranking are used.
    """
    def __init__(self, ranking_type, graphfile, color_measure=None, size_measure=None,
                 cmap=None):
        """
        Rank nodes according to the parameters given by user.

        :param ranking_type Type of ranking. It can be done, color ranking, size
        ranking, hybrid ranking.
        :param graphfile graph object which is currently analyzed by user.
        :param color_measure Defines measure which nodes are going to be colored
        according to.
        :param size_measure Defines measure which nodes are going to be sized
        according to.
        :param cmap Color diversities for the color ranking way.
        """
        self.type = ranking_type
        if self.type == 'colorRanking':
            self.cmap = cmap
            self.color_ranking = self.rank_nodes(color_measure, graphfile)
        elif self.type == 'bothRanking':
            self.cmap = cmap
            size_values = self.rank_nodes(size_measure, graphfile)
            color_values = self.rank_nodes(color_measure, graphfile)
            self.size_ranking = define_size_ranking(size_values)
            self.color_ranking = self.get_sequence_of_nodes(color_values)
        else:
            self.size_ranking = define_size_ranking(self.rank_nodes(size_measure, graphfile))

    def rank_nodes(self, measure, graphfile):
        """
        Rank nodes according to the specific measure given as parameter such
        as closeness centrality, clustering coefficient, etc.

        :param measure Measure of nodes.
        :param graphfile graph object which is currently analyzed by user.
        :return values of node measures.
        """
        ranking = []
        values = nx.get_node_attributes(graphfile.graph.graph, measure)
        if self.type == 'colorRanking':
            for node in graphfile.graph.graph.nodes():
                ranking.append(graphfile.graph.graph.node[node][measure])
            return ranking
        elif self.type == 'sizeRanking' or self.type == 'bothRanking':
            return values

    def get_sequence_of_nodes(self, values):
        """
        Add values of dictionary given as parameter to a list.

        :param values dictionary to add its values to a list.
        """
        new_nodelist = []
        for node in self.size_ranking[1]:
            new_nodelist.append(values.get(node))
        return new_nodelist


class Path:
    """
    This class represents a path which can be a shortest, critical or strongest
    path between two nodes (one is the source node, and other is target node).
    """
    def __init__(self, graph, source, target, path_type, weight):
        """
        Detect a path (critical, shortest or strongest) between two nodes.

        :param graph Graph object to detect paths.
        :param source Source node of path.
        :param target Target node of path.
        :param path_type Type of path. It can be critical, shortest or strongest.
        :param weight Defines the way (critical or shortest) path has to be
        calculated (based on path length, or based on edge weight).
        """
        self.graph = graph
        if weight == 'weighted':
            self.weight = True
        else:
            self.weight = False
        if self.graph.uploaded:
            self.source = source
            self.target = target
        else:
            self.source = int(source)
            self.target = int(target)
        self.path_length = None
        self.path_type = path_type
        self.path_sequence = self.calculate_path()

    def calculate_path(self):
        """
        Detect path (critical, shortest or strongest) between two nodes.

        :return A list with sequence of nodes that are included in path.
        """
        if self.path_type == "shortest":
            return self.find_shortest_paths()
        elif self.path_type == "strongest":
            return self.find_strongest_path()
        elif self.path_type == 'critical':
            return self.critical_path_detection()

    def calculate_strongest_paths_floyd_warshall(self):
        """
        Implementation of Floyd Warshall algorithm for strongest path detection.

        :return dictionary pred so pred[i] = j is the predecessor of node i in
        the strongest path to node j and dictionary so that s[i] = j is the
        strongest path between nodes i and j.
        """
        s = {}
        pred = {}
        for u in self.graph.graph.nodes():
            for v in self.graph.graph.nodes():

                if self.graph.graph.has_edge(u, v):

                    s[(u, v)] = float(self.graph.graph.edge[u][v]['weight'])
                    pred[(u, v)] = u
                else:
                    s[(u, v)] = float('-inf')
                    pred[(u, v)] = None
        for node1 in self.graph.graph.nodes():
            for node2 in self.graph.graph.nodes():
                if node1 != node2:
                    for node3 in self.graph.graph.nodes():
                        if node3 != node2:
                            if s[(node2, node3)] < min(s[(node2, node1)], s[(node1, node3)]):
                                s[(node2, node3)] = min(s[(node2, node1)], s[(node1, node3)])
                                pred[(node2, node3)] = pred[(node1, node3)]
        return pred, s

    def find_strongest_path(self):
        """
        Strongest path detection between two nodes.

        Customized Floyd Warshall algorithm is used for strongest path detection.

        :return A list with sequence of nodes that are included in path. If
        there is no path between these nodes None value is returned.
        """
        pred = self.calculate_strongest_paths_floyd_warshall()
        predecessors = {}
        for node in self.graph.graph.nodes():
            predecessors[node] = pred[0][(self.source, node)]
        sequence = [self.target]
        path_sequence = self.create_path_sequence(predecessors, self.target,
                                                  sequence)
        if len(path_sequence[0]) == 1:
            return None
        else:
            self.path_length = pred[1][(self.source, self.target)]
            return path_sequence

    def find_shortest_paths(self):
        """
        Shortest path detection between two nodes.

        If graph has negative weights, Bellman Ford algorithm is used for
        path detection, otherwise Djikstra Algorithm is used.

        :return A list with sequence of nodes that are included in path. If
        there is no path between these nodes None value is returned.
        """
        if not self.weight:
            weight = None
        else:
            weight = 'weight'
        if self.graph.has_negative_weights and self.graph.is_weighted:
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

    def critical_path_detection(self):
        """
        Critical path detection between two nodes.

        Customized Bellman Ford algorithm for critical path detection is used.

        :return A list with sequence of nodes that are included in path. If
        there is no path between these nodes None value is returned.
        """
        path = self.bellman_ford_critical_path()
        sequence = [self.target]
        path_sequence = self.create_path_sequence(path[0], self.target,
                                                  sequence)
        if len(path_sequence[0]) == 1:
            return None
        else:
            self.path_length = path[1][self.target]
            return path_sequence

    def bellman_ford_critical_path(self):
        """
        Implementation of customized Bellman Ford algoritm for critical path
        detection.

        :return dictionary pred so that pred[i] = j is the predecessor of node i in
        the critical path to node j and dictionary so that dist[i] = j is the
        strongest path between nodes i and j.
        """
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

    def create_path_sequence(self, pred, target, sequence):
        """
        Recursive method for getting list of sequence of nodes that are
        visited in a path.

        :param pred: dictionary pred so that pred[i] = j is the predecessor of node i in
        the path to node j
        :param target: target node of path.
        :param sequence: incomplete list of sequence of nodes.
        :return: A list with sequence of nodes that are included in path.
        """
        while pred[target] is not None:
            sequence.append(pred[target])
            return self.create_path_sequence(pred, pred[target], sequence)
        sequence.reverse()
        path_sequence = [sequence]
        return path_sequence

    @staticmethod
    def get_path_edges(path):
        """
        Gets edges that are included in a list of sequence of nodes that
        are included in path.
        :param path: A list with sequence of nodes that are included in path.
        :return: List of tuples that represents an edge in graph so that
        (i, j) represents the edge from node i to node j.
        """
        path_edges = []
        for s in range(0, len(path) - 1):
            if s != len(path) - 1:
                vertice = (path[s], path[s + 1])
                path_edges.append(vertice)
        return path_edges

    @staticmethod
    def get_nodes_which_are_not_in_path(graph, paths):
        """
        Gets list of nodes that are not included in the list with sequence
        of nodes that are included in path.

        :param graph: Graph object which included these nodes.
        :param paths: A list with sequence of nodes that are included in path.
        :return: List of nodes that are not included in path.
        """
        rest_nodes = []
        for node in graph.nodes():
            is_in_path = False
            for path in paths:
                if node in path:
                    is_in_path = True
            if not is_in_path:
                rest_nodes.append(node)
        return rest_nodes

    @staticmethod
    def get_edges_which_are_not_in_paths(graph, path_edges):
        """
        Gets list of tuples (that represents edges) that are not included in the
        list of edges that are included in path.

        :param graph: Graph object which included these edges.
        :param path_edges List of tuples that represents an edge in graph so that
        (i, j) represents the edge from node i to node j.
        :return: List of edges that are not included in path.
        """
        rest_edges = []
        for edge in graph.edges():
            is_in_path = False
            for p_edge in path_edges:
                if edge in p_edge:
                    is_in_path = True
            if not is_in_path:
                rest_edges.append(edge)
        return rest_edges
