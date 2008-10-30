import model, config, gui
import appuifw
import thread
from model import *
from config import *
from logging import logger
from e32 import Ao_lock, in_emulator
from key_codes import *
import key_codes
from inbox import EInbox,Inbox
from gui import *

ACTION_LIST_KEYS_AND_MENU = config.Configuration(gtd_directory+"actions.cfg",defaultconfig.default_actions_menu)

class ActionView( object ):
    
    def __init__( self, action):
        self.action = action
        self.saved = False
 

 
 
    ## Displays the form.
    def execute( self ):
        self.saved = False
        fields = [(u'Context','text',self.action.context),
        (u'Description','text',self.action.description),
        (u'Info','text',self.action.info)]
        logger.log(repr(fields))
        self.form = appuifw.Form(fields, appuifw.FFormEditModeOnly)
        
        self.form.save_hook = self.markSaved
        self.form.flags = appuifw.FFormEditModeOnly
        self.form.execute( )
        if self.saved:
            self.action.context = self.get_context()
            self.action.description = self.get_description()
            self.action.info = self.get_info()
 
 
    ## save_hook send True if the form has been saved.
    def markSaved( self, saved ):
        if saved and self.is_valid():
            self.saved = True
        return self.saved
    def isSaved( self ):
        return self.saved
 
    def get_description( self ):
        return self.form[1][2]
 
 

    def get_context( self ):
        return self.form[0][2]
    def is_valid(self):
        return len(self.form[0]) > 2 and len(self.form[1]) > 2
 

    def get_info( self ):
        return self.form[2][2]

def ask_for_action(project_name,proposition=None):

    action = Action(project_name,u'',u'',u'',u'')
    edit_action(action)
    
    return action


#def ask_for_action(project_name,proposition=None):
#    if proposition == None:
#        proposition = u'Context %s'%(project_name)
#    action_line = appuifw.query(u'Enter action %s'%project_name,'text',proposition)
#    if action_line == None:
#        return None
#    else:
#        return parse_action(action_line)

def edit_action(action):
    f = ActionView(action)
    f.execute()
    return f.saved
#    text = u'Enter action'
#    if info:
#        text = text+info
#    new_description = appuifw.query(text,'text',action.description)
#    if new_description:
#        action.set_description(new_description)
#        return True
#    return False



def ask_for_info(proposition):
    return appuifw.query(u'Enter info','text',u'%s'%(proposition))


class ProjectView(EditableListView):
    def __init__(self,project,projects):
        self.project = project
        self.projects = projects
        super(ProjectView, self).__init__(self.project_name(), [self.project.not_done_actions,self.project.get_actions,self.project.inactive_actions], ACTION_LIST_KEYS_AND_MENU)

    def exit(self):
        EditableListView.exit(self)
        self.project.dirty = True
        self.project.write()
        self.projects.update_status(self.project)
    def edit_menu(self):
        show_config(ACTION_LIST_KEYS_AND_MENU)
        ACTION_LIST_KEYS_AND_MENU.write()

    def actions(self):
        return self.filtered_list()
    def infos(self):
        return self.project.get_infos()
    def generate_widgets(self):
        widgets = []
        widgets.append(InfosWidget(self.project))
        infos = self.infos()
        for info in infos:
            widgets.append(InfoWidget(info,self.project))
        for (context,actions) in self.actions_by_context().items():
            widgets.append(ContextWidget(context,self.project))
            for action in actions:
                widgets.append(ActionWidget(action,self.project))
        return widgets
    def actions_by_context(self):
        context_actions_map = {}
        for action in self.actions():
            if not action.context in context_actions_map:
                context_actions_map[action.context]=[]
            context_actions_map[action.context].append(action)
        return context_actions_map
    def project_name(self):
        return self.project.name()
    def add_action(self):
        action = ask_for_action(self.project_name())
        if action:
            action.project = self.project_name()
            action.process()
            self.project.add_action(action)
    def add_info(self):
        info = ask_for_info(self.project.name())
        if info:
            selected = self.selected_index()
            if selected>0 and selected < len(self.project.get_infos()):
                position = selected
            else:
                position = None
            self.project.add_info(model.Info(info),position)



class ActionWidget:
    def __init__(self,action,project):
        self.action = action
        self.project = project
    def action_done(self):
        self.action.done()
        self.project.dirty=True
    def action_to_info(self):
        self.project.remove_action(self.action)
        self.project.add_info(self.action.context_description_info())
    def change(self):
        if edit_action(self.action):
            self.project.dirty=True


    def remove(self):
        self.action.remove()
        self.project.remove_action(self.action)
    def process(self,action):
        action.process()
        self.project.dirty=True
    def change_status(self):
        
        if self.action.is_reviewable():
            self.action.process()
        elif self.action.status == processed:
            self.action.done()
        elif self.action.status == done:
            self.action.deactivate()
        self.project.dirty=True
    def list_repr(self):
        return u'  %s %s'%(self.action.status_string(),self.action.description)

class InfoWidget:
    def __init__(self,info,project):
        self.info = info
        self.project = project
    def remove(self):
        self.project.remove_info(self.info)
    def change(self):
        new_info=ask_for_info(self.info.gui_string())
        if new_info:
            self.info.text = new_info
            self.project.dirty=True
            
    def list_repr(self):
        return u'  %s'%self.info.gui_string()

class ContextWidget:
    def __init__(self,context,project):
        self.context = context
        self.project = project
    def change(self):
        action = Action(self.project.name(),self.context,self.project.name())
        if edit_action(action):
            action.process()
            self.project.add_action(action)
    def list_repr(self):
        return u'@%s'%self.context

class InfosWidget:
    def __init__(self,project):
        self.project = project
    def change(self):
        info = ask_for_info(self.project.name())
        if info:
            self.project.add_info(model.Info(info),None)
            self.project.dirty=True
    def list_repr(self):
        return u'Infos'


__all__= ('ProjectView')
