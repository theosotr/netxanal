"""
This module contains request handler functions for the graph-project
manipulation from user.

This includes actions such as project addition and deletion as well as
display of project which are already saved by user.

"""
__author__ = 'Thodoris Sotiropoulos'

import json

from mvc.controller import graphfile as current_graph
from flask import request, Response, session, jsonify, render_template
from main import app
from mvc.model.user_model import User


@app.route("/_save_project")
def save_project():
    """
    Saves current graph to the datastore in order user can analyze it another
    time. It requires a name to save graph with that name. If graph with the
    given is already existed in the list of saved graphs of user,
    saving completion cannot be done unless user wants to overwrite existing
    graph.

    :return: Returns in JSON format if graph saving was completed or not.

    """
    graph = current_graph.graphfile[session['user']]
    if not graph.graph.data_exists():
        graph.graph.add_data()
    projectname = request.args.get("project", None, type=str)
    save = request.args.get("saveAction", None, type=bool)
    user = User(session['user'])
    completion = user.save_project(projectname, save, graph)
    if completion:
        return Response(json.dumps(True))
    else:
        return Response(json.dumps(False))


@app.route('/_delete_project')
def delete_project():
    """ Deletes a specific graph from the list of saved graphs of user. """
    projectname = request.args.get('project', None, type=str)
    user = User(session['user'])
    user.delete_project(projectname)
    return jsonify()


@app.route('/projects')
def projects():
    """ Gets the list of saved graph of user. """
    user = User(session['user'])
    projectlist = user.get_existing_projects()
    return render_template('dialogs.html', projects=projectlist)
