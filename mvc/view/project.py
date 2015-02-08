"""
This module contains request handler functions for the graph-project
manipulation from user.

This includes actions such as project addition and deletion as well as
display of project which are already saved by user.

"""
from mvc.controller import graphfile as current_graph

__author__ = 'Thodoris Sotiropoulos'

import json

from flask import request, Response, session, jsonify, render_template
from main import app
from UserAdministrator import UserAdministrator


@app.route("/_save_project")
def save_project():
    """
    Takes a name
    :return:
    """
    graph = current_graph.graphfile[session['user']]
    if not graph.graph.data_exists():
        graph.graph.add_data()
    projectname = request.args.get("project", None, type=str)
    save = request.args.get("saveAction", None, type=bool)
    user = UserAdministrator(session['user'])
    completion = user.save_project(projectname, save, graph)
    if completion:
        return Response(json.dumps(True))
    else:
        return Response(json.dumps(False))


@app.route('/_delete_project')
def delete_project():
    projectname = request.args.get('project', None, type=str)
    user = UserAdministrator(session['user'])
    user.delete_project(projectname)
    return jsonify()


@app.route('/projects')
def projects():
    user = UserAdministrator(session['user'])
    projectlist = user.get_existing_projects()
    return render_template('select_project.html', projects=projectlist)
