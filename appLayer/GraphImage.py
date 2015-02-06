from appLayer import Communities as c
import networkx as nx
import matplotlib
matplotlib.use('AGG')
import pylab as plt
import StringIO
import handler as hand
from random import random


class GraphImage:
    """
    Initialize image of graph according to what should be depicted
    """

    def __init__(self, image_style):
        self.url = None
        self.communities = None
        self.communities_image = False
        self.communities_color = {}
        self.level = 1
        self.path_image = False
        self.ranking = None
        self.ranking_image = False
        self.graph = hand.graphfile.graph
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
            if (edge_list.count(str(u + v)) == 0 and self.graph.graphtype == 'Directed'):
                nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels,
                                             font_size=9, label_pos=0.2)
                if (self.graph.graph.has_edge(v, u)):
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
            hand.graphfile.image = self
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
        rest_nodes = self.paths.get_nodes_which_are_not_in_path(self.graph.graph,
            self.paths.path_sequence)
        nx.draw_networkx_nodes(self.graph.graph, pos, nodelist=rest_nodes,
            node_size=self.image_style.node_size,
            node_color=self.image_style.node_color,
            node_shape=self.image_style.node_shape)

    def draw_path_edges(self, pos):
        all_vertices = []
        for path in self.paths.path_sequence:
            path_vertices = self.paths.calculate_path_vertices(path)
            all_vertices.append(path_vertices)
            nx.draw_networkx_edges(self.graph.graph, pos, edgelist=path_vertices,
                width=self.image_style.edge_width + 1,
                edge_color="black", style="dashed")
        rest_edges = self.paths.get_edges_which_are_not_in_paths(self.graph.graph,
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
        self.communities = c.Communities(g)
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






            
            
    