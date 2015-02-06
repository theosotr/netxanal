import json
import csv
import StringIO
from base64 import decodestring

from appLayer import Ranking as rank
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, stream_with_context
import appLayer.Graphs as g
import appLayer.GraphImage as g_image
import UserAdministrator as user_admin
import appLayer.Diagram as diagram
import ApplicationModel as model
import appLayer.Communities as c
import appLayer.Path as p
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response


app = Flask(__name__)
app.secret_key = "rd"
graph = None
current_user = None
project = None
graphfile = None


@app.route('/')
def mainpage():
    session["showimage"] = False
    return render_template("login.html")

import registration

@app.route('/graph', methods=['GET', 'POST'])
def graph():
    global graphfile
    return render_template("index.html", name =  graphfile.graph.graphtype,
                            number_of_nodes = graphfile.graph.number_of_nodes,
                            nodes = graphfile.graph.graph.nodes(),
                            edges = graphfile.graph.number_of_edges,
                            is_weighted = graphfile.graph.is_weighted,
                            url = graphfile.image.url,
                            diameter = graphfile.graph.diameter,
                            negative_cycle = graphfile.graph.negative_cycle,
                            negative_weights = graphfile.graph.has_negative_weights,
                            density = graphfile.graph.density, is_DAG = graphfile.graph.is_DAG,
                            is_connected = graphfile.graph.is_connected,
                            growing = graphfile.graph.growing)


@app.route('/upload', methods= ['GET','POST'])
def draw_graph():
    if(not session['login']):
        return redirect(url_for('mainpage'))
    f = request.files['file']
    filestream = f.read()
    parameters = request.form
    global graph
    graph = g.Graphs(parameters, layout = 'random', upload = True, 
                     data = filestream)
    user = user_admin.UserAdministrator(session['user'])
    global graphfile
    graphfile = user.create_temp_project(graph)
    if(graph.graphtype == 'Directed'):
        session['undirected'] = False
    else:
        session['undirected'] = True
    image_style = g_image.ImageStyle()
    image = g_image.GraphImage(image_style)
    session['showimage'] = True
    return redirect(url_for('graph'))
    
@app.route("/import_file", methods=['GET', 'POST'])    
def import_file():
    if(not session['login']):
        return redirect(url_for('mainpage'))
    session["showimage"] = False
    model.delete_data()
    user = user_admin.UserAdministrator(session['user'])
    projects = user.get_existing_projects()
    return render_template('index.html', projects = projects)

@app.route("/_update_image")
def update_image():
    updated_value = request.args.get('updatedValue', None, type=str)
    component_to_update = request.args.get('componentToUpdate', None, type=str)
    global graphfile
    if component_to_update == 'layout':
        graphfile.image.image_style.layout = updated_value
        graphfile.image.graph.set_node_pos(updated_value)
    elif component_to_update == 'node_size':
        graphfile.image.image_style.node_size = int(updated_value)
        if graphfile.image.ranking is not None:
            graphfile.image.ranking.initial_size = int(updated_value)
    elif component_to_update == 'edge_width':
        graphfile.image.image_style.edge_width = float(updated_value)
    elif component_to_update == 'font_size':
        graphfile.image.image_style.font_size = int(updated_value)
    elif component_to_update == 'node_color':
        graphfile.image.image_style.node_color = updated_value
        graphfile.image.communities_image = False
        graphfile.image.ranking_image = False
    elif component_to_update == 'edge_color':
        graphfile.image.image_style.edge_color = updated_value
    elif component_to_update == 'font_color':
        graphfile.image.image_style.font_color = updated_value
    elif component_to_update == 'node_shape':
        graphfile.image.image_style.node_shape = updated_value
    elif component_to_update == 'edge_style':
        graphfile.image.image_style.edge_style = updated_value
    else:
        if updated_value == 'True':
            graphfile.image.image_style.edge_label = True
        else:
            graphfile.image.image_style.edge_label = False
    graphfile.image.update_image()
    return Response(json.dumps(graphfile.image.url))

