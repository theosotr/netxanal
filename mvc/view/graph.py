"""
This module contains view functions associated with the analysis of graph on graph
visualization page.

Graph analysis includes, path detections, such as shortest path, critical, strongest
path detection, , community detection, node ranking based on node measures
(closeness centrality, clustering coefficient etc), edit of graph image, cliques
detection.

Some of these steps of graph analysis also modify image of graph.

For example, edit of graph image obviously is associated with the modification of
graph image. Path detection also depicts the corresponding path to the image.

Apart from this, this module contains view functions associated with the import of
a graph. A graph import can be done, by uploading a graph file to the system,
generating a graph according to one of the available mathematical models of system or
by importing an existing graph file which has been previously saved by user.

"""
from mvc.model import user_model as user_admin

__author__ = 'Thodoris Sotiropoulos'

import json

from flask import session, request, render_template, redirect, url_for, Response
from main import app
from mvc.controller.graph import *
from mvc.controller.analysis import *
from mvc.controller.depiction import *
import mvc.controller.graphfile as current_graph


@app.route('/upload', methods=['GET', 'POST'])
def draw_graph():
    """
    Import a graph by uploading a graph file.

    System supports graph files in txt format.
    File has to follow the principles mentioned below:
    It has to include all graph's edges and edge weight (if graph is
    weighted).
    Each row incudes:
        -- Edge's source node following by whitespace
        -- Edge's target node following by whitespace

    If graph is weighted row also includes edge weight

    :return: Main page of graph visualization.

    """
    if not session['login']:
        return redirect(url_for('index'))
    f = request.files['file']
    filestream = f.read()
    parameters = request.form
    try:
        graph = Graphs(parameters, layout='random', upload=True,
                       data=filestream)
    except IOError:
        return redirect(url_for('mainpage', warning=True))
    user = user_admin.User(session['user'])
    current_graph.graphfile[session['user']] = user.create_temp_project(graph)
    if graph.graphtype == 'Directed':
        session['undirected'] = False
    else:
        session['undirected'] = True
    image_style = ImageStyle()
    current_graph.graphfile[session['user']].image = GraphImage(image_style,
                                                                current_graph.graphfile[session['user']])
    session['showimage'] = True
    return redirect(url_for('graph'))


@app.route("/_update_image")
def update_image():
    """
    Refresh graph image by editing one of the following fields:
    - Node size
    - Edge width
    - Font size of node labes,
    - Node color,
    - Edge color,
    - Font color of edge labels,
    - Node shape
    - Edge style
    - Graph layout
    - Depiction or not of edge weight

    :return: Encoded string of new graph image based on base64
    encoding system in JSON format.

    """
    updated_value = request.args.get('updatedValue', None, type=str)
    component_to_update = request.args.get('componentToUpdate', None, type=str)
    graph = current_graph.graphfile[session['user']]
    if component_to_update == 'layout':
        graph.image.image_style.layout = updated_value
        graph.image.graph.set_node_pos(updated_value)
    elif component_to_update == 'node_size':
        graph.image.image_style.node_size = int(updated_value)
        if graph.image.ranking is not None:
            graph.image.ranking.initial_size = int(updated_value)
    elif component_to_update == 'edge_width':
        graph.image.image_style.edge_width = float(updated_value)
    elif component_to_update == 'font_size':
        graph.image.image_style.font_size = int(updated_value)
    elif component_to_update == 'node_color':
        graph.image.image_style.node_color = updated_value
        graph.image.communities_image = False
        graph.image.ranking_image = False
    elif component_to_update == 'edge_color':
        graph.image.image_style.edge_color = updated_value
    elif component_to_update == 'font_color':
        graph.image.image_style.font_color = updated_value
    elif component_to_update == 'node_shape':
        graph.image.image_style.node_shape = updated_value
    elif component_to_update == 'edge_style':
        graph.image.image_style.edge_style = updated_value
    else:
        if updated_value == 'True':
            graph.image.image_style.edge_label = True
        else:
            graph.image.image_style.edge_label = False
    graph.image.update_image()
    return Response(json.dumps(graph.image.url))


