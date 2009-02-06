from model import model
from config import config
from gui.gui import EditableListView
import appuifw,thread,re
from model import *
from config.config import gtd_directory,read_sms
from config.defaultconfig import default_projects_menu
from log.logging import logger
from e32 import Ao_lock, in_emulator
from key_codes import *
import key_codes
from new_project_widget import NewProjectWidget
from new_action_widget import NewActionWidget
from project_widget import ProjectWidget
from logic import review_visitor

#from gui import *


PROJECT_LIST_KEYS_AND_MENU = config.Configuration(gtd_directory+"projects.cfg",default_projects_menu)
sms_regexp = re.compile('([^\w ]*)',re.U)

class ProjectListView(EditableListView):
    def __init__(self,projects):
        self.projects = projects
        self.projects.observers.append(self)
        super(ProjectListView, self).__init__(u'Projects', [lambda:projects],PROJECT_LIST_KEYS_AND_MENU)
        #appuifw.note(u'Before starting thread')
#        thread.start_new_thread(projects.process,())
        #appuifw.note(u'After starting thread %s'%repr(projects.observers))
    def exit(self):
        self.exit_flag = True
        self.lock.signal()
        if not in_emulator():
            appuifw.app.set_exit()

    def edit_menu(self):
        show_config(PROJECT_LIST_KEYS_AND_MENU)
        PROJECT_LIST_KEYS_AND_MENU.write()
    def edit_config(self):
        show_config(COMMON_CONFIG)
        COMMON_CONFIG.write()
    def add_project(self,project):
        self.projects.add_project(project)
        self.refresh()
    def all_widget_entries(self):
        return [entry.name_and_details() for entry in self.widgets]
    def new_project(self):
        NewProjectWidget(self.projects).change()
    def new_action(self):
        NewActionWidget().change()
    def generate_widgets(self):
        widgets = []
        widgets.append(NewProjectWidget(self.projects))
        widgets.append(NewActionWidget())
        self.filtered_list()
        widgets.extend([ProjectWidget(self.projects,project) for project in self.projects.sorted_by_status()])
        if read_sms:
            from sms_widget import create_sms_widgets
            try:
                widgets.extend(create_sms_widgets())
            except Exception,e:
                logger.log(u'No permission to access SMS inbox')
                logger.log(unicode(repr(e.args)))
        return widgets

    def process_all(self):
        appuifw.note(u'Processing all Projects')
        reviewer = review_visitor.ReviewVisitor()
        reviewer.review(self.projects)
        self.redisplay_widgets()
    def reread_projects(self):
        self.projects.reread()
        self.refresh()




