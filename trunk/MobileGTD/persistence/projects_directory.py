from inout.io import *
from model.project import Project
from project_file import *
def is_project(path):
    return os.path.splitext(path)[1]=='.prj'



class ProjectsDirectory:
    def __init__(self,projects,directory):
        self.projects = projects
        self.directory = directory

    def read(self):
        for f in list_dir(self.directory,recursive=False,filter=is_project):
            name = project_name(f)
            print name
            self.projects.append(Project(name))
        