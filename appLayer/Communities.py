import networkx as nx

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