__author__ = 'Thodoris Sotiropoulos'

import json

from flask import session, request, render_template, redirect, url_for, Response
from main import app
from mvc.controller.graph import *
from mvc.controller.analysis import *
from mvc.controller.depiction import *
import UserAdministrator as user_admin
import mvc.controller.graphfile as current_graph


@app.route('/upload', methods=['GET', 'POST'])
def draw_graph():
    if not session['login']:
        return redirect(url_for('mainpage'))
    f = request.files['file']
    filestream = f.read()
    parameters = request.form
    graph = Graphs(parameters, layout='random', upload=True,
                     data=filestream)
    user = user_admin.UserAdministrator(session['user'])
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
    graph = current_graph.graphfile[session['user']]
    cliques = Communities(graph.graph.graph)
    return Response(json.dumps(cliques.cliques))


@app.route('/_rank_nodes')
def rank_nodes():
    graph = current_graph.graphfile[session['user']]
    if not graph.graph.data_exists():
        graph.graph.add_data()
    color_measure = request.args.get("colorMeasure", None, type=str)
    size_measure = request.args.get('sizeMeasure', None, type=str)
    colors = request.args.get("colors", None, type=str)
    ranking_way = request.args.get('rankingWay', None, type=str)
    ranking = Ranking(type=ranking_way, graphfile=graph,
                           color_measure=color_measure,
                           size_measure=size_measure, cmap=colors,
                           initial_size=graph.image.image_style.node_size)
    graph.image.ranking_nodes_image(ranking)
    if ranking_way == 'colorRanking' or ranking_way == 'bothRanking':
        urls = [graph.image.url, graph.image.ranking.colorbase]
    else:
        urls = [graph.image.url]
    return Response(json.dumps(urls))


@app.route("/open_project", methods=['GET', 'POST'])
def open_project():
    if not session['login']:
        return redirect(url_for('mainpage'))
    projectname = request.form['project']
    user = user_admin.UserAdministrator(session['user'])
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
    if not session['login']:
        return redirect(url_for('mainpage'))
    parameters = request.form
    r_graph = Graphs(parameters, 'random', False)
    user = user_admin.UserAdministrator(session['user'])
    current_graph.graphfile[session['user']] = user.create_temp_project(r_graph)
    graph = current_graph.graphfile[session['user']]
    if graph.graph.graphtype == "Directed":
        session['undirected'] = False
    else:
        session['undirected'] = True
    image_style = ImageStyle()
    graph.image = GraphImage(image_style, graph)
    session['showimage'] = True
    return redirect(url_for('graph'))


@app.route("/dynamic_graph")
def dynamic_graph():
    edges = request.args['edges']
    graph = current_graph.graphfile[session['user']]
    return render_template("index.html", name=graph.graph.graphtype,
                           number_of_nodes=graph.graph.number_of_nodes,
                           nodes=graph.graph.graph.nodes(),
                           edges=current_graph.graphfile.graph.number_of_edges,
                           is_weighted=current_graph.graphfile.graph.is_weighted,
                           url=current_graph.graphfile.image.url,
                           diameter=current_graph.graphfile.graph.diameter,
                           negative_cycle=current_graph.graphfile.graph.negative_cycle,
                           average=current_graph.graphfile.graph.average_shortest_path_length,
                           number=current_graph.graphfile.graph.number_of_shortest_paths,
                           negative_weights=current_graph.graphfile.graph.has_negative_weights,
                           density=current_graph.graphfile.graph.density,
                           is_DAG=current_graph.graphfile.graph.is_DAG,
                           is_connected=current_graph.graphfile.graph.is_connected,
                           growing=current_graph.graphfile.graph.growing,
                           new_edges=edges)


@app.route('/add_node', methods=['GET', 'POST'])
def add_node():
    returned_data = current_graph.graphfile.graph.add_new_node_barabasi_model()
    current_graph.graphfile[session['user']].graph.graph = returned_data[0]
    new_edges = " ".join(str(x) for x in returned_data[1])
    current_graph.graphfile[session['user']].graph.set_node_pos()
    current_graph.graphfile[session['user']].graph.initialize_graph_characteristics()
    image_style = ImageStyle()
    current_graph.graphfile[session['user']].image = GraphImage(image_style, current_graph.graphfile)
    return redirect(url_for('dynamic_graph', edges=new_edges))


@app.route("/delete_node", methods=["GET", "POST"])
def delete_node():
    current_graph.graphfile[session['user']].graph.graph = current_graph.graphfile.graph.delete_node()
    current_graph.graphfile[session['user']].graph.set_node_pos()
    current_graph.graphfile[session['user']].graph.initialize_graph_characteristics()
    image_style = ImageStyle()
    current_graph.graphfile[session['user']].image = GraphImage(image_style, current_graph.graphfile)
    return redirect(url_for('graph'))
