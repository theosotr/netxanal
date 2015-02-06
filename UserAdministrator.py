import handler as hand
import ApplicationModel as model
from google.appengine.ext import db


class UserAdministrator:
    def __init__(self, username, password=""):
        self.username = username
        self.password = password


    def check_credentials(self):
        user = db.Query(model.User).filter('username =', self.username)
        if (user.count() == 0):
            message = 'Invalid username'
        elif (user.get().password != self.password):
            message = 'Invalid password'
        else:
            message = None
        return message

    def user_exists(self):
        user = db.Query(model.User).filter('username =', self.username)
        exists = False
        if (user.count() == 0):
            return exists
        else:
            exists = True
            return exists

    def add_user(self):
        completion = False
        if (db.Query(model.User).filter('username =', self.username).count() == 0):
            user = model.User(username=self.username, password=self.password)
            user.put()
            completion = True
        return completion

    def get_existing_projects(self):
        projects = db.Query(model.GraphFile).filter('user =', self.username)

        return projects


    def update_data(self, projectname, graphtype):
        if (graphtype == 'Directed'):
            data = db.Query(model.directed_graph_info).filter(
                'user =', self.username).filter(
                'project =', hand.graphfile.filename)
            average_nodes = db.Query(model.AverageMetricsDirected).filter(
                'user =', self.username).filter(
                'project =', hand.graphfile.filename).get()
        else:
            data = db.Query(model.undirected_graph_info).filter(
                'user =', self.username).filter(
                'project =', hand.graphfile.filename)
            average_nodes = db.Query(model.AverageMetricsUndirected).filter(
                'user =', self.username).filter(
                'project =', hand.graphfile.filename).get()
        average_edges = db.Query(model.AverageEdgeMetrics).filter(
            'user =', self.username).filter(
            'project =', hand.graphfile.filename).get()
        for row in data:
            row.project = projectname
            row.put()
        average_nodes.project = projectname
        average_edges.project = projectname
        average_nodes.put()
        average_edges.put()

    def save_project(self, projectname, save):
        query = db.Query(model.GraphFile).filter(
            'user = ', self.username).filter(
            'filename =', hand.graphfile.filename).get()
        existing_projects = self.get_existing_projects()
        for pr in existing_projects:
            if (pr.filename == projectname and not save):
                return False
        self.delete_project(projectname)
        project = model.GraphFile(user=self.username,
                                  filename=projectname,
                                  data=query.data,
                                  graphtype=hand.graphfile.graph.graphtype,
                                  image=hand.graphfile.image,
                                  graph=hand.graphfile.graph)

        project.put()
        return True

    def create_temp_project(self, graph):
        temp_graphs = db.Query(model.GraphFile).filter(
            "user =", self.username).filter("filename =",
                                            "file.txt")
        if (temp_graphs.count() == 0):
            temp_graph = model.GraphFile(user=self.username,
                                         filename="file.txt",
                                         graph=graph)
            temp_graph.put()
            return temp_graph
        else:
            return temp_graphs.get()


    def import_existing_project(self, projectname):
        project = db.Query(model.GraphFile).filter(
            'user = ', self.username).filter("filename =",
                                             projectname).get()
        return project

    def delete_project(self, projectname):
        project = db.Query(model.GraphFile).filter(
            'user = ', self.username).filter("filename =",
                                             projectname)
        if (project.count() != 0):
            db.delete(project)