@app.route('/_find_paths', methods=['GET', 'POST'])
def shortest_paths():
    """
    Detect a path on graph between two nodes. One node is the source
    node and one is the target node.

    Parameters of graph also define the type of graph. Three types of paths are
    supported by the system. Critical paths for DAG graphs, shortest path for
    graphs which do not have negative cycles and strongest paths for weighted
    graphs.

    Path also is depicted to the graph image, and node sequence of path and path
    length are also returned.

    Renewed graph image which depicts path is encoded on a string based on base64

    :return: JSON object which includes encoded string of graph image, path length
    and node sequence.

    """
    graph = current_graph.graphfile[session['user']]
    source = request.args.get('source', None, type=str)
    target = request.args.get('target', None, type=str)
    path_type = request.args.get('pathType', None, type=str)
    calculation_way = request.args.get('calculationWay', None, type=str)
    path = Path(graph.graph, source, target, path_type, calculation_way)
    json_obj = {}
    if path.path_sequence:
        graph.image.create_path(path)
        json_obj['url'] = graph.image.url
        json_obj['pathSequence'] = path.path_sequence
        json_obj['pathLength'] = path.path_length
    return Response(json.dumps(json_obj))


@app.route('/_find_communities')
def find_communities():
    """
    Detect communities of graph.

    Communities are depicted to graph image, colored with different colors.
    Renewed image is represented as an encoded string based on base64.
    Also list of communities is returned.

    :return: JSON object which included encoded string of graph image, and
    list of communities.

    """
    graph = current_graph.graphfile[session['user']]
    level = request.args.get('level', 1, type=int)
    graph.image.image_communities(level)
    json_obj = {'url': graph.image.url}
    componets_of_communities = []
    for community in graph.image.communities.communities[level - 1]:
        componets_of_communities.append(community.nodes())
    json_obj['listOfCommunities'] = componets_of_communities
    json_obj['levels'] = len(graph.image.communities.communities) - 1
    return Response(json.dumps(json_obj))


@app.route('/_find_cliques')
def find_cliques():
    """
    Detect cliques of graph. List of cliques is returned.

    :return: JSON object with the list of cliques.

    """
    graph = current_graph.graphfile[session['user']]
    cliques = Community(graph.graph.graph)
    return Response(json.dumps(cliques.cliques))


@app.route('/_rank_nodes')
def rank_nodes():
    """
    Rank nodes based on a selected measure (closeness centrality,
    clustering coefficient, etc) given by user.

    Node ranking can be done with three different ways. First is color ranking.
    Each node has a color according to its value of the selected measure. Second
    way is size ranking. Each node has a size according to its value of
    the selected measure. The last one is the hybric way which both color
    ranking and size ranking are done parallelly.

    With node ranking user can easily see which nodes have the higher
    and lower values, which is variance of node values.

    :return: JSON object which includes encoded string of graph image
    based on base64.

    """
    graph = current_graph.graphfile[session['user']]
    if not graph.graph.data_exists():
        graph.graph.add_data()
    color_measure = request.args.get("colorMeasure", None, type=str)
    size_measure = request.args.get('sizeMeasure', None, type=str)
    colors = request.args.get("colors", None, type=str)
    ranking_way = request.args.get('rankingWay', None, type=str)
    ranking = Ranking(ranking_type=ranking_way, graphfile=graph,
                      color_measure=color_measure,
                      size_measure=size_measure, cmap=colors)
    graph.image.ranking_nodes_image(ranking)
    if ranking_way == 'colorRanking' or ranking_way == 'bothRanking':
        urls = [graph.image.url, graph.image.ranking.colorbase]
    else:
        urls = [graph.image.url]
    return Response(json.dumps(urls))


