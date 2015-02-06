__author__ = 'Thodoris Sotiropoulos'

from flask import session, request, render_template, redirect, url_for, jsonify, Response
import UserAdministrator as user_admin
import json
from ApplicationModel import delete_data
from handler import app


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = user_admin.UserAdministrator(username, password)
    message = user.check_credentials()
    if message is None:
        global current_user
        session['login'] = True
        session['showimage'] = False
        session['user'] = username
        current_user = username
        projects = user.get_existing_projects()
        return render_template('index.html', projects=projects)
    else:
        return render_template('login.html', message=message)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    delete_data()
    global current_user
    session['user'] = None
    current_user = None
    session['showimage'] = False
    session['login'] = False
    return redirect(url_for('mainpage'))


@app.route('/_check_user')
def check_username():
    username = request.args.get('username', None, type=str)
    user = user_admin.UserAdministrator(username, '')
    if not user.user_exists():
        if len(username) > 3:
            return Response(json.dumps('Your username is accepted!'))
        else:
            return Response(json.dumps('Username must have at least 3 characters'))
    else:
        return Response(json.dumps('Username already exists!'))


@app.route('/_new_account', methods=['GET', 'POST'])
def new_account():
    username = request.args.get('username', None, type=str)
    password = request.args.get('password', None, type=str)
    user = user_admin.UserAdministrator(username, password)
    user.add_user()
    return jsonify()
