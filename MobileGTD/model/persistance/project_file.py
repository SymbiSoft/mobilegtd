import re,os
from model.model import *

file_name_regexp = re.compile('/?(?P<path>.*/)*(?P<file_name>.*)\....',re.U)

project_dir_status_map = {u'Done':done,u'Review':inactive,u'Someday':someday,u'Tickled':tickled}
status_project_dir_map = invert_dictionary(project_dir_status_map)


class ProjectFile(WriteableItem):
    def __init__(self,project):
        self.project = project

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
        if status in status_project_dir_map:
            return '@'+status_project_dir_map[status]
        return ''
        
    def notify(self,project,attribute,value):
        if attribute == 'status':
            self.move_to(self.directory_for_status(value))
        else:
            self.rename(value)
    def file_string(self):
        lines = []
        for info in self.project.infos:
            lines.append(info.file_string())
#        self.sort_actions()
        for action in self.project.actions:
            lines.append(action.project_file_string())
        return u'\n'.join(lines) 
