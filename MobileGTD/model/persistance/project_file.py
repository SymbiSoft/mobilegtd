import re,os
from model.model import *


class ProjectFile(WriteableItem):
    def __init__(self,project):
        self.project = project

    def path(self):
        if self.project.status == inactive:
            return os.path.join('@Review',self.project.name+'.prj')
        return self.project.name+'.prj'