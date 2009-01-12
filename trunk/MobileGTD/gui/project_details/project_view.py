import model, config, gui
import appuifw,os
import thread
from model.model import *
from config.config import gtd_directory,Configuration
from config.defaultconfig import default_actions_menu
from gui.gui import EditableListView
from infos_widget import InfosWidget
from info_widget import InfoWidget
from context_widget import ContextWidget
from action_widget import ActionWidget
from action_view import ActionView
from model import action
from model import info
from model.action import Action
from log.logging import logger
from e32 import Ao_lock, in_emulator
from key_codes import *
import key_codes

from gui import *

ACTION_LIST_KEYS_AND_MENU = Configuration(os.path.join(gtd_directory,"actions.cfg"))


def ask_for_action(project_name,proposition=None):

    action = Action(project_name,u'')
    was_saved = edit_action(action)
    if was_saved:
    	return action
    else:
    	return None


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
    return f.isSaved() == 1
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
    def __init__(self,project):
        self.project = project
        self.project.observers.append(self)
        super(ProjectView, self).__init__(self.project.name, [lambda:self.project.actions.with_property(lambda a:a.status==action.active)], ACTION_LIST_KEYS_AND_MENU)

    def exit(self):
        self.project.observers.remove(self)
        EditableListView.exit(self)
#        self.project.dirty = True
#        self.project.write()
#        self.projects.update_status(self.project)
    def edit_menu(self):
        show_config(ACTION_LIST_KEYS_AND_MENU)
        ACTION_LIST_KEYS_AND_MENU.write()

    def actions(self):
        return self.project.actions

    def generate_widgets(self):
        widgets = []
        widgets.append(InfosWidget(self.project))
        for info in self.project.infos:
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

    def add_action(self):
        action = ask_for_action(self.project.name)
        if action:
            self.project.add_action(action)
    def add_info(self):
        i = ask_for_info(self.project.name)
        if i:
            selected = self.selected_index()
            # First position is "Infos"
            if selected>=0 and selected <= len(self.project.infos):
                position = selected
            else:
                position = None
            self.project.add_info(info.Info(i),position)
            if position:
                self.set_index(position+1)



    def notify(self,project,attribute,new=None,old=None):
        self.refresh()




__all__= ('ProjectView','ask_for_action','ask_for_info')