@app.route("/node_info")
def node_info():
    if(not session['login']):
        return redirect(url_for('mainpage'))
    if(not graphfile.graph.data_exists()):
        graphfile.graph.add_data()
    if(graphfile.graph.graphtype == 'Directed'):
        return render_template("nodes_info.html",
                                graph = graphfile.graph.graph,
                                is_weighted = graphfile.graph.is_weighted)
    else:
        return render_template("nodes_info.html",
                               graph = graphfile.graph.graph,
                               is_weighted = graphfile.graph.is_weighted)


@app.route('/_find_paths', methods = ['GET', 'POST'])
def shortest_paths():
    source = request.args.get('source', None, type=str)
    target = request.args.get('target', None, type=str)
    path_type = request.args.get('pathType', None, type=str)
    calculation_way = request.args.get('calculationWay', None, type=str)
    path = p.Path(graphfile.graph, source, target, path_type, calculation_way)
    json_obj = {}
    if path.path_sequence:
        graphfile.image.create_path(path)
        json_obj['url'] = graphfile.image.url
        json_obj['pathSequence'] = path.path_sequence
        json_obj['pathLength'] = path.path_length
    return Response(json.dumps(json_obj))

@app.route('/_find_communities')
def find_communities():
    level = request.args.get('level', 1, type=int)
    graphfile.image.image_communities(level)
    json_obj = {'url': graphfile.image.url}
    componets_of_communities = []
    for community in graphfile.image.communities.communities[level - 1]:
        componets_of_communities.append(community.nodes())
    json_obj['listOfCommunities'] = componets_of_communities
    json_obj['levels'] = len(graphfile.image.communities.communities) - 1
    return Response(json.dumps(json_obj))

@app.route('/_find_cliques')
def find_cliques():
    cliques = c.Communities(graphfile.graph.graph)
    return Response(json.dumps(cliques.cliques))

@app.route('/_rank_nodes')
def rank_nodes():
    if not graphfile.graph.data_exists():
        graphfile.graph.add_data()
    color_measure = request.args.get("colorMeasure", None, type=str)
    size_measure = request.args.get('sizeMeasure', None, type=str)
    colors = request.args.get("colors", None, type=str)
    rankingWay = request.args.get('rankingWay', None, type=str)
    ranking = rank.Ranking(type=rankingWay, color_measure=color_measure,
                            size_measure=size_measure, cmap=colors,
                            initial_size=graphfile.image.image_style.node_size)
    graphfile.image.ranking_nodes_image(ranking)
    if(rankingWay == 'colorRanking' or rankingWay == 'bothRanking'):
        URLS = [graphfile.image.url, graphfile.image.ranking.colorbase]
    else:
        URLS = [graphfile.image.url]
    return Response(json.dumps(URLS))

@app.route('/diagrams')
def diagrams():
    if(not graphfile.graph.data_exists()):
        graphfile.graph.add_data()
    return render_template('diagrams.html',
                           graphtype = graphfile.graph.graphtype,
                           is_weighted=graphfile.graph.is_weighted,
                           growing=graphfile.graph.growing)

@app.route('/_create_diagram')
def create_diagram():
    diagram_type = request.args.get('diagram', None, type = str)
    diag = diagram.Diagram(diagram_type)
    average_values = graphfile.graph.get_average_values(diagram_type)
    json_obj = {}
    json_obj['url'] = diag.url
    json_obj['average'] = average_values
    return Response(json.dumps(json_obj))

@app.route("/open_project", methods= ['GET','POST'])
def open_project():
    if(not session['login']):
        return redirect(url_for('mainpage'))
    projectname = request.form['project']
    user = user_admin.UserAdministrator(session['user'])
    global graphfile
    graphfile = user.import_existing_project(projectname)
    if(graphfile.graph.graphtype == "Directed"):
        session['undirected'] = False
    else:
        session['undirected'] = True
    session['showimage'] = True 
    return redirect(url_for('graph'))


@app.route('/random_graph', methods= ['GET','POST'])
def random_graph():
    if not session['login']:
        return redirect(url_for('mainpage'))
    parameters = request.form
    global graphfile
    r_graph = g.Graphs(parameters, 'random', False)
    user = user_admin.UserAdministrator(session['user'])
    graphfile = user.create_temp_project(r_graph)
    if(graphfile.graph.graphtype == "Directed"):
        session['undirected'] = False
    else:
        session['undirected'] = True
    image_style = g_image.ImageStyle()
    image = g_image.GraphImage(image_style)
    session['showimage'] = True 
    return redirect(url_for('graph'))

