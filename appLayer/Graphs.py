import networkx as nx
import UserAdministrator as user_admin
from random import random, randint
import graph_info as info
import ApplicationModel as model
import handler as hand
from google.appengine.ext import db


class Graphs:
    def __init__(self, parameters, layout='random', upload=True,
                 data=None):
        self.growing = False
        if (upload):
            self.uploaded = True
            self.create_graph(data, parameters['graphtype'])
        else:
            self.uploaded = False
            self.get_generated_graph(parameters)
        self.initialize_graph_characteristics()
        if (self.is_weighted):
            self.initialize_graph_characteristics_weighted()
        if (layout != None):
            self.set_node_pos(layout)


    """
    Create graph object according to file data saved in datastore
    """

    def create_graph(self, data, graphtype):
        if (graphtype == 'Directed'):
            self.graphtype = 'Directed'
            self.graph = nx.DiGraph()
        else:
            self.graph = nx.Graph()
            self.graphtype = 'Undirected'
        lines = str(data).split('\n')
        for line in lines:
            words = str(line).split(' ')
            if (len(words) != 1):
                if (not self.graph.has_node(words[0])):
                    self.graph.add_node(words[0])
                if (not self.graph.has_node(words[1])):
                    self.graph.add_node(words[1])
                if (len(words) == 3):
                    self.graph.add_edge(words[0], words[1],
                                        weight=float(words[2]))

                else:
                    self.graph.add_edge(words[0], words[1])

    """
    Save in datastore nodes position
    """

    def set_node_pos(self, selection='random'):
        pos = {}
        if (selection == "circular"):
            pos = nx.circular_layout(self.graph)

        elif (selection == "random"):
            pos = nx.random_layout(self.graph)

        elif (selection == "spring"):
            pos = nx.spring_layout(self.graph)

        elif (selection == "shell"):
            pos = nx.shell_layout(self.graph)

        else:
            pos = nx.spectral_layout(self.graph)

        nx.set_node_attributes(self.graph, 'position', pos)
        return pos


    def get_node_label(self):
        label = {}
        for node in self.graph.nodes():
            label[node] = (str(node))
        return label

    def check_if_weighted(self):
        self.is_weighted = False
        for u, v in self.graph.edges():
            if ('weight' in self.graph.edge[u][v]):
                self.is_weighted = True
                break

    def check_if_has_negative_weights(self):
        if (self.is_weighted):
            for u, v in self.graph.edges():
                if (float(self.graph.edge[u][v]['weight']) < 0):
                    self.has_negative_weights = True
                    break


    def get_graph_diameter(self, weight):
        max_value = float('-inf')
        for u in self.graph.nodes():
            for v in self.graph.nodes():
                descendants = nx.descendants(self.graph, u)
                if (v in descendants):
                    if (not self.has_negative_weights):
                        dist = nx.shortest_path_length(self.graph, u, v,
                                                       weight=weight)
                    else:
                        distances = nx.floyd_warshall(self.graph,
                                                      weight=weight)
                        dist = distances[u][v]
                    if (dist > max_value):
                        max_value = dist
        return max_value

    def get_shortest_paths_info(self, weight):
        sum = float(0)
        number_of_shortest_paths = 0
        for u in self.graph.nodes():
            for v in self.graph.nodes():
                descendants = nx.descendants(self.graph, u)
                if (v in descendants):
                    shortest_paths = nx.all_shortest_paths(self.graph,
                                                           u, v, weight)
                    paths = list(shortest_paths)
                    number = len(paths)
                    sum = sum + number * nx.shortest_path_length(self.graph,
                                                                 u, v, weight)
                    number_of_shortest_paths = number_of_shortest_paths + number
        return sum, number_of_shortest_paths

    def is_fully_connected(self):
        if (self.graphtype == 'Directed'):
            return nx.is_strongly_connected(self.graph)
        else:
            return nx.is_connected(self.graph)


    def initialize_graph_characteristics(self):
        self.has_negative_weights = False
        self.negative_cycle = False
        self.diameter = False
        self.average_shortest_path_length = []
        self.number_of_shortest_paths = []
        self.density = nx.density(self.graph)
        self.check_if_weighted()
        self.is_connected = self.is_fully_connected()
        self.is_DAG = nx.is_directed_acyclic_graph(self.graph)
        self.number_of_nodes = self.graph.number_of_nodes()
        self.number_of_edges = self.graph.number_of_edges()


    def initialize_graph_characteristics_weighted(self):
        self.check_if_has_negative_weights()
        self.negative_cycle = nx.negative_edge_cycle(self.graph, 'weight')
        if (not self.negative_cycle):
            self.diameter.append(self.get_graph_diameter('weight'))

    def graph_data(self, username, upload, data):
        user = user_admin.UserAdministrator(username, '')
        self.graphfile = user.create_temp_project(upload, data,
                                                  self.graphtype)


    def initialize_barabasi_graph(self, n, directed):
        if (directed):
            g = nx.DiGraph()
        else:
            g = nx.Graph()
        for i in range(0, n):
            g.add_node(i)
        for u in g.nodes():
            for v in g.nodes():
                if (u != v):
                    if (directed):
                        g.add_edge(u, v)
                        g.add_edge(v, u)
                    else:
                        g.add_edge(u, v)
        return g

    def add_new_node_barabasi_model(self):
        new_edges = []
        node = self.graph.number_of_nodes()
        self.graph.add_node(node)
        while self.graph.degree(node) < self._initial_nodes:
            random_node = randint(0, self.graph.number_of_nodes() - 2)
            p = (self.graph.degree(random_node) / float((2 * self.graph.number_of_edges())))
            chance1 = random()
            if p > chance1 and (not self.graph.has_edge(node, random_node)):
                if (not self.graph.is_directed()):
                    self.graph.add_edge(node, random_node)
                    new_edges.append((node, random_node))
                else:
                    chance2 = random()
                    if p > chance2:
                        if (not self.graph.has_edge(node, random_node)
                            and (not self.graph.has_edge(random_node, node))):
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
        if self.number_of_nodes != self._initial_nodes:
            self.graph.remove_node(self.number_of_nodes - 1)
        return self.graph

    def get_generated_graph(self, parameters):
        model = parameters['model']
        n = int(parameters['nodes'])
        if (model != 'regular' and model != 'watts_strogatz'):
            if (parameters['graphtype'] == 'Directed'):
                directed = True
            else:
                directed = False
        if (model == 'erdos'):
            self.graph = nx.erdos_renyi_graph(n,
                                              float(parameters['probability']),
                                              directed=directed)
        elif (model == 'binomial'):
            self.graph = nx.binomial_graph(n,
                                           float(parameters['probability']),
                                           directed=directed)
        elif (model == 'watts_strogatz'):
            if (parameters['isConnected'] == 'Yes'):
                self.graph = nx.connected_watts_strogatz_graph(n,
                                                               int(parameters['edges']),
                                                               float(parameters['probability']))
            else:
                self.graph = nx.watts_strogatz_graph(n,
                                                     int(parameters['edges']),
                                                     float(parameters['probability']))
        elif (model == 'regular'):
            self.graph = nx.random_regular_graph(int(parameters['degree']), n)
        elif (model == 'random'):
            self.graph = nx.gnm_random_graph(n, int(parameters['edges']),
                                             directed=directed)
        elif (model == 'barabasi'):
            self.growing = True
            self._initial_nodes = n
            self.graph = self.initialize_barabasi_graph(n, directed)

        if (self.graph.is_directed()):
            self.graphtype = 'Directed'
        else:
            self.graphtype = 'Undirected'


    def calculate_clustering_coifficient(self):
        if (self.is_weighted):
            values = nx.clustering(self.graph, weight="weight")
        else:
            values = nx.clustering(self.graph, weight=None)
        nx.set_node_attributes(self.graph, 'clustering', values)

    def calculate_weighted_degree(self):
        if (self.is_weighted):
            values = nx.degree(self.graph, weight="weight")
            nx.set_node_attributes(self.graph, 'weighted_degree', values)


    def calculate_weighted_in_degree(self):
        if (self.is_weighted):
            values = self.graph.in_degree(weight="weight")
            nx.set_node_attributes(self.graph, 'weighted_in_degree', values)


    def calculate_weighted_out_degree(self):
        if (self.is_weighted):
            values = self.graph.out_degree(weight="weight")
            nx.set_node_attributes(self.graph, 'weighted_out_degree', values)


    def calculate_pageRank(self):
        if (self.is_weighted):
            values = nx.pagerank_numpy(self.graph, weight='weight')
        else:
            values = nx.pagerank_numpy(self.graph, weight=None)
        nx.set_node_attributes(self.graph, 'pagerank', values)

    def calculate_degree_centrality(self):
        values = nx.degree_centrality(self.graph)
        nx.set_node_attributes(self.graph, 'degree', values)

    def calculate_in_degree_centrality(self):
        values = nx.in_degree_centrality(self.graph)
        nx.set_node_attributes(self.graph, 'in_degree', values)

    def calculate_out_degree_centrality(self):
        values = nx.out_degree_centrality(self.graph)
        nx.set_node_attributes(self.graph, 'out_degree', values)

    def calculate_betweeness_centrality(self):
        if (self.is_weighted):
            values = nx.betweenness_centrality(self.graph, weight="weight")
        else:
            values = nx.betweenness_centrality(self.graph, weight=None)
        nx.set_node_attributes(self.graph, 'betweenness', values)

    def calculate_closeness_centrality(self):
        values = nx.closeness_centrality(self.graph)
        nx.set_node_attributes(self.graph, 'closeness', values)

    def calculate_eigenvector_centrality(self):
        values = nx.eigenvector_centrality_numpy(self.graph)
        nx.set_node_attributes(self.graph, 'eigenvector', values)

    def find_connected_components(self, connectivity):
        if connectivity.find("weak") != -1:
            components = nx.weakly_connected_component_subgraphs(self.graph)
        elif connectivity.find("strong") != -1:
            components = nx.strongly_connected_component_subgraphs(self.graph)
        else:
            components = nx.connected_component_subgraphs(self.graph)
        counter = 0
        dict = {}
        for i in range(0, len(components)):
            for node in self.graph.nodes():
                if (components[i].has_node(node)):
                    dict[node] = 'A' + str(counter)
            counter = counter + 1
        nx.set_node_attributes(self.graph, connectivity, dict)

    def calculate_edge_betweeness(self):
        if (self.is_weighted):
            values = nx.edge_betweenness_centrality(self.graph, weight="weight")
        else:
            values = nx.edge_betweenness_centrality(self.graph)
        nx.set_edge_attributes(self.graph, 'betweenness', values)

    def add_data(self):
        self.calculate_betweeness_centrality()
        self.calculate_closeness_centrality()
        self.calculate_eigenvector_centrality()
        self.calculate_edge_betweeness()
        if self.graphtype == 'Directed':
            self.calculate_pageRank()
            self.calculate_in_degree_centrality()
            self.calculate_out_degree_centrality()
            self.find_connected_components('weak')
            self.find_connected_components('strong')
            if (self.is_weighted):
                self.calculate_weighted_in_degree()
                self.calculate_weighted_out_degree()
        else:
            self.calculate_clustering_coifficient()
            self.calculate_degree_centrality()
            self.find_connected_components('full')
            if self.is_weighted:
                self.calculate_weighted_degree()

    def data_exists(self):
        try:
            self.graph.node['closeness']
            exists = True
        except KeyError:
            exists = False
        return exists

    def calculate_degree_over_time(self, time):
        degree_values = list(nx.degree_centrality(self.graph).values())
        degree_variance = {0: sum(degree_values) / len(degree_values)}
        average_shortest_path = {0: nx.average_shortest_path_length(self.graph)}
        for i in range(1, time + 1):
            self.add_new_node_barabasi_model()
            degree_values = list(nx.degree_centrality(self.graph).values())
            degree_variance[i] = sum(degree_values) / len(degree_values)
            average_shortest_path[i] = nx.average_shortest_path_length(self.graph)
        return degree_variance, average_shortest_path

    def directed_graph_data(self):
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
        if self.graph.is_directed():
            return self.directed_graph_data()
        else:
            return self.undirected_graph_data()

    def get_edge_data(self):
        data = []
        for u, v in self.graph.edges():
            row = (u, v, self.graph.edge[u][v]['weight'],
                   self.graph.edge[u][v]['betweenness'])
            data.append(row)
        return data

    def get_graph_txtformat(self):
        data = []
        for u, v, in self.graph.edges():
            if self.is_weighted:
                row = (str(u), str(v), str(self.graph.edge[u][v]['weight']))
            else:
                row = (str(u), str(v))
            data.append(row)
        return data

    def get_average_values(self, values_type):
        values = nx.get_node_attributes(self.graph, values_type).values()
        return sum(values) / len(values)
