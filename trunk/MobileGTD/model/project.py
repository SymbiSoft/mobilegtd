from action import Action
from info import Info
from model import ItemWithStatus,Status
import action
from observable import *
from filtered_list import FilteredList,StatusFilteredList

class ProjectStatus(Status):

    def update(self,project):
        return self


class Inactive(ProjectStatus):
    def __init__(self):
        super(Inactive,self).__init__('review',4)

    def update(self,project):
        if project.has_active_actions():
            #print repr(active)
            return active
        return self



class Active(ProjectStatus):
    
    def __init__(self):
        super(Active,self).__init__('',1)
        
    def update(self,project):
        if not project.has_active_actions():
            #print repr(inactive)
            return inactive
        return self

    



unprocessed = ProjectStatus('unprocessed',0)
active = Active()
done = ProjectStatus('done',2)
tickled = ProjectStatus('tickled',3)
inactive = Inactive()
someday = ProjectStatus('someday',5)
info = ProjectStatus('info',0)


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
    observers = []
    def __init__(self,name,status = inactive,actions=[],infos=[]):
        ItemWithStatus.__init__(self,status)
        self.name=name
        self.actions=StatusFilteredList(actions)
        self.infos=FilteredList(infos)
        self.update_methods = {'status':self.action_changed_status,
                               'description':self.action_changed_content,
                               'info':self.action_changed_content,
                               'context':self.action_changed_content,
                               'text':self.info_changed}
        super(Project,self).__init__()
        for o in Project.observers:
            o.notify(self.__class__,'new_project',self,None)


    def add_action(self,action):
        action.project = self
        action.observers.append(self)
        self.actions.append(action)
        self.notify_observers('add_action',action)
        self.update_status()
        
    def remove_action(self,action):
        action.status = done
        action.observers.remove(self)
        self.actions.remove(action)
        self.notify_observers('remove_action',action)
        self.update_status()

    def add_info(self,info,position=None):
        info.observers.append(self)
        self.infos.append(info)
        self.notify_observers('add_info', info)

    def remove_info(self,info):
        info.observers.remove(self)
        self.infos.remove(info)
        self.notify_observers('remove_info', info)

    def actions_with_status(self,status):
        return self.actions.with_property(lambda a:a.status == status)

    def active_actions(self):
        return self.actions_with_status(action.active)

    def has_active_actions(self):
        return len(self.active_actions()) > 0
    
    def notify(self,action,attribute,new_value,old_value=None):
        self.update_methods[attribute](action,new_value)
    
    def info_changed(self,info,text):
        self.notify_observers('changed_info', info)

    def action_changed_content(self,action,content):
        self.notify_observers('changed_action',action)
        
    def update_status(self):
        self.status = self.status.update(self)
    
    def action_changed_status(self,action,status):
        self.update_status()
        
    def __eq__(self, other):
        return self.name == other.name and self.status == other.status

    def __ne__(self,project):
        return not self.__eq__(project)

    def __str__(self):
        return self.name

    def status_symbol_and_name(self):
        return self.status_symbol()+self.name
    def __repr__(self):
        return 'Project %s (%s actions, %s infos)'%(self.name,len(self.actions),len(self.infos))