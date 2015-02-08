"""
This module contains request handler functions for the generation of
diagrams for distribution or dynamic analysis.

For example, a diagram for reasons mentioned above can be a frequency
diagram for closeness centrality of graph's nodes. On X-AXIS are closeness
centrality values and on Y-AXIS are number of nodes.

"""
from mvc.controller import graphfile as current_graph

__author__ = 'Thodoris Sotiropoulos'

import json

from mvc.controller.depiction import Diagram
from flask import request, Response, session
from main import app


@app.route('/_create_diagram')
def create_diagram():
    """
    A request handler function that takes one parameter which defines
    the type of diagram.

    A diagram can be a frequency diagram of closeness centrality,
    degree centrality, clustering coefficient, etc.

    :return: Encoded string of diagram image and mean of values in JSON format.

    """
    graph = current_graph.graphfile[session['user']]
    diagram_type = request.args.get('diagram', None, type=str)
    diag = Diagram(diagram_type, graph)
    average_values = graph.graph.get_average_values(diagram_type)
    json_obj = {'url': diag.url, 'average': average_values}
    return Response(json.dumps(json_obj))


@app.route('/_dynamic_analysis')
def dynamic_analysis():
    """
    A request handler function that takes one parameter which defines
    a future time for the graph. Then creates two diagrams:

    The first one describes the evolution of average degree between current time
    of graph and the future time specified by the parameter.

    The second one described the evolution of average shortest path length between
    current time of graph and the future time specified by the parameter.

    :return: Encoded strings of diagram images in JSON format.

    """
    graph = current_graph.graphfile[session['user']]
    time = request.args.get('time', 1, type=int)
    url = Diagram.degree_over_time(time, graph)
    json_obj = {'degree': url[0], 'pathInTime': url[1]}
    return Response(json.dumps(json_obj))