@app.route('/add_node', methods=['GET', 'POST'])
def add_node():
    global graphfile
    returned_data = graphfile.graph.add_new_node_barabasi_model()
    graphfile.graph.graph = returned_data[0]
    new_edges = " ".join(str(x) for x in returned_data[1])
    graphfile.graph.set_node_pos()
    graphfile.graph.initialize_graph_characteristics()
    image_style = g_image.ImageStyle()
    image = g_image.GraphImage(image_style)
    return redirect(url_for('dynamic_graph', edges=new_edges))

@app.route("/dynamic_graph")
def dynamic_graph():
    edges = request.args['edges']
    return render_template("index.html", name =  graphfile.graph.graphtype,
                            number_of_nodes = graphfile.graph.number_of_nodes,
                            nodes = graphfile.graph.graph.nodes(),
                            edges = graphfile.graph.number_of_edges,
                            is_weighted = graphfile.graph.is_weighted,
                            url = graphfile.image.url,
                            diameter = graphfile.graph.diameter,
                            negative_cycle = graphfile.graph.negative_cycle,
                            average = graphfile.graph.average_shortest_path_length,
                            number = graphfile.graph.number_of_shortest_paths,
                            negative_weights = graphfile.graph.has_negative_weights,
                            density = graphfile.graph.density, is_DAG = graphfile.graph.is_DAG,
                            is_connected = graphfile.graph.is_connected,
                            growing = graphfile.graph.growing,
                            new_edges = edges)

@app.route("/delete_node", methods=["GET", "POST"])
def delete_node():
    global graphfile
    graphfile.graph.graph = graphfile.graph.delete_node()
    graphfile.graph.set_node_pos()
    graphfile.graph.initialize_graph_characteristics()
    image_style = g_image.ImageStyle()
    g_image.GraphImage(image_style)
    return redirect(url_for('graph'))
 
@app.route("/_save_project")
def save_project():
    if not graphfile.graph.data_exists():
        graphfile.graph.add_data()
    projectname = request.args.get("project", None, type = str)
    save = request.args.get("saveAction", None, type = bool)
    user = user_admin.UserAdministrator(session['user'])
    completion = user.save_project(projectname, save)
    if(completion):
        return Response(json.dumps(True))
    else:
        return Response(json.dumps(False))

@app.route('/_delete_project')
def delete_project():
    projectname = request.args.get('project', None, type = str)
    user = user_admin.UserAdministrator(session['user']) 
    user.delete_project(projectname)
    return jsonify()

@app.route('/dialog')
def dialog_window():
    if(not session['login']):
        return redirect(url_for('mainpage'))
    return render_template('dialog.html')


@app.route('/projects')
def projects():
    user = user_admin.UserAdministrator(session['user'])
    projects = user.get_existing_projects()
    return render_template('select_project.html', projects = projects)

@app.route('/_dynamic_analysis')
def dynamic_analysis():
    time = request.args.get('time', 1, type=int)
    url = diagram.Diagram.degree_over_time(time)
    json_obj = {'degree' : url[0], 'pathInTime': url[1]}
    return Response(json.dumps(json_obj))

@app.route('/download_node_info')
def download_node_info():
    def download():
        info = graphfile.graph.get_node_data()
        data = StringIO.StringIO()
        w = csv.writer(data)
        if graphfile.graph.graph.is_directed():
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
    def download():
        info = graphfile.graph.get_edge_data()
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
    image = graphfile.image.url.split(",")[1]
    image_output = StringIO.StringIO()
    image_output.write(decodestring(image))   # Write decoded image to buffer
    image_output.seek(0)
    headers = Headers()
    headers.add('Content-Disposition', 'attachment', filename='graph_img.png')
    return Response(
        image_output,
        mimetype='image/png',
        headers=headers
    )
@app.route('/download_diagram')
def download_diagram():
    diagram = request.form['diagram']
    image_output = StringIO.StringIO()
    image_output.write(decodestring(diagram))   # Write decoded image to buffer
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
    def download():
        info = graphfile.graph.get_graph_txtformat()
        data = StringIO.StringIO()
        for row in info:
            if graphfile.graph.is_weighted:
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

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def page_not_found(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
