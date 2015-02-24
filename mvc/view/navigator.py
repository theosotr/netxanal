"""
This module contains request handler functions that allow user to navigate
through the system. There are five pages where can
visit.

First page is the one which user visit first. It contains forms for user to import
a graph with three ways:
--By uploading a graph file.
--By generating a random graph based on a mathematical model.
--By import a graph which he has saved in datastore.

Second page is the page with the visualization of graph. Third page is the one
shows the list of node and edge information, the fourth one allow user to see
frequency diagrams for node measures such as degree centrality, pagerank,
clustering coefficient.

The last one is a page where a user who is not connected can enter system with
their credentials. Moreover, unregistered users can create a new account to use
system.
"""
__author__ = 'Thodoris Sotiropoulos'

from mvc.controller import graphfile as current_graph
from flask import render_template, session, redirect, url_for
from main import app
from mvc.model.application_model import delete_data
from mvc.model.user_model import User


@app.route('/')
def index():
    """
    Go to the page when a user who is not connected or registered to the system
    first visit. Contains login and registration forms to enter system.

    """
    session["showimage"] = False
    return render_template("login.html")


@app.route('/graph', methods=['GET', 'POST'])
def graph():
    """
    Go the page of visualization of graph. It also returns all required
    information about graph such as the list of nodes, if it is weighted,
    if it is a DAG, measures(density), etc.

    """
    user_graph = current_graph.graphfile[session['user']]
    return render_template("index.html", name=user_graph.graph.graphtype,
                           number_of_nodes=user_graph.graph.number_of_nodes,
                           nodes=user_graph.graph.graph.nodes(),
                           edges=user_graph.graph.number_of_edges,
                           is_weighted=user_graph.graph.is_weighted,
                           url=user_graph.image.url,
                           negative_cycle=user_graph.graph.negative_cycle,
                           negative_weights=user_graph.graph.has_negative_weights,
                           density=user_graph.graph.density,
                           is_DAG=user_graph.graph.is_DAG,
                           is_connected=user_graph.graph.is_connected,
                           diameter=user_graph.graph.diameter,
                           average_path=user_graph.graph.average_shortest_path_length,
                           growing=user_graph.graph.growing)


@app.route('/diagrams')
def diagrams():
    """
    Go to the page of frequency diagrams. It also returns all required information
    about graph such if it is a growing graph, if it is weighted, its type.

    """
    user_graph = current_graph.graphfile[session['user']]
    if not user_graph.graph.data_exists():
        user_graph.graph.add_data()
    return render_template('diagrams.html',
                           graphtype=user_graph.graph.graphtype,
                           is_weighted=user_graph.graph.is_weighted,
                           growing=user_graph.graph.growing)


@app.route("/node_info")
def node_info():
    """
    Go the page with the list of edge and node information.
    It gets all required information associated with both nodes and edges of
    graph.

    Edge information includes:
    -- Edge's source node
    -- Edge's target
    -- Betweenness centrality
    -- Edge weight for weighted graphs).

    Node information information includes:
    -- Degree centrality and In/Out-degree centrality for directed graphs
    -- Clustering coefficient for undirected graphs
    -- Pagerank for directed graphs
    -- Betweeness centrality,
    -- Closeness centrality,
    -- Eigenvector centrality,
    -- Connected Components

    """
    if not session['login']:
        return redirect(url_for('index'))
    user_graph = current_graph.graphfile[session['user']]
    if not user_graph.graph.data_exists():
        user_graph.graph.add_data()
    if user_graph.graph.graphtype == 'Directed':
        return render_template("graph_info.html",
                               graph=user_graph.graph.graph,
                               is_weighted=user_graph.graph.is_weighted)
    else:
        return render_template("graph_info.html",
                               graph=user_graph.graph.graph,
                               is_weighted=user_graph.graph.is_weighted)


@app.route("/import_file", methods=['GET', 'POST'])
def import_file():
    """
    Go to the page which allows which allows user to import graph with the
    following ways:
    -- By uploading a graph file.
    -- By generating a random graph based on a mathematical model.
    -- By import a graph which he has saved in datastore.

    """
    if not session['login']:
        return redirect(url_for('index'))
    current_graph.graphfile.pop(session['user'], None)
    session["showimage"] = False
    delete_data()
    return redirect(url_for('mainpage'))


@app.route('/mainpage', defaults={'warning': False})
@app.route('/mainpage/<warning>')
def mainpage(warning):
    user = User(session['user'])
    projects = user.get_existing_projects()
    return render_template('index.html', projects=projects, wrong_file=warning)