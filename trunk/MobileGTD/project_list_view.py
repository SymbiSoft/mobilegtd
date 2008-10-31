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


PROJECT_LIST_KEYS_AND_MENU = config.Configuration(gtd_directory+"projects.cfg",defaultconfig.default_projects_menu)
sms_regexp = re.compile('([^\w ]*)',re.U)
INBOX = Inbox(EInbox)

class ProjectListView(EditableListView):
    def __init__(self,projects):
        self.projects = projects
        self.projects.attach(self)
        super(ProjectListView, self).__init__(u'Projects', [projects.get_current_projects,projects.get_all_projects,projects.get_inactive_projects],PROJECT_LIST_KEYS_AND_MENU)
        #appuifw.note(u'Before starting thread')
        thread.start_new_thread(projects.process,())
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
        widgets.extend([ProjectWidget(self.projects,project) for project in self.filtered_list()])
        if read_sms:
            try:
                widgets.extend([SMSWidget(sms_id,self.projects) for sms_id in INBOX.sms_messages()])
            except Exception,e:
                logger.log(u'No permission to access SMS inbox')
                logger.log(unicode(repr(e.args)))
        return widgets

    def process_all(self):
        appuifw.note(u'Processing all Projects')
        self.projects.process()
        self.redisplay_widgets()
    def reread_projects(self):
        self.projects.reread()
        self.refresh()

class SMSWidget:
    def __init__(self,sms_id,projects):
        self.sms_id = sms_id
        self.projects = projects
    def content(self):
        return INBOX.content(self.sms_id)
    def change(self):
        self.view_sms()
    def create_project(self):
        infos = []
        lines = sms_regexp.split(self.content())
        
        info_lines = []
        for index in range(len(lines)):
            if len(lines[index]) < 2 and index>0:
                previous = info_lines.pop()
                info_lines.append(previous+lines[index])
            else:
                info_lines.append(lines[index])
        for line in info_lines:
            infos.append(line)
        project = NewProjectWidget(self.projects).change(u'Project for SMS from %s'%self.sender(),infos)
    def remove(self):
        INBOX.delete(self.sms_id)
    def sender(self):
        return INBOX.address(self.sms_id)
    def list_repr(self):
        return u'SMS from %s'%self.sender()
    def name_and_details(self):
        return (self.list_repr(), self.content())

    def view_sms(self):
        save_gui(self)
        t = appuifw.Text()
        t.add(self.list_repr())
        t.add(u':\n')
        t.add(self.content())
        appuifw.app.menu=[(u'Create Project', self.create_project),
        (u'Exit', self.exit_sms_view)]

        appuifw.app.title=self.list_repr()
        appuifw.app.body=t
        appuifw.app.exit_key_handler=self.exit_sms_view
        lock = Ao_lock()
    def exit_sms_view(self):
        self.lock.signal()
        restore_gui(self)

class NewActionWidget:
    def change(self):
        action = ask_for_action(u"No project")
        if action:
            action.process()
        return action

    def list_repr(self):
        return u'New action'
    def name_and_details(self):
        return (self.list_repr(), u'Sure? No project attached?')

class NewProjectWidget:
    def __init__(self,projects):
        self.projects = projects
    def change(self,proposed_name = 'Project name',infos=None):
        project_name = appuifw.query(u'Enter a name for the project','text',proposed_name)
        if not project_name:
            return
        logger.log(u'New project %s'%project_name)
        project = self.projects.create_project(project_name)
        if infos:
            for info in infos:
                project.add_info(Info(info))
        ProjectWidget(self.projects,project).change()
        return project

    def list_repr(self):
        return u'New project'
    def name_and_details(self):
        return (self.list_repr(), u'')

class ProjectWidget:
    def __init__(self,projects,project):
        self.project = project
        self.projects = projects
    def change(self):
        from project_view import ProjectView
        edit_view = ProjectView(self.project, self.projects)
        edit_view.run()

    def add_action(self):
        action = ask_for_action(u'for project %s'%self.project.name())
        if action:
            action.process()
            add_action_to_project(action,self.project)
            self.project.write()

    def add_info(self):
        info = ask_for_info(self.project.name())
        if info:
            self.project.add_info(Info(info))
            self.project.write()
    def review(self):
        self.projects.review(self.project)
    def activate(self):
        self.projects.activate(self.project)
    def process(self):
        appuifw.note(u'Processing %s'%self.project.name())
        self.projects.process(self.project)
        
    def rename(self):
        new_name = appuifw.query(u'Enter new project name','text',u'%s'%self.project.name())
        if new_name != None:
            self.project.set_name(new_name)
    def remove(self):
        self.projects.set_done(self.project)
    def list_repr(self):
        return self.project.name_with_status()
    def name_and_details(self):
        if self.project.has_active_actions():
            details=self.project.active_actions()[0].summary()
        else:
            details=self.project.additional_info()
        return (self.list_repr(),details)

    
    def tickle(self):
        self.choose_and_execute(self.projects.get_tickle_times(),self.projects.tickle)
    def defer(self):
        self.choose_and_execute(self.projects.get_someday_contexts(),self.projects.defer)
    def choose_and_execute(self,choices,function):
        if choices==None or len(choices)==0:
            function(self.project)
            return
        selected_item = appuifw.selection_list(choices,search_field=1)   
        
        if not selected_item==None:
            function(self.project,choices[selected_item])
        
    def review(self):
        self.projects.review(self.project)
