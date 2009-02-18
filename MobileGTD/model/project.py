from action import Action
from info import Info
from model import *
from datetime import date
import action
from observable import *
from filtered_list import FilteredList,StatusFilteredList
import datetime
from log.logging import logger
import sys

class ProjectStatus(Status):
    pass

#    def __eq__(self,other):
#        return False
class Inactive(ProjectStatus):
    def __init__(self):
        super(Inactive,self).__init__('review',4,'!')

    def update(self,project):
#        if project.has_active_actions():
#            #print repr(active)
#            return active
        return self



class Active(ProjectStatus):
    
    def __init__(self):
        super(Active,self).__init__('active',1)
        
    def update(self,project):
        if not project.has_active_actions():
            #print repr(inactive)
            return inactive
        return self

    
class Tickled(ProjectStatus):
    def __init__(self,date=date.tomorrow()):
        super(Tickled,self).__init__('tickled',3,'/')
        self.date = date
    
    def update(self,project):
        if self.date <= date.now():
            return active
        else:
            return self

    def __str__(self):
        return super(Tickled,self).__str__()+" for %s"%self.date
    
    def __repr__(self):
        return self.__str__()

unprocessed = ProjectStatus('unprocessed',0)
active = Active()
done = ProjectStatus('done',2,'+')
tickled = Tickled()
inactive = Inactive()
someday = ProjectStatus('someday',5,'~')
info = ProjectStatus('info',0)



class Project(ObservableItem,ItemWithStatus):
    observers = []
    def __init__(self,name,status = inactive):
        logger.log(u'Creating project %s (%s)'%(name,status))
        ItemWithStatus.__init__(self,status)
        self.name=name
        self.actions=StatusFilteredList([])
        self.infos=FilteredList([])
        self.update_methods = {'status':self.action_changed_status,
                               'description':self.action_changed_content,
                               'info':self.action_changed_content,
                               'context':self.action_changed_content,
                               'text':self.info_changed}
        super(Project,self).__init__()
        for o in Project.observers:
            o.notify(self.__class__,'new_project',self,None)
        logger.log(u'Now, its project %s (%s)'%(name,status))


    def add_action(self,a):
        a.project = self
        a.observers.append(self)
        self.actions.append(a)
        self.notify_observers('add_action',a)
        if a.status == action.unprocessed:
            a.status = action.active
        
    def remove_action(self,a):
        a.status = action.done
        a.observers.remove(self)
        self.actions.remove(a)
        self.notify_observers('remove_action',a)

    def add_info(self,info,position=None):
        info.observers.append(self)
        self.infos.append(info)
        self.notify_observers('add_info', info)

    def remove_info(self,info):
        info.observers.remove(self)
        self.infos.remove(info)
        self.notify_observers('remove_info', info)

    def activate(self):
        self.status = active
        for a in self.actions_with_status(action.inactive):
            a.status = action.active

    def deactivate(self):
        self.status = inactive
        for a in self.actions_with_status(action.active):
            a.status = action.inactive

    def actions_with_status(self,status):
        return self.actions.with_property(lambda a:a.status == status)

    def active_actions(self):
        return self.actions_with_status(action.active)

    def has_active_actions(self):
        return len(self.active_actions()) > 0
    
    def notify(self,action,attribute,new=None,old=None):
        self.update_methods[attribute](action,new)
    
    def info_changed(self,info,text):
        self.notify_observers('changed_info', info)

    def action_changed_content(self,action,content):
        self.notify_observers('changed_action',action)
        
    
    def action_changed_status(self,a,status):
        self.notify_observers('changed_action', new=a, old=None)
        
    def last_modification_date(self):
        return datetime.date.now()
        
    def __eq__(self, other):
        return self.name == other.name and self.status == other.status

    def __ne__(self,project):
        return not self.__eq__(project)

    def __str__(self):
        return self.name

    def status_symbol_and_name(self):
        return self.status_symbol()+self.name
    def __repr__(self):
        return 'Project %s (@%s, %s actions, %s infos)'%(self.name,self.status.name.capitalize(),len(self.actions),len(self.infos))