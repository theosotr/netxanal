import matplotlib
matplotlib.use('AGG')
import StringIO
import pylab as plt
import handler as hand
import networkx as nx
import copy
import math


class Diagram:
    def __init__(self, x_values_type):
        self.x_values_type = x_values_type
        self.classes_number = 0
        self.class_width = 0.0
        self.bar_frequencies = []
        self.polygon_frequencies = []
        self.central_values = []
        self.initial_values = []
        self.values = self.get_x_values(self.x_values_type)
        self.initialize_values()
        self.create_histogram()
        self.create_polygon()
        self.url = self.get_diagram_url()

    """
    Get requested values
    """
    def get_x_values(self, measure):
        graph = hand.graphfile.graph.graph
        values = list(nx.get_node_attributes(graph, measure).values())
        return values

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

    def get_diagram_url(self):
        try:
            rv = StringIO.StringIO()
            plt.savefig(rv, format="png")
            url = "data:image/png;base64,%s" % rv.getvalue().encode("base64").strip()
        finally:
            plt.clf()
            plt.close()
        return url

    @staticmethod
    def degree_over_time(time):
        G = copy.deepcopy(hand.graphfile.graph)
        values_to_analyze = G.calculate_degree_over_time(time)
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