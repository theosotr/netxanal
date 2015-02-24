"""
This module contains all request handlers which
are associated with the enter of user to application.

For example, there are functions for registration requests,
 request to enter system, and request to logout.

"""
__author__ = 'Thodoris Sotiropoulos'

import json

from flask import session, request, redirect, url_for, Response
from mvc.model.user_model import User
from mvc.model.application_model import delete_data
from main import app
from mvc.controller.graphfile import graphfile


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Request handler for login operation. It takes two parameters.
    First one is username and the second one is password. Then it searches
    database if a user with the given credentials exists. If user exists, go to the
    main page of application, otherwise go to the page with the login form and a
    message that wrong credentials were given is returned.

    :return: Page to forward accodring to the existence of user.
    """
    username = request.form['username']
    password = request.form['password']
    user = User(username, password)
    message = user.check_credentials()
    if message is None:
        session.pop('warningMessage', None)
        session['login'] = True
        session['showimage'] = False
        session['user'] = username
        return redirect(url_for('mainpage'))
    else:
        session['warningMessage'] = message
        return redirect(url_for('index'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    Request of user to logout system. Removes all sessions associated with the user.

    :return: Page with the login form.
    """
    graphfile.pop(session['user'], None)
    delete_data()
    session['user'] = None
    session['showimage'] = False
    session['login'] = False
    return redirect(url_for('index'))


@app.route('/_check_user')
def check_username():
    """
    A request handler function that takes as username as parameters
    and it looks if a user with the username given as parameter exists.
    If user exists, then returns message to user accordingly.

    It is implemented via AJAX and when a user types a username in the
    corresponding field of registration form, then client sends a request
    to this function to check if a user with the same username as the one
    given by user who wants to register system in order to warn user that there
    is already a user with this username.

    :return: Message to user, if username is accepted or not.
    """
    input_value = request.args.get('value', None, type=str)
    input_type = request.args.get('inputType', None, type=str)
    if input_type == 'username':
        user = User(username=input_value)
    else:
        user = User(email=input_value)
    if not user.user_exists(input_type):
        return Response(json.dumps('Your ' + input_type + ' is accepted!'))
    else:
        return Response(json.dumps(input_type + ' already exists!'))


@app.route('/_new_account', methods=['GET', 'POST'])
def new_account():
    """ A new user is added to the system. """
    username = request.args.get('username', None, type=str)
    password = request.args.get('password', None, type=str)
    first_name = request.args.get('name', None, type=str)
    last_name = request.args.get('lastName', None, type=str)
    email = request.args.get('email', None, type=str)
    user = User(username, password, first_name, last_name, email)
    user.add_user()
    return Response(json.dumps('Your registration completed!'))
