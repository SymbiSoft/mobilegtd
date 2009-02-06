from inout.io import *
from model.project import Project
from project_file import ProjectFile
import project_file
def is_project(path):
    return os.path.splitext(path)[1]=='.prj'



class ProjectsDirectory:
    def __init__(self,projects,directory):
        self.projects = projects
        self.projects.observers.append(self)
        self.directory = directory

    def read(self):
        for f in list_dir(self.directory,recursive=True,filter=is_project):
            p = project_file.read(f)
            self.projects.append(p)

    def notify(self,projects,attribute,new=None,old=None):
        ProjectFile(new) 