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
        except:
            pass
        return super(ObjectProperty, self).make_value_from_datastore(value)


class directed_graph_info(db.Model):
    node = db.StringProperty()
    in_degree = db.FloatProperty()
    out_degree = db.FloatProperty()
    weighted_in_degree = db.FloatProperty()
    weighted_out_degree = db.FloatProperty()
    closeness_centrality = db.FloatProperty()
    betweeness_centrality = db.FloatProperty()
    eigenvector_centrality = db.FloatProperty()
    pagerank = db.FloatProperty()
    modularity = db.IntegerProperty()
    weak_components = db.StringProperty()
    strong_components = db.StringProperty()
    user = db.StringProperty()
    project = db.StringProperty()
    
    
class undirected_graph_info(db.Model):
    node = db.StringProperty()
    degree = db.FloatProperty()
    weighted_degree = db.FloatProperty()
    closeness_centrality = db.FloatProperty()
    betweeness_centrality = db.FloatProperty()
    eigenvector_centrality = db.FloatProperty()
    clustering = db.FloatProperty()
    modularity = db.IntegerProperty()
    connected_components = db.StringProperty()
    user = db.StringProperty()
    project = db.StringProperty()


class AverageMetricsUndirected(db.Model):
    average_degree = db.FloatProperty()
    average_betweeness = db.FloatProperty()
    average_closeness = db.FloatProperty()
    average_eigenvector = db.FloatProperty()
    average_clustering = db.FloatProperty()
    average_w_degree = db.FloatProperty()
    user = db.StringProperty()
    project = db.StringProperty()


class AverageMetricsDirected(db.Model):
    average_in_degree = db.FloatProperty()
    average_out_degree = db.FloatProperty()
    average_betweeness = db.FloatProperty()
    average_closeness = db.FloatProperty()
    average_eigenvector = db.FloatProperty()
    average_pagerank = db.FloatProperty()
    average_w_in_degree = db.FloatProperty()
    average_w_out_degree = db.FloatProperty()
    user = db.StringProperty()
    project = db.StringProperty()


class AverageEdgeMetrics(db.Model):
    averageWeight = db.FloatProperty()
    averageBetweenness = db.FloatProperty()
    user = db.StringProperty()
    project = db.StringProperty()


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


def delete_data():
    query1 = db.Query(directed_graph_info).filter(
                    'user =', session['user']).filter('project =','file.txt')
    query2 = db.Query(undirected_graph_info).filter(
                    'user =', session['user']).filter('project =','file.txt')
    query4 = db.Query(GraphFile).filter('user =', session['user']).filter(
                                        'filename =','file.txt')
    query7 = db.Query(AverageMetricsUndirected).filter(
                    'user =', session['user']).filter('project =','file.txt')
    query8 = db.Query(AverageMetricsDirected).filter(
                    'user =', session['user']).filter('project =','file.txt')
    query3 = db.Query(AverageEdgeMetrics).filter(
                    'user =', session['user']).filter('project =','file.txt')
    list1 = query1.fetch(limit=10000)
    list2 = query2.fetch(limit = 10000)
    list4 = query4.fetch(limit = 10000)
    list7 = query7.fetch(limit = 10000)
    list8 = query8.fetch(limit = 10000)
    list3 = query3.fetch(limit = 10000)
    db.delete(list1)
    db.delete(list2)
    db.delete(list4)  
    db.delete(list7)
    db.delete(list8)
    db.delete(list3)
