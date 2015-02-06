import matplotlib
matplotlib.use('AGG')
import pylab as plt
import StringIO
import handler as hand
import networkx as nx
import operator

class Ranking:
    def __init__(self, type, color_measure = None, size_measure = None, 
                 cmap = None, initial_size = None):
        self.type = type
        if(self.type == 'colorRanking'):
            self.cmap = cmap
            self.color_ranking = self.rank_nodes(color_measure)
            self.colorbase = self.draw_color_base()
        elif(self.type == 'bothRanking'):
            self.cmap = cmap
            size_values = self.rank_nodes(size_measure)
            color_values = self.rank_nodes(color_measure)
            self.size_ranking = self.define_size_ranking(size_values, initial_size)
            self.color_ranking = self.get_sequence_of_nodes(color_values)
            self.colorbase = self.draw_color_base()
        else:
            self.size_ranking = self.define_size_ranking(self.rank_nodes(size_measure), 
                                                         initial_size)
    """
    Get requested values
    """
    def rank_nodes(self, measure):
        ranking = []
        values = nx.get_node_attributes(hand.graphfile.graph.graph, measure)
        if(self.type == 'colorRanking'):
            for node in hand.graphfile.graph.graph.nodes():
                ranking.append(hand.graphfile.graph.graph.node[node][measure])
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