@app.route("/open_project", methods=['GET', 'POST'])
def open_project():
    """
    Import a graph by importing one which has been previously saved by
    user.

    :return: Main page of graph visualization.
    """
    if not session['login']:
        return redirect(url_for('index'))
    projectname = request.form['project']
    user = user_admin.User(session['user'])
    current_graph.graphfile[session['user']] = user.import_existing_project(projectname)
    graph = current_graph.graphfile[session['user']]
    if graph.graphtype == "Directed":
        session['undirected'] = False
    else:
        session['undirected'] = True
    session['showimage'] = True
    return redirect(url_for('graph'))


@app.route('/random_graph', methods=['GET', 'POST'])
def random_graph():
    """
    Import a graph by generating a random graph based on one of the
    available mathematical models which are supported by system.

    :return: Main page of graph visualization.
    """
    if not session['login']:
        return redirect(url_for('index'))
    parameters = request.form
    r_graph = Graphs(parameters, 'random', False)
    user = user_admin.User(session['user'])
    current_graph.graphfile[session['user']] = user.create_temp_project(r_graph)
    graph = current_graph.graphfile[session['user']]
    if current_graph.graphfile[session['user']].graph.graphtype == "Directed":
        session['undirected'] = False
    else:
        session['undirected'] = True
    image_style = ImageStyle()
    graph.image = GraphImage(image_style, current_graph.graphfile[session['user']])
    session['showimage'] = True
    return redirect(url_for('graph'))


@app.route("/dynamic_graph")
def dynamic_graph():
    """
    Go the page of visualization of graph. It also returns all required
    information about graph such as the list of nodes, if it is weighted,
    if it is a DAG, measures(density), etc. It is especially for
    dynamic graphs.

    :return: Main page of graph visualization.

    """
    edges = request.args['edges']
    graph = current_graph.graphfile[session['user']]
    return render_template("index.html", name=graph.graph.graphtype,
                           number_of_nodes=graph.graph.number_of_nodes,
                           nodes=graph.graph.graph.nodes(),
                           edges=graph.graph.number_of_edges,
                           is_weighted=graph.graph.is_weighted,
                           url=graph.image.url,
                           negative_cycle=graph.graph.negative_cycle,
                           average=graph.graph.average_shortest_path_length,
                           number=graph.graph.number_of_shortest_paths,
                           negative_weights=graph.graph.has_negative_weights,
                           density=graph.graph.density,
                           is_DAG=graph.graph.is_DAG,
                           is_connected=graph.graph.is_connected,
                           diameter=graph.graph.diameter,
                           average_path=graph.graph.average_shortest_path_length,
                           growing=graph.graph.growing,
                           new_edges=edges)


@app.route('/add_node', methods=['GET', 'POST'])
def add_node():
    """
    Increase size of graph by adding a new node. New node 'select' with which
    node will be connected according to the Albert Barabasi algorithm.

    This operation is only supported for random graphs which were generated by
    Albert Barabasi model.

    :return: Main page of graph visualization.

    """
    returned_data = current_graph.graphfile[session['user']].graph.add_new_node_barabasi_model()
    current_graph.graphfile[session['user']].graph.graph = returned_data[0]
    new_edges = " ".join(str(x) for x in returned_data[1])
    current_graph.graphfile[session['user']].graph.set_node_pos()
    current_graph.graphfile[session['user']].graph.initialize_graph_characteristics()
    image_style = ImageStyle()
    current_graph.graphfile[session['user']].image = GraphImage(image_style,
                                                                current_graph.graphfile[session['user']])
    return redirect(url_for('dynamic_graph', edges=new_edges))


@app.route("/delete_node", methods=["GET", "POST"])
def delete_node():
    """
    Decrease size of graph by deleting a the previous node which was added.

    This operation is only supported for random graphs which were generated by
    Albert Barabasi model.

    :return: Main page of graph visualization.

    """
    current_graph.graphfile[session['user']].graph.graph = current_graph.graphfile[session['user']].graph.delete_node()
    current_graph.graphfile[session['user']].graph.set_node_pos()
    current_graph.graphfile[session['user']].graph.initialize_graph_characteristics()
    image_style = ImageStyle()
    current_graph.graphfile[session['user']].image = GraphImage(image_style,
                                                                current_graph.graphfile[session['user']])
    return redirect(url_for('graph'))
