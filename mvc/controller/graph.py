"""
This module contains class that represents a graph. This module, actually,
represents the data associated with the graph (subject) which other modules
can either analyze or visualize.
"""
__author__ = 'Thodoris Sotiropoulos'

from random import random, randint

import networkx as nx


def calculate_average_shortest_path_length(graph, weight):
    """
    Calculates the average shortest path length of a graph. This
    algorithm can either take graph's weight into account or not.

    :param graph Graph object
    :param weight If None then average shortest path length will be calculated
    without taking graph weight into account. Otherwise, if parameter's value
    is equal to 'weight' average shortest path length will be calculated
    taking graph's weight into account.
    :return Average shortest path length of graph.
    """
    average_path = []
    for g in nx.connected_component_subgraphs(graph.to_undirected()):
        try:
            average_path.append(nx.average_shortest_path_length(g, weight))
        except ZeroDivisionError:
            pass
        except ValueError:
            return None
    return sum(average_path) / len(average_path)


class Graphs:
    """ Class that represents a graph. """

    def __init__(self, parameters, layout='random', upload=True,
                 data=None):
        """
        Constructor which initializes a graph object according to the method
        of graph initialization. Graph initialization can be done either by
        uploading a graph file or by generating a random graph by a mathematical
        model, such as Binomial graph.

        :param parameters dictionary of parameters which define the way graph is
        going to be initialized.
        :param layout Layout of graph's nodes.
        :param upload If true graph object is initialized by a graph file which user
        uploaded, if false graph object is initialized by a mathematical model.
        :param data Data of graph file which user uploaded.

        """
        self.growing = False
        self.diameter = 0.0
        self.average_shortest_path_length = []
        self.graph = None
        self.is_weighted = False
        self.has_negative_weights = False
        self.negative_cycle = False
        self.is_connected = False
        self.is_DAG = False
        self.density = 0.0
        self.number_of_nodes = 0
        self.graphtype = None
        self.number_of_edges = 0
        self._initial_nodes = 0
        if upload:
            self.uploaded = True
            self.create_graph(data, parameters['graphtype'])
        else:
            self.uploaded = False
            self.get_generated_graph(parameters)
        self.initialize_graph_characteristics()
        if self.is_weighted:
            self.initialize_graph_characteristics_weighted()
        if layout is not None:
            self.set_node_pos(layout)

    def create_graph(self, data, graphtype):
        """
        Creates graph object of networkx library according to the data of the graph
        file uploaded by user.

        :param data Data of graph file which user uploaded.
        :param graphtype type of graph. Directed or Undirected.
        :raise IOError IOError is thrown when graph object cannot be initialized
        with the given data of uploaded file.

        """
        if graphtype == 'Directed':
            self.graphtype = 'Directed'
            self.graph = nx.DiGraph()
        else:
            self.graph = nx.Graph()
            self.graphtype = 'Undirected'
        lines = str(data).split('\n')
        for line in lines:
            if line:
                words = str(line).split(' ')
                if len(words) == 2 or len(words) == 3:
                    if not self.graph.has_node(words[0]):
                        self.graph.add_node(words[0])
                    if not self.graph.has_node(words[1]):
                        self.graph.add_node(words[1])
                    if len(words) == 3:
                        try:
                            self.graph.add_edge(words[0], words[1],
                                                weight=float(words[2]))
                        except ValueError:
                            raise IOError
                    else:
                        self.graph.add_edge(words[0], words[1])
                elif len(words) == 1 or len(words) > 3:
                    raise IOError

    def set_node_pos(self, selection='random'):
        """
        Set layout of graph's nodes.

        :param selection: Layout of graph's nodes.
        :return: position of graph's nodes.

        """
        if selection == "circular":
            pos = nx.circular_layout(self.graph)
        elif selection == "random":
            pos = nx.random_layout(self.graph)
        elif selection == "spring":
            pos = nx.spring_layout(self.graph)
        elif selection == "shell":
            pos = nx.shell_layout(self.graph)
        else:
            pos = nx.spectral_layout(self.graph)
        nx.set_node_attributes(self.graph, 'position', pos)
        return pos

    def get_node_label(self):
        """
        Get label of nodes. Labels can be either the name of node according to
        the uploaded file or the a unique default number when a graph object
        is initialized by mathematical model randomly.

        :return: Label of nodes.
        """
        label = {}
        for node in self.graph.nodes():
            label[node] = (str(node))
        return label

    def check_if_weighted(self):
        """
        Check is graph is a weighted graph or not. Assigns value of attribute
        'is_weighted' accordingly. If graph is weighted value of this attribute
        is True, False otherwise.

        """
        self.is_weighted = False
        for u, v in self.graph.edges():
            if 'weight' in self.graph.edge[u][v]:
                self.is_weighted = True
                break

    def check_if_has_negative_weights(self):
        """
        Check if a weighted graph has edges with negative weighted.
        Assigns value of attribute 'has_negative_weights' accordingly.
        If graph has negative weights, value of this attribute is True,
        False otherwise.

        """
        if self.is_weighted:
            for u, v in self.graph.edges():
                if float(self.graph.edge[u][v]['weight']) < 0:
                    self.has_negative_weights = True
                    break

    def is_fully_connected(self):
        """
        Check if graph is connected.

        :return: True if graph is connected, false otherwise.
        """
        if self.graphtype == 'Directed':
            return nx.is_strongly_connected(self.graph)
        else:
            return nx.is_connected(self.graph)

    def calculate_diameter(self):
        """
        Calculates graph's diameter.

        :return: graph's diameter.
        """
        try:
            return nx.diameter(self.graph)
        except nx.NetworkXError:
            return None

    def initialize_graph_characteristics(self):
        """
        Initializes class attributes which associated with information about
        graph such as graph's diameter, if graph is weighted, if graph is Directed
        Acyclic Graph, number of nodes, number of edges, average shortest path length,
        etc.

        """
        self.has_negative_weights = False
        self.negative_cycle = False
        self.diameter = self.calculate_diameter()
        self.density = nx.density(self.graph)
        self.check_if_weighted()
        self.is_connected = self.is_fully_connected()
        self.is_DAG = nx.is_directed_acyclic_graph(self.graph)
        self.number_of_nodes = self.graph.number_of_nodes()
        self.number_of_edges = self.graph.number_of_edges()
        if self.growing:
            self.average_shortest_path_length = []
            self.average_shortest_path_length.append(calculate_average_shortest_path_length(self.graph,
                                                                                            None))
        else:
            self.average_shortest_path_length.append(calculate_average_shortest_path_length(self.graph,
                                                                                            None))

    def initialize_graph_characteristics_weighted(self):
        """
        Initializes class attributes which asscociated especially with weighted
        graphs such as if graph has negative cycles, if graph has negative weights,
        average shortest path length based on weights of edges.

        """
        self.check_if_has_negative_weights()
        self.negative_cycle = nx.negative_edge_cycle(self.graph, 'weight')
        self.average_shortest_path_length.append(calculate_average_shortest_path_length(self.graph,
                                                                                        'weight'))

    @staticmethod
    def initialize_barabasi_graph(n, directed):
        """
        Initializes a graph based on Albert Barabasi's model.

        Parameters define the type of graph and the initial number of nodes.
        Then each node creates an edge with every other node.

        :param n: Initial number of nodes.
        :param directed: True if graph is directed, False otherwise
        :return: initial graph

        """
        if directed:
            g = nx.DiGraph()
        else:
            g = nx.Graph()
        for i in range(0, n):
            g.add_node(i)
        for u in g.nodes():
            for v in g.nodes():
                if u != v:
                    if directed:
                        g.add_edge(u, v)
                        g.add_edge(v, u)
                    else:
                        g.add_edge(u, v)
        return g

    def add_new_node_barabasi_model(self):
        """
        Add new node to graph based on Albert Barabasi model.

        This method, implements the algorithm of preferential attachment model.
        Every new node creates as many edges as the initial number of graph's
        nodes. Then chooses the nodes with whom creates an edge according to its
        degree value. Therefore, there a high possiblity to create edges with nodes
        which are older in network.

        :return: Graph with the new node added and list of edges which new node created.
        """
        new_edges = []
        node = self.graph.number_of_nodes()
        self.graph.add_node(node)
        while self.graph.degree(node) < self._initial_nodes:
            random_node = randint(0, self.graph.number_of_nodes() - 2)
            p = (self.graph.degree(random_node) / float((2 * self.graph.number_of_edges())))
            chance1 = random()
            if p > chance1 and (not self.graph.has_edge(node, random_node)):
                if not self.graph.is_directed():
                    self.graph.add_edge(node, random_node)
                    new_edges.append((node, random_node))
                else:
                    chance2 = random()
                    if p > chance2:
                        if (not (
                                    self.graph.has_edge(node, random_node)
                                or not (not self.graph.has_edge(random_node, node)))):
                            self.graph.add_edge(node, random_node)
                            self.graph.add_edge(random_node, node)
                            new_edges.append((node, random_node))
                            new_edges.append((random_node, node))
                    else:
                        if not self.graph.has_edge(node, random_node):
                            self.graph.add_edge(node, random_node)
                            new_edges.append((node, random_node))
        return self.graph, new_edges

    def delete_node(self):
        """
        Delete the last node added with its edges from a Albert Barabasi graph.

        :return: Graph with node deleted.
        """
        if self.number_of_nodes != self._initial_nodes:
            self.graph.remove_node(self.number_of_nodes - 1)
        return self.graph

    def get_generated_graph(self, parameters):
        """
        Initializes graph according to the dictianary of parameters given by user.
        This graph is going to be initializes by a mathematical model such as
        Erdos - Renyi model, Albert Barabasi model, Watts Strogatz model, etc
        randomly.

        :param parameters dictionary of parameters which define the way graph is
        going to be initialized.

        """
        model = parameters['model']
        n = int(parameters['nodes'])
        directed = False
        if model != 'regular' and model != 'watts_strogatz' \
                and parameters['graphtype'] == 'Directed':
            directed = True
        if model == 'erdos':
            self.graph = nx.erdos_renyi_graph(n,
                                              float(parameters['probability']),
                                              directed=directed)
        elif model == 'binomial':
            self.graph = nx.binomial_graph(n,
                                           float(parameters['probability']),
                                           directed=directed)
        elif model == 'watts_strogatz':
            if parameters['isConnected'] == 'Yes':
                self.graph = nx.connected_watts_strogatz_graph(n,
                                                               int(parameters['edges']),
                                                               float(parameters['probability']))
            else:
                self.graph = nx.watts_strogatz_graph(n,
                                                     int(parameters['edges']),
                                                     float(parameters['probability']))
        elif model == 'regular':
            self.graph = nx.random_regular_graph(int(parameters['degree']), n)
        elif model == 'random':
            self.graph = nx.gnm_random_graph(n, int(parameters['edges']),
                                             directed=directed)
        elif model == 'barabasi':
            self.growing = True
            self._initial_nodes = n
            self.graph = self.initialize_barabasi_graph(n, directed)

        if self.graph.is_directed():
            self.graphtype = 'Directed'
        else:
            self.graphtype = 'Undirected'

    def calculate_clustering_coifficient(self):
        """
        Calculates clustering coefficient for every node on graph.

        For undirected graphs only.
        """
        if self.is_weighted:
            values = nx.clustering(self.graph, weight="weight")
        else:
            values = nx.clustering(self.graph, weight=None)
        nx.set_node_attributes(self.graph, 'clustering', values)

    def calculate_weighted_degree(self):
        """
        Calculates degree centrality for every node of graph based on edge weights.

        For weighted undirected graphs only.
        """
        if self.is_weighted:
            values = nx.degree(self.graph, weight="weight")
            nx.set_node_attributes(self.graph, 'weighted_degree', values)

    def calculate_weighted_in_degree(self):
        """
        Calculates In - degree centrality for every node of graph based on edge weights.

        For weighted directed graphs only.
        """
        if self.is_weighted:
            values = self.graph.in_degree(weight="weight")
            nx.set_node_attributes(self.graph, 'weighted_in_degree', values)

    def calculate_weighted_out_degree(self):
        """
        Calculates Out - degree centrality for every node of graph based on edge weights.

        For weighted directed graphs only.
        """
        if self.is_weighted:
            values = self.graph.out_degree(weight="weight")
            nx.set_node_attributes(self.graph, 'weighted_out_degree', values)

    def calculate_pagerank(self):
        """
        Calculates PageRank for every node of graph.

        For directed graphs only.
        """
        if self.is_weighted:
            values = nx.pagerank_numpy(self.graph, weight='weight')
        else:
            values = nx.pagerank_numpy(self.graph, weight=None)
        nx.set_node_attributes(self.graph, 'pagerank', values)

    def calculate_degree_centrality(self):
        """
        Calculates degree centrality for every node of graph.

        For undirected graphs only.
        """
        values = nx.degree_centrality(self.graph)
        nx.set_node_attributes(self.graph, 'degree', values)

    def calculate_in_degree_centrality(self):
        """
        Calculates In - degree centrality for every node of graph.

        For directed graphs only.
        """
        values = nx.in_degree_centrality(self.graph)
        nx.set_node_attributes(self.graph, 'in_degree', values)

    def calculate_out_degree_centrality(self):
        """
        Calculates Out - degree centrality for every node of graph.

        For directed graphs only.
        """
        values = nx.out_degree_centrality(self.graph)
        nx.set_node_attributes(self.graph, 'out_degree', values)

    def calculate_betweeness_centrality(self):
        """ Calculates betweenness centrality for every node of graph. """
        if self.is_weighted:
            values = nx.betweenness_centrality(self.graph, weight="weight")
        else:
            values = nx.betweenness_centrality(self.graph, weight=None)
        nx.set_node_attributes(self.graph, 'betweenness', values)

    def calculate_closeness_centrality(self):
        """ Calculates closeness centrality for every node of graph. """
        values = nx.closeness_centrality(self.graph)
        nx.set_node_attributes(self.graph, 'closeness', values)

    def calculate_eigenvector_centrality(self):
        """ Calculates eigenvector centrality for every node of graph. """
        values = nx.eigenvector_centrality_numpy(self.graph)
        nx.set_node_attributes(self.graph, 'eigenvector', values)

    def find_connected_components(self, connectivity):
        """
        Detects connected components of graph.

        For directed graphs, it detected both weakly and strongly connected
        components.

        :param connectivity: Defines components to be found. Weakly, Strongly or
        for undirected graphs.
        """
        if connectivity.find("weak") != -1:
            components = nx.weakly_connected_component_subgraphs(self.graph)
        elif connectivity.find("strong") != -1:
            components = nx.strongly_connected_component_subgraphs(self.graph)
        else:
            components = nx.connected_component_subgraphs(self.graph)
        counter = 0
        connected_components = {}
        for i in range(0, len(components)):
            for node in self.graph.nodes():
                if components[i].has_node(node):
                    connected_components[node] = 'A' + str(counter)
            counter += 1
        nx.set_node_attributes(self.graph, connectivity, connected_components)

    def calculate_edge_betweeness(self):
        """ Calculates betweenness centrality for every edge of graph. """
        if self.is_weighted:
            values = nx.edge_betweenness_centrality(self.graph, weight="weight")
        else:
            values = nx.edge_betweenness_centrality(self.graph)
        nx.set_edge_attributes(self.graph, 'betweenness', values)

    def add_data(self):
        """ Adds all information associated with the graph on the networkx graph object. """
        self.calculate_betweeness_centrality()
        self.calculate_closeness_centrality()
        self.calculate_eigenvector_centrality()
        self.calculate_edge_betweeness()
        if self.graphtype == 'Directed':
            self.calculate_pagerank()
            self.calculate_in_degree_centrality()
            self.calculate_out_degree_centrality()
            self.find_connected_components('weak')
            self.find_connected_components('strong')
            if self.is_weighted:
                self.calculate_weighted_in_degree()
                self.calculate_weighted_out_degree()
        else:
            self.calculate_clustering_coifficient()
            self.calculate_degree_centrality()
            self.find_connected_components('full')
            if self.is_weighted:
                self.calculate_weighted_degree()

    def data_exists(self):
        """
        Check if information such as centralities, clustering associated with
        the graph has already been calculated.

        :return: True if information has already been calculated,
        False otherwise.
        """
        try:
            value = self.graph.node['closeness']
            exists = True
        except KeyError:
            exists = False
        return exists

    def calculate_evolution_over_time(self, time):
        """
        Calculated average degree centrality and average shortest path length
        for different time, until the time given as parameter by user.

        For growing networks such as Albert Barabasi graphs.

        :param time: Time to stop calculation
        :return: dictionaries of average degree centrality and average shortest
        path length for each time.
        """
        degree_values = list(nx.degree_centrality(self.graph).values())
        degree_variance = {0: sum(degree_values) / len(degree_values)}
        average_shortest_path = {0: calculate_average_shortest_path_length(self.graph, None)}
        for i in range(1, time + 1):
            self.add_new_node_barabasi_model()
            degree_values = list(nx.degree_centrality(self.graph).values())
            degree_variance[i] = sum(degree_values) / len(degree_values)
            average_shortest_path[i] = calculate_average_shortest_path_length(self.graph, None)
        return degree_variance, average_shortest_path

    def directed_graph_data(self):
        """
        Adds all information such as centralities, PageRank, etc associated with directed
        graph nodes to a list of tuples.

        Each tuple contains all information mentioned above for a single node.

        :return: List of tuples
        """
        data = []
        for node in self.graph.nodes():
            basic_data = (node, self.graph.node[node]['in_degree'],
                          self.graph.node[node]['out_degree'],
                          self.graph.node[node]['closeness'],
                          self.graph.node[node]['betweenness'],
                          self.graph.node[node]['eigenvector'],
                          self.graph.node[node]['pagerank'],
                          self.graph.node[node]['weak'],
                          self.graph.node[node]['strong'])
            if self.is_weighted:
                data_weighted = (self.graph.node[node]['weighted_in_degree'],
                                 self.graph.node[node]['weighted_out_degree'])
                data.append(basic_data + data_weighted)
            else:
                data.append(basic_data)
        return data

    def undirected_graph_data(self):
        """
        Adds all information such as centralities, PageRank, etc associated with
        undirected graph nodes to a list of tuples.

        Each tuple contains all information mentioned above for a single node.

        :return: List of tuples
        """
        data = []
        for node in self.graph.nodes():
            basic_data = (node, self.graph.node[node]['degree'],
                          self.graph.node[node]['closeness'],
                          self.graph.node[node]['betweenness'],
                          self.graph.node[node]['eigenvector'],
                          self.graph.node[node]['clustering'],
                          self.graph.node[node]['full'])
            if self.is_weighted:
                data_weighted = (self.graph.node[node]['weighted_degree'],)
                data.append(basic_data + data_weighted)
            else:
                data.append(basic_data)
        return data

    def get_node_data(self):
        """
        Gets all information such as centralities, PageRank, etc associated
        with a graph nodes.

        Each tuple contains all information mentioned aboved for a single node.

        :return: List of tuples
        """
        if self.graph.is_directed():
            return self.directed_graph_data()
        else:
            return self.undirected_graph_data()

    def get_edge_data(self):
        """
        Adds all information such as betweenness centrality, weight, associated
        with a graph edges.

        Each tuple contains all information mentioned above for a single node.

        :return: List of tuples
        """
        data = []
        for u, v in self.graph.edges():
            if self.is_weighted:
                weight = self.graph.edge[u][v]['weight']
            else:
                weight = 1.0
            row = (u, v, weight,
                   self.graph.edge[u][v]['betweenness'])
            data.append(row)
        return data

    def get_graph_txtformat(self):
        """
        Gets graph's edges and then generates a graph file in txt format.
        File has to follow the principles mentioned below:
        It has to include all graph's edges and edge weight (if graph is
        weighted).
        Each row incudes:
        -- Edge's source node following by whitespace
        -- Edge's target node following by whitespace

        If graph is weighted row also includes edge weight

        """
        data = []
        for u, v, in self.graph.edges():
            if self.is_weighted:
                row = (str(u), str(v), str(self.graph.edge[u][v]['weight']))
            else:
                row = (str(u), str(v))
            data.append(row)
        return data

    def get_average_values(self, values_type):
        """
        Get average values of a measure such as closeness centrality, clustering
        coefficient.

        :param values_type: Type of measure.
        :return: Average values of measure.
        """
        values = nx.get_node_attributes(self.graph, values_type).values()
        return sum(values) / len(values)
