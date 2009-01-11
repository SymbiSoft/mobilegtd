import re,os
from model.project import *
from model.model import invert_dictionary,WriteableItem


project_dir_status_map = {u'Done':done,u'Review':inactive,u'Someday':someday,u'Tickled':tickled}
status_project_dir_map = invert_dictionary(project_dir_status_map)

def project_name(file_name):
    return os.path.splitext(os.path.basename(file_name))[0]

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
            return '@'+status_string
        return ''
        
    def notify(self,project,attribute,new=None,old=None):
        if attribute == 'status':
            self.move_to(self.directory_for_status(new),self.directory_for_status(old))
        elif attribute == 'name':
            self.rename(new)
        else:
            self.write()
    
    def file_string(self):
        lines = []
        for info in self.project.infos:
            lines.append(info.file_string())
#        self.sort_actions()
        for action in self.project.actions:
            lines.append(action.project_file_string())
        return u'\n'.join(lines) 

    def read(file_path):
        file_name = os.path.basename(file_path)
        name = project_name(file_name)
        project = Project(name,inactive)
        project_file = ProjectFile(project)
#        project.observers.append()
        file_content = parse_file_to_line_list(file_path)
        actions,infos = parse_lines(file_content)
        for action in actions:
            project.add_action(action)
        
        for info in infos:    
            project.add_info(info)
        return project


    read = staticmethod(read)