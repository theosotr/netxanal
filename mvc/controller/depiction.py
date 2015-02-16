__author__ = 'Thodoris Sotiropoulos'
from mvc.controller.analysis import Communities
from mvc.controller.analysis import Path
import matplotlib

matplotlib.use('AGG')
import StringIO
import pylab as plt
import networkx as nx
import copy
import math
from random import random


class GraphImage:
    """
    Initialize image of graph according to what should be depicted
    """

    def __init__(self, image_style, graphfile):
        self.url = None
        self.communities = None
        self.communities_image = False
        self.communities_color = {}
        self.level = 1
        self.path_image = False
        self.paths = None
        self.ranking = None
        self.ranking_image = False
        self.graph = graphfile.graph
        self.image_style = image_style
        self.simple_image()

    """
    Get node position from datastore
    """

    def get_node_pos(self):
        pos = nx.get_node_attributes(self.graph.graph, 'position')
        return pos

    """
    Draw edge weights
    """

    def draw_edge_weights(self, pos):
        if self.graph.graphtype == 'Undirected':
            return self.draw_edge_weights_undirected(pos)
        edge_list = []
        for u, v in self.graph.graph.edges():
            edge_labels = {}
            e1 = (u, v)
            edge_labels[tuple(e1)] = self.graph.graph.edge[u][v]['weight']
            if edge_list.count(str(u + v)) == 0 and self.graph.graphtype == 'Directed':
                nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels,
                                             font_size=9, label_pos=0.2)
                if self.graph.graph.has_edge(v, u):
                    edge_lab = {}
                    e2 = (v, u)
                    edge_list.append(str(v + u))
                    edge_lab[tuple(e2)] = self.graph.graph.edge[v][u]['weight']
                    nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_lab,
                                                 font_size=9, label_pos=0.2)

    def draw_edge_weights_undirected(self, pos):
        edge_labels = {}
        for u, v in self.graph.graph.edges():
            e = (u, v)
            edge_labels[tuple(e)] = self.graph.graph.edge[u][v]['weight']
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels,
                                     font_size=9)

    def create_image_url(self):
        plt.axis("off")
        try:
            rv = StringIO.StringIO()
            plt.savefig(rv, format="png")
            self.url = "data:image/png;base64,%s" % rv.getvalue().encode("base64").strip()
        finally:
            plt.clf()
            plt.close()
        return self.url

    def simple_image(self):
        pos = self.get_node_pos()
        self.draw_nodes(pos)
        self.draw_edges(pos)
        self.create_image_url()

    def draw_nodes(self, pos):
        nodes = self.graph.graph.nodes()
        nx.draw_networkx_nodes(self.graph.graph, pos, nodelist=nodes,
                               node_size=self.image_style.node_size,
                               node_color=self.image_style.node_color,
                               node_shape=self.image_style.node_shape)

    """
    Create graph image with the requested path depicted
    """

    def create_path(self, path=None):
        self.path_image = True
        self.communities_image = False
        self.ranking_image = False
        if path is not None:
            self.paths = path
        pos = self.get_node_pos()
        self.draw_path_nodes(pos)
        self.draw_path_edges(pos)
        self.create_image_url()

    def draw_path_nodes(self, pos):
        for path in self.paths.path_sequence:
            nx.draw_networkx_nodes(self.graph.graph, pos, nodelist=path,
                                   node_size=self.image_style.node_size + 100,
                                   node_color='crimson',
                                   node_shape=self.image_style.node_shape)
        rest_nodes = Path.get_nodes_which_are_not_in_path(self.graph.graph,
                                                          self.paths.path_sequence)
        nx.draw_networkx_nodes(self.graph.graph, pos, nodelist=rest_nodes,
                               node_size=self.image_style.node_size,
                               node_color=self.image_style.node_color,
                               node_shape=self.image_style.node_shape)

    def draw_path_edges(self, pos):
        all_vertices = []
        for path in self.paths.path_sequence:
            path_vertices = Path.calculate_path_vertices(path)
            all_vertices.append(path_vertices)
            nx.draw_networkx_edges(self.graph.graph, pos, edgelist=path_vertices,
                                   width=self.image_style.edge_width + 1,
                                   edge_color="black", style="dashed")
        rest_edges = Path.get_edges_which_are_not_in_paths(self.graph.graph,
                                                           all_vertices)
        label = self.graph.get_node_label()
        nx.draw_networkx_edges(self.graph.graph, pos, rest_edges,
                               width=self.image_style.edge_width,
                               edge_color=self.image_style.edge_color,
                               style=self.image_style.edge_style)
        nx.draw_networkx_labels(self.graph.graph, pos, labels=label,
                                font_size=self.image_style.font_size,
                                font_color=self.image_style.font_color)
        if self.graph.is_weighted and self.image_style.edge_label:
            self.draw_edge_weights(pos)

    """
    Create graph image with communities detected drawn with
    different color
    """

    def draw_communities(self, pos):
        g = nx.Graph(self.graph.graph)
        self.communities = Communities(g)
        counter = 0
        for community in self.communities.communities[self.level - 1]:
            if not self.communities_image:
                color = (random(), random(), random())
                self.communities_color[counter] = color
            else:
                try:
                    color = self.communities_color[counter]
                except KeyError:
                    color = (random(), random(), random())
                    self.communities_color[counter] = color
            nx.draw_networkx_nodes(g, pos, nodelist=community.nodes(),
                                   node_size=self.image_style.node_size,
                                   node_color=color,
                                   node_shape=self.image_style.node_shape)
            counter += 1
        self.communities_image = True

    def image_communities(self, level=None):
        self.path_image = False
        self.ranking_image = False
        if level is not None:
            self.level = level
        pos = self.get_node_pos()
        self.draw_communities(pos)
        self.draw_edges(pos)
        self.create_image_url()

    def update_image(self):
        if self.communities_image:
            self.image_communities()
        elif self.path_image:
            self.create_path()
        elif self.ranking_image:
            self.ranking_nodes_image()
        else:
            self.simple_image()

    def draw_edges(self, pos):
        label = self.graph.get_node_label()
        nx.draw_networkx_edges(self.graph.graph, pos, self.graph.graph.edges(),
                               width=self.image_style.edge_width,
                               edge_color=self.image_style.edge_color,
                               style=self.image_style.edge_style)
        nx.draw_networkx_labels(self.graph.graph, pos, labels=label,
                                font_size=self.image_style.font_size,
                                font_color=self.image_style.font_color)
        if self.graph.is_weighted and self.image_style.edge_label:
            self.draw_edge_weights(pos)

    def rank_nodes_by_color(self, pos):
        nx.draw_networkx_nodes(self.graph.graph, pos,
                               nodelist=self.graph.graph.nodes(),
                               node_size=self.image_style.node_size,
                               node_color=self.ranking.color_ranking,
                               node_shape=self.image_style.node_shape,
                               cmap=plt.get_cmap(self.ranking.cmap))

    def rank_nodes_by_size(self, pos):
        nx.draw_networkx_nodes(self.graph.graph,
                               pos, nodelist=self.ranking.size_ranking[1],
                               node_size=self.ranking.size_ranking[0],
                               node_color=self.image_style.node_color,
                               node_shape=self.image_style.node_shape)

    def rank_nodes_by_color_and_size(self, pos):
        nx.draw_networkx_nodes(self.graph.graph, pos,
                               nodelist=self.ranking.size_ranking[1],
                               node_size=self.ranking.size_ranking[0],
                               node_color=self.ranking.color_ranking,
                               node_shape=self.image_style.node_shape,
                               cmap=plt.get_cmap(self.ranking.cmap))

    """
    Create graph image with a nodes ranking. Either color ranking or size ranking
    or both color ranking and size ranking.
    """

    def ranking_nodes_image(self, ranking=None):
        self.ranking_image = True
        self.communities_image = False
        self.path_image = False
        if ranking is not None:
            self.ranking = ranking
        pos = self.get_node_pos()
        if self.ranking.type == 'colorRanking':
            self.rank_nodes_by_color(pos)
        elif self.ranking.type == 'sizeRanking':
            self.rank_nodes_by_size(pos)
        else:
            self.rank_nodes_by_color_and_size(pos)
        self.draw_edges(pos)
        self.create_image_url()


class ImageStyle:
    def __init__(self, selection='random', n_size=500, edge_width=1.0,
                 ncolor='red', ecolor='red', estyle='solid', shape='o',
                 fsize=12, fcolor='black', weights='on'):
        self.layout = selection
        self.node_size = n_size
        self.edge_width = edge_width
        self.node_color = ncolor
        self.edge_color = ecolor
        self.edge_style = estyle
        self.node_shape = shape
        self.font_size = fsize
        self.font_color = fcolor
        self.edge_label = weights


def get_x_values(measure, graphfile):
    graph = graphfile.graph.graph
    values = list(nx.get_node_attributes(graph, measure).values())
    return values


def get_diagram_url():
    try:
        rv = StringIO.StringIO()
        plt.savefig(rv, format="png")
        url = "data:image/png;base64,%s" % rv.getvalue().encode("base64").strip()
    finally:
        plt.clf()
        plt.close()
    return url


class Diagram:
    def __init__(self, x_values_type, graphfile):
        self.x_values_type = x_values_type
        self.classes_number = 0
        self.class_width = 0.0
        self.bar_frequencies = []
        self.polygon_frequencies = []
        self.central_values = []
        self.initial_values = []
        self.values = get_x_values(self.x_values_type, graphfile)
        self.initialize_values()
        self.create_histogram()
        self.create_polygon()
        self.url = get_diagram_url()

    """
    Get requested values
    """

    def initialize_values(self):
        min_value = min(self.values)
        max_value = max(self.values)
        variance = max_value - min_value
        self.classes_number = int(math.ceil(1 + 3.3 * math.log10(len(self.values)))) + 1
        self.class_width = variance / float(self.classes_number)
        self.central_values = [min_value - self.class_width / 2]
        classes = [(min_value, min_value + self.class_width)]
        self.central_values.append((min_value + min_value + self.class_width) / 2)
        for i in range(1, self.classes_number + 1):
            lower_limit = min_value + (i * self.class_width)
            upper_limit = min_value + (i + 1) * self.class_width
            classes.append((lower_limit, upper_limit))
            self.central_values.append((lower_limit + upper_limit) / 2)
        self.polygon_frequencies.append(0)
        for diagram_class in classes:
            counter = 0
            for value in self.values:
                if diagram_class[0] <= value < diagram_class[1]:
                    counter += 1
            self.bar_frequencies.append(counter)
            self.polygon_frequencies.append(counter)
            self.initial_values.append(diagram_class[0])

    def create_polygon(self):
        plt.plot(self.central_values, self.polygon_frequencies)

    def create_histogram(self):
        plt.subplots()
        opacity = 0.7
        error_config = {'ecolor': '0.1'}
        plt.bar(self.initial_values,
                self.bar_frequencies,
                self.class_width,
                alpha=opacity,
                color='green',
                error_kw=error_config)
        plt.xlabel(str.capitalize(self.x_values_type))
        plt.ylabel('Number of Nodes')
        plt.title(str.capitalize(self.x_values_type) + ' Distribution')
        plt.legend()
        plt.tight_layout()

    @staticmethod
    def degree_over_time(time, graphfile):
        graph_copy = copy.deepcopy(graphfile.graph)
        values_to_analyze = graph_copy.calculate_degree_over_time(time)
        degree_values = values_to_analyze[0].values()
        shortest_path_values = values_to_analyze[1].values()
        x_values = values_to_analyze[0].keys()
        plt.figure(1)
        plt.plot(x_values, degree_values, 'ro-')
        plt.xlabel('Time')
        plt.ylabel('Degree')
        plt.title('Degree over time')
        url1 = Diagram.get_url()
        plt.figure(2)
        plt.plot(x_values, shortest_path_values, 'ro-')
        plt.xlabel('Time')
        plt.ylabel('Average shortest path length')
        plt.title('Average shortest path length over time')
        url2 = Diagram.get_url()
        return url1, url2

    @staticmethod
    def get_url():
        try:
            rv = StringIO.StringIO()
            plt.savefig(rv, format="png")
            url = "data:image/png;base64,%s" % rv.getvalue().encode("base64").strip()
        finally:
            plt.clf()
            plt.close()
        return url