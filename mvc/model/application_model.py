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
    user = db.StringProperty()
    filename = db.StringProperty()
    data = db.BlobProperty()
    graphtype = db.StringProperty()
    image = ObjectProperty()
    graph = ObjectProperty()


class User(db.Model):
    username = db.StringProperty()
    password = db.StringProperty()
    firstName = db.StringProperty()
    lastName = db.StringProperty()
    email = db.StringProperty()


def delete_data():
    query4 = db.Query(GraphFile).filter('user =', session['user']).filter(
        'filename =', 'file.txt')
    list4 = query4.fetch(limit=10000)
    db.delete(list4)
