import model, config, gui
import appuifw
import thread
from model import *
from config import *
from logging import logger
from e32 import Ao_lock, in_emulator
from key_codes import *
import key_codes

from gui import *

ACTION_LIST_KEYS_AND_MENU = config.Configuration(gtd_directory+"actions.cfg",defaultconfig.default_actions_menu)


def ask_for_action(project_name,proposition=None):

    action = Action(project_name,u'',u'',u'',u'')
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
            # First position is "Infos"
            if selected>=0 and selected <= len(self.project.get_infos()):
                position = selected
            else:
                position = None
            self.project.add_info(model.Info(info),position)
            if position:
                self.set_index(position+1)








__all__= ('ProjectView','ask_for_action')
