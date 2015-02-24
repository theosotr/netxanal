"""
This module contains classes that represent entities of the database of
application.
"""
__author__ = 'Thodoris Sotiropoulos'


from google.appengine.ext import db
import pickle
from flask import session


class ObjectProperty(db.BlobProperty):
    def validate(self, value):
        try:
            result = pickle.dumps(value)
            return value
        except pickle.PicklingError, e:
            return super(ObjectProperty, self).validate(value)

    def get_value_for_datastore(self, model_instance):
        result = super(ObjectProperty, self).get_value_for_datastore(model_instance)
        result = pickle.dumps(result)
        return db.Blob(result)

    def make_value_from_datastore(self, value):
        try:
            value = pickle.loads(str(value))
        except Exception:
            pass
        return super(ObjectProperty, self).make_value_from_datastore(value)


class GraphFile(db.Model):
    """
    This class represents a graph which user analyze.

    Attributes:
    user: User who analyze graph.
    filename: Name of analysis progress.
    graphtype: Type of graph, Directed or Undirected.
    image: Encoded String for graph visualization based on base64 encoding.
    graph: Graph object to be analyzed.
    """
    user = db.StringProperty()
    filename = db.StringProperty()
    data = db.BlobProperty()
    graphtype = db.StringProperty()
    image = ObjectProperty()
    graph = ObjectProperty()


class User(db.Model):
    """
    A class that represents user which is registered to the system. Not a guest
    user.

    User who is registered to the system he has to give his credentials
    (username and password) to enter system.

    Attributes:
    username: Username of user.
    password: Password of user.
    firstName: First name of user.
    lastName: Surname of user.
    email: email of user.
    """
    username = db.StringProperty()
    password = db.StringProperty()
    firstName = db.StringProperty()
    lastName = db.StringProperty()
    email = db.StringProperty()


def delete_data():
    """
    Deletes temporary progress of a graph which a user analyze when user wants
    to import a new graph or to logout.
    """
    query4 = db.Query(GraphFile).filter('user =', session['user']).filter(
        'filename =', 'file.txt')
    list4 = query4.fetch(limit=10000)
    db.delete(list4)
