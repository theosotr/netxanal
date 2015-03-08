"""
This module contains all request handler functios that are associated with
requests for file downloading.

For instance, these files can be, image of graph visualization in png format,
edge information and node in information in CSV format, graph file in txt format,
diagrams in png format.
"""
__author__ = 'Thodoris Sotiropoulos'

import csv
import StringIO
from base64 import decodestring

from mvc.controller import graphfile as current_graph
from flask import stream_with_context, request, session
from main import app
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response


@app.route('/download_node_info')
def download_node_info():
    """
    Gets a request for node information download. Then generates a file in
    csv format with all required information.

    :return: CSV file with the node information
    """
    def download():
        """
        Gets all node information of the graph such as centrality measures
        (degree centrality, closeness centrality, etc.), pagerank if graph is
        directed, clustering coefficient if graph is undirected and then it
        creates a file in CSV format without saving it.
        """
        graph = current_graph.graphfile[session['user']]
        info = graph.graph.get_node_data()
        data = StringIO.StringIO()
        w = csv.writer(data)
        if graph.graph.graph.is_directed():
            w.writerow(('node', 'in_degree', 'out_degree', 'closeness',
                        'betweenness', 'eigenvector', 'pagerank', 'weak',
                        'strong', 'weighted_in_degree', 'weighted_out_degree'))
        else:
            w.writerow(('node', 'degree', 'closeness',
                        'betweenness', 'eigenvector', 'clustering', 'full',
                        'weighted_degree'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)
        for item in info:
            w.writerow(item)
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    headers = Headers()
    headers.add('Content-Disposition', 'attachment', filename='nodes.csv')
    return Response(
        stream_with_context(download()),
        mimetype='text/csv', headers=headers
    )


@app.route('/download_edge_info')
def download_edge_info():
    """
    Gets a request for edge information download. Then generates a file in
    csv format with all required information.

    :return: CSV file with the edge information
    """
    def download():
        """
        Gets all edge information of the graph such as edge's source node,
        edge's target node, edge weight if graph is weighted, betweenness centrality
        and then it creates a file in CSV format without saving it.
        """
        graph = current_graph.graphfile[session['user']]
        info = graph.graph.get_edge_data()
        data = StringIO.StringIO()
        w = csv.writer(data)
        w.writerow(('source_node', 'target_node', 'weight', 'betweenness'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)
        for item in info:
            w.writerow(item)
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    headers = Headers()
    headers.add('Content-Disposition', 'attachment', filename='edges.csv')
    return Response(
        stream_with_context(download()),
        mimetype='text/csv', headers=headers
    )


@app.route('/download_graph_image')
def download_graph_image():
    """
    Gets encoded string for png image of graph visualization. It decodes it
    and then generates a png file of image without saving it.

    :return: Image of graph in png format.
    """
    image = current_graph.graphfile[session['user']].image.url.split(",")[1]
    image_output = StringIO.StringIO()
    image_output.write(decodestring(image))  # Write decoded image to buffer
    image_output.seek(0)
    headers = Headers()
    headers.add('Content-Disposition', 'attachment', filename='graph_img.png')
    return Response(
        image_output,
        mimetype='image/png',
        headers=headers
    )


@app.route('/download_diagram', methods=['POST'])
def download_diagram():
    """
    Gets encoded string for png image of a frequency diagram It decodes it
    and then generates a png file of image without saving it.

    :return: Image of frequency diagram in a png format.
    """
    diagram = request.form['diagram'].split(',')[1]
    image_output = StringIO.StringIO()
    image_output.write(decodestring(diagram))  # Write decoded image to buffer
    image_output.seek(0)
    headers = Headers()
    headers.add('Content-Disposition', 'attachment', filename='diagram.png')
    return Response(
        image_output,
        mimetype='image/png',
        headers=headers
    )


@app.route('/download_graph')
def download_graph():
    """
    Gets edges of graph and then generates a graph file in txt format.

    :return: Graph file in txt format.
    """
    def download():
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
        graph = current_graph.graphfile[session['user']]
        info = graph.graph.get_graph_txtformat()
        data = StringIO.StringIO()
        for row in info:
            if graph.graph.is_weighted:
                data.write(row[0] + " " + row[1] + " " + row[2] + "\n")
            else:
                data.write(row[0] + " " + row[1] + "\n")
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
    headers = Headers()
    headers.add('Content-Disposition', 'attachment', filename='graph.txt')
    return Response(
        stream_with_context(download()),
        mimetype='text/txt',
        headers=headers
    )
