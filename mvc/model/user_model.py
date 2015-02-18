from google.appengine.ext import db
from mvc.model import application_model as model


class UserAdministrator:
    def __init__(self, username='', password="", first_name='', last_name='',
                 email=''):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def check_credentials(self):
        user = db.Query(model.User).filter('username =', self.username)
        if user.count() == 0:
            message = 'Invalid username'
        elif user.get().password != self.password:
            message = 'Invalid password'
        else:
            message = None
        return message

    def user_exists(self, input_type):
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
        completion = False
        if db.Query(model.User).filter('username =', self.username).count() == 0:
            user = model.User(username=self.username, password=self.password,
                              firstName=self.first_name, lastName=self.last_name,
                              email=self.email)
            user.put()
            completion = True
        return completion

    def get_existing_projects(self):
        projects = db.Query(model.GraphFile).filter('user =', self.username)

        return projects

    def save_project(self, projectname, save, graphfile):
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
        project = db.Query(model.GraphFile).filter(
            'user = ', self.username).filter("filename =",
                                             projectname).get()
        return project

    def delete_project(self, projectname):
        project = db.Query(model.GraphFile).filter(
            'user = ', self.username).filter("filename =",
                                             projectname)
        if project.count() != 0:
            db.delete(project)