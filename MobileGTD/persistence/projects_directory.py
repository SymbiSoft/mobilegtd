from inout.io import *
from model.project import Project
from project_file import ProjectFile
import project_file
from log.logging import logger
def is_project(path):
    return os.path.splitext(path)[1]=='.prj'



class ProjectsDirectory:
    def __init__(self,projects):
        self.projects = projects
        self.projects.observers.append(self)
        self.projects.reread = self.read
        self.directories = {}
        self.num_elements = 0
    
    def add_directory(self,directory,recursive = False):
        self.directories[directory] = recursive

    def read(self):
        for p in range(0,self.num_elements):
            self.projects.pop()
            self.num_elements -= 1
        for directory,recursive in self.directories.items():
            self.read_directory(directory,recursive)

    def read_directory(self,directory,recursive=False):
        for f in list_dir(directory,recursive=recursive,filter=is_project):
            
            p,actions,infos = project_file.read(f)
#            if not p in self.projects:
            self.projects.append(p)
            self.num_elements += 1
            logger.log(u'Read project %s, actions %s, infos %s'%(p,actions,infos))
            for a in actions:
                p.add_action(a)
            for info in infos:    
                p.add_info(info)
            logger.log(u'Result %s'%repr(p))

    def notify(self,projects,attribute,new=None,old=None):
        logger.log(u"ProjectsDirectory notified of %s | %s | %s"%(repr(projects),repr(attribute),repr(new)))
        if attribute == 'add_item':
            new.observers.append(ProjectFile(new)) 