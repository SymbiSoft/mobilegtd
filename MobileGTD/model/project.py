from action import Action
from info import Info
from model import *
from inout.io import parse_file_to_line_list,u_join
import os,re
from observable import *

file_name_regexp = re.compile('/?(?P<path>.*/)*(?P<file_name>.*)\....',re.U)

project_dir_status_map = {u'Done':done,u'Review':inactive,u'Someday':someday,u'Tickled':tickled}
status_project_dir_map = invert_dictionary(project_dir_status_map)

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



class Project(ObservableItem,ItemWithStatus):
    def __init__(self,name):
        super(Project,self).__init__()
        ItemWithStatus.__init__(self)
        self.name=name
        self.actions=[]
        self.infos=[]
        
    def add_action(self,action):
        action.observers.append(self)
        self.actions.append(action)
        if action.status == active:
            self.status = active
        self.update_status()
        
    def remove_action(self,action):
        action.observers.remove(self)
        self.actions.remove(action)
        

    def update_status(self):
        for action in self.actions:
            if action.status == active:
                self.status = active

    def actions_with_status(self,status):
        result = []
        for action in self.actions:
            if action.status == status:
                result.append(action)
        return result
        

    def notify(self,action,attribute,value):
        if value == active:
            self.status = active
        else:
            active_actions = self.actions_with_status(active)
            if action in active_actions:
                active_actions.remove(action)
            if  len(active_actions) == 0:
                self.status = inactive
        
#        self.dirty = False
#        super(Project, self).__init__()
#        ##logger.log(u'Project %s is %s'%(self.name(),self.status))
#        #self.read()
#    def __eq__(self, project):
#        return self.path == project.path
#    def __ne__(self,project):
#        return not self.__eq__(project)
#    def read(self):
#        if not self.exists():
#            self.actions=[]
#            self.infos=[]
#        else:
#            action_strings = parse_file_to_line_list(self.path)
#            self.actions,self.infos = parse_lines(action_strings)
#            for action in self.actions:
#                action.project = self.name()
#
#    def file_string(self):
#        lines = []
#        for info in self.get_infos():
#            lines.append(info.file_string())
#        self.sort_actions()
#        for action in self.get_actions():
#            lines.append(action.project_file_string())
#        return u'\n'.join(lines) 
#
#    def write(self):
#        if self.dirty:
#            WriteableItem.write(self)
#            self.dirty = False
#    def sort_actions(self):
#        self.get_actions().sort()
#
#    def get_actions(self):
#        if self.actions == None:
#            self.read()
#        return self.actions
#    def get_infos(self):
#        if self.infos == None:
#            self.read()
#        return self.infos
#    def status_string(self):
#        if self.get_status() == active:
#            return u''
#        else:
#            return ItemWithStatus.status_string(self)
#    def name_with_status(self):
#        return self.status_string()+self.name() #+self.additional_info()
#    def additional_info(self):
#        # TODO
#        status_part=self.status_part_of_path()
#        if len(status_part)<=1:
#            return u''
#        else:
#            return u'/'.join(status_part[2:])
#    def name(self):
#        matching = file_name_regexp.match(self.path())
#        file_name=matching.group('file_name')
#        return file_name
#    def active_actions(self):
#        return filter(lambda action: action.is_active() ,self.get_actions())
#    def not_done_actions(self):
#        return filter(lambda action: action.is_not_done() ,self.get_actions())
#    def inactive_actions(self):
#        return filter(lambda action: not action.is_active() ,self.get_actions())
#    def add_action(self,action):
#        self.get_actions().append(action)
#        self.dirty = True
#    def add_info(self,info,position=None):
#        if position == None:
#            self.get_infos().append(info)
#        else:
#            self.get_infos().insert(position,info)
#        self.dirty = True
#    def remove_action(self,action):
#        self.get_actions().remove(action)
#        action.remove()
#        self.dirty = True
#    def remove_info(self,info):
#        self.get_infos().remove(info)
#        self.dirty = True
#    def has_active_actions(self):
#        return len(self.active_actions())>0
#    def path(self):
#        return os.path.dirname(self.path.encode('utf-8')).decode('utf-8')
#    def file_name(self):
#        return os.path.basename(self.path.encode('utf-8')).decode('utf-8')
#    def move_to(self,directory):
#        self.path = WriteableItem.move_to(self,directory)
#    def inactivate(self):
#        for action in self.active_actions():
#            action.deactivate()
#        self.dirty = True
#    def activate(self):
#        for action in self.not_done_actions():
#            action.process()
#        self.dirty = True
#        self.write()
#
#    def get_status(self):
#        status_and_path = self.status_part_of_path()
#        status_string = status_and_path[0]
#        if status_string == '':
#            return active
#        else:
#            return project_dir_status_map[status_string[1:]]
#    def status_part_of_path(self):
#        split_path = self.path().split('/')
#        project_index = split_path.index('@Projects')
#        if project_index == len(split_path)-1 or not split_path[project_index+1][0]=='@':
#            return ['']+split_path[project_index+1:]
#        else:
#            return split_path[project_index+1:]
#    def is_processed(self):
#        return self.get_status() == active
#    def date_of_last_activity(self):
#        file_name = self.path.encode('utf-8')
#        #logger.log(repr('Counting inactivity for %s.'%file_name),3)
#        return os.path.getmtime(file_name)
#    def days_since_last_activity(self):
#        days = (time()-self.date_of_last_activity())/86400
#        #logger.log(u'No activity since %s days in %s'%(days,self.name()),3)
#        return days
#    def get_tickle_date(self):
#        spp = self.status_part_of_path()
#        return extract_datetime(spp)
#    def should_not_be_tickled(self):
#        tickle_path = u'/'.join(self.status_part_of_path()[-2:])
#        return TickleDirectory(tickle_path).is_obsolete()
#    def scheduled_for_review(self):
#        return self.path().endswith('@Review')
#    def set_name(self,name):
#        self.rename(name)
#    def set_path(self,path):
#        self.path = path
#    def process(self):
#        
#        for action in self.get_actions():
#            if (action.update()):
#                self.dirty = True
#        self.write()
#        if not self.has_active_actions():
#            return False
#        days_since_last_activity = self.days_since_last_activity() 
#        if days_since_last_activity > inactivity_threshold:
#            return False
#        return True
def add_action_to_project(action,project):
    action.process()
    project.add_action(action)
    project.write()