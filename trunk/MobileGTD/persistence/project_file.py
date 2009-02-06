import re,os
from inout.io import parse_file_to_line_list
from model.project import *
from model.model import invert_dictionary,WriteableItem
from action_file import ActionFile




projects_dir = '@Projects'

def project_name(file_name):
    return os.path.splitext(os.path.basename(file_name))[0]


class ProjectFileCreator(object):
    
    def notify(self,project_class,attribute,new=None,old=None):
        ProjectFile(new)
    
    def __eq__(self,other):
        return type(other) == ProjectFileCreator

#Project.observers.append(ProjectFileCreator())


def status_for_dir(dir_name):
    p,last_part_of_path = os.path.split(dir_name)
#    print last_part_of_path
    if last_part_of_path == '.' or last_part_of_path == '@Projects':
        return active   
    if last_part_of_path[0] == '@':
        return ProjectStatus.get_status_for_name(last_part_of_path[1:].lower())
    raise "Invalid path"

def read(file_path):
    file_name = os.path.basename(file_path)
    name = project_name(file_name)
    project = Project(name,status_for_dir(os.path.dirname(file_path)))
    file_content = parse_file_to_line_list(file_path)
    actions,infos = parse_lines(file_content)
    for a in actions:
        project.add_action(a)
        # Need to do this by hand because project has not yet been registered with Projects
        append_action_file_observer(a)
    for info in infos:    
        project.add_info(info)
    return project

def parse_lines(lines):
    actions = []
    infos = []
    for line in lines:
        if len(line) < 3:
            continue
        elif line[0]=='#':
            infos.append(Info(line[1:].strip()))
        else:
            actions.append(Action.parse(line))
    return (actions,infos)



def append_action_file_observer(a):
    a.observers.append(ActionFile(a))


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
        if status_string != 'Active':
            return os.path.join(projects_dir,'@'+status_string)
        return projects_dir
        
    def notify(self,project,attribute,new=None,old=None):
        if attribute == 'status':
            self.move_to(self.directory_for_status(new),self.directory_for_status(old))
        elif attribute == 'name':
            self.rename(new)
        elif attribute == 'add_action':
            append_action_file_observer(new)
            super(ProjectFile,self).notify(project,attribute,new=new,old=old)
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

    
