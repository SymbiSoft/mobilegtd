import re,os
from inout.io import parse_file_to_line_list
from model.project import *
from model.model import invert_dictionary,WriteableItem
from action_file import ActionFile

project_dir_status_map = {u'Done':done,u'Review':inactive,u'Someday':someday,u'Tickled':tickled}
status_project_dir_map = invert_dictionary(project_dir_status_map)


projects_dir = '@Projects'

def project_name(file_name):
    return os.path.splitext(os.path.basename(file_name))[0]


class ProjectFileCreator(object):
    
    def notify(self,project_class,attribute,new=None,old=None):
        ProjectFile(new)
    
    def __eq__(self,other):
        return type(other) == ProjectFileCreator

#Project.observers.append(ProjectFileCreator())



def read(file_path):
    file_name = os.path.basename(file_path)
    name = project_name(file_name)
    project = Project(name,inactive)
    file_content = parse_file_to_line_list(file_path)
    actions,infos = parse_lines(file_content)
    for action in actions:
        project.add_action(action)
        action.observers.append(ActionFile(action))
    
    for info in infos:    
        project.add_info(info)
    return project


class ProjectFile(WriteableItem):
    def __init__(self,project):
        self.project = project
        project.observers.append(self)

    def path(self):
        return self.path_for_status(self.project.status)

    def project_file_name(self):
        return self.project.name+'.prj'

    def path_for_status(self,status):
        directory = self.directory_for_status(status)
        if len(directory) > 0:
            return os.path.join(directory,self.project_file_name())
        else:
            return self.project_file_name()

    def directory_for_status(self,status):
        status_string = status.name.capitalize()
        if len(status_string) > 0:
            return os.path.join(projects_dir,'@'+status_string)
        return projects_dir
        
    def notify(self,project,attribute,new=None,old=None):
        if attribute == 'status':
            self.move_to(self.directory_for_status(new),self.directory_for_status(old))
        elif attribute == 'name':
            self.rename(new)
        else:
            super(ProjectFile,self).notify(project,attribute,new=new,old=old)
    
    def file_string(self):
        lines = []
        for info in self.project.infos:
            lines.append(info.file_string())
#        self.sort_actions()
        for action in self.project.actions:
            lines.append(action.project_file_string())
        return u'\n'.join(lines) 

    
