"""
This module contains all required information associated with a user of system.
Implements operations associated with the account of a user.

Some examples are:
Graph save to their profile, graph deletion, addition of a user to datastore,
search for a user in datastore, etc.
"""
__author__ = 'Thodoris Sotiropoulos'

from google.appengine.ext import db
from mvc.model import application_model as model


class User:
    """
    A class that represents user which is registered to the system. Not a guest
    user.

    User who is registered to the system he has to give his credentials
    (username and password) to enter system.

    User class needs data that are stored database for many operations.

    For example, to check if credentials given by user during login operation are
    right, it is needed to check database if a user matching these credentials
    exists.

    """

    def __init__(self, username='', password="", first_name='', last_name='',
                 email=''):
        """
        Initializes User object.

        :param username: Username of user.
        :param password: Password of user to enter system.
        :param first_name: First name of user.
        :param last_name: Surname of user.
        :param email: email of user.

        """
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def check_credentials(self):
        """
        Checks database if a user with credentials specified in object given as
        parameter exists. This method is for the login operation and it tests
        the password and username of a user.

        If there is no record in database with username and password which are
        the same with the corresponding fields of user objects then false is
        returned, true otherwise.

        :return: Message according to the result of search.
        """
        user = db.Query(model.User).filter('username =', self.username)
        if user.count() == 0:
            message = 'Invalid username'
        elif user.get().password != self.password:
            message = 'Invalid password'
        else:
            message = None
        return message

    def user_exists(self, input_type):
        """
        Search database if a user exists as a criteria of input.

        Input might be email. Then checks database if a user exists with the given
        email class object and returns true if exists, false otherwise.

        Input might be username. Then checks database if a user exists with the
        given stored in class object given as parameter  and returns true if exists,
        false otherwise.

        Note: input parameter does not refer to the value of email or username,
        but defines if DAO has to search for a user with criteria of email or
        username.

        :param input_type: Type of input which defines the criteria which search
        will be based on. It can be either username or email.
        :return: true if user exists, false otherwise.
        """
        if input_type == 'username':
            user = db.Query(model.User).filter('username =', self.username)
        else:
            user = db.Query(model.User).filter('email =', self.email)
        exists = False
        if user.count() == 0:
            return exists
        else:
            exists = True
            return exists

    def add_user(self):
        """
        Add user specified on the parameter to database. If user is added, it
        is considered registered to the system and now he can enter system with
        the credentials given during his registration.

        :return: True if registration completed, False otherwise.
        """
        completion = False
        if db.Query(model.User).filter('username =', self.username).count() == 0:
            user = model.User(username=self.username, password=self.password,
                              firstName=self.first_name, lastName=self.last_name,
                              email=self.email)
            user.put()
            completion = True
        return completion

    def get_existing_projects(self):
        """
        Get all graphs that user has saved to the system.

        :return: Progress for all graph's analysis saved by user.
        """
        projects = db.Query(model.GraphFile).filter('user =', self.username)
        return projects

    def save_project(self, projectname, save, graphfile):
        """
        Save a progress of an analysis of a graph to the user's account
        in order to continue analysis other time.

        :param projectname: Name of project to be saved.
        :param save: True if save must be done obligingly, False otherwise.
        :param graphfile: Progress of analysis of a graph to be saved.
        :return: True if save has been completed, False otherwise.
        """
        query = db.Query(model.GraphFile).filter(
            'user = ', self.username).filter(
            'filename =', graphfile.filename).get()
        existing_projects = self.get_existing_projects()
        for pr in existing_projects:
            if pr.filename == projectname and not save:
                return False
        self.delete_project(projectname)
        project = model.GraphFile(user=self.username,
                                  filename=projectname,
                                  data=query.data,
                                  graphtype=graphfile.graph.graphtype,
                                  image=graphfile.image,
                                  graph=graphfile.graph)

        project.put()
        return True

    def create_temp_project(self, graph):
        """
        Saves progress of an analysis of a graph temporarily for the current
        analysis of a user.

        This progress is going to be deleted unless user saves progress with
        a name for analyzing later.

        :param graph: Graph instance to be saved.
        :return: Progress of graph analysis.
        """
        temp_graphs = db.Query(model.GraphFile).filter(
            "user =", self.username).filter("filename =",
                                            "file.txt")
        if temp_graphs.count() == 0:
            temp_graph = model.GraphFile(user=self.username,
                                         filename="file.txt",
                                         graph=graph)
            temp_graph.put()
            return temp_graph
        else:
            return temp_graphs.get()

    def import_existing_project(self, projectname):
        """
        Gets an existing progress of analysis of a graph that user has already
        saved.

        :param projectname: Name of progress to import.
        :return: Progress of graph analysis.
        """
        project = db.Query(model.GraphFile).filter(
            'user = ', self.username).filter("filename =",
                                             projectname).get()
        return project

    def delete_project(self, projectname):
        """
        Deleted an existing progress of analysis of a graph that user has already
        saved.

        :param projectname: Name of progress to import.
        """
        project = db.Query(model.GraphFile).filter(
            'user = ', self.username).filter("filename =",
                                             projectname)
        if project.count() != 0:
            db.delete(project)