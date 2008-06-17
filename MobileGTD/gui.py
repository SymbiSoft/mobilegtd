import model, config
import appuifw
import thread
from model import *
from config import *
from logging import logger
from e32 import Ao_lock, in_emulator
from key_codes import *
import key_codes
from inbox import EInbox,Inbox
INBOX = Inbox(EInbox)

PROJECT_LIST_KEYS_AND_MENU = config.Configuration(gtd_directory+"projects.cfg",defaultconfig.default_projects_menu)
ACTION_LIST_KEYS_AND_MENU = config.Configuration(gtd_directory+"actions.cfg",defaultconfig.default_actions_menu)
sms_regexp = re.compile('([^\w ]*)',re.U)
def show_config(cfg):        
    fields = []
    for k, v in cfg.items():
        v = cfg.format_value(v)
        if isinstance(v, int) or isinstance(v, long):
            tname = 'number'
            v = int(v)
        elif isinstance(v, list) or isinstance(v, tuple):
            for item in v[0]:
                if not isinstance(item, unicode):
                    raise Exception("list can contain only unicode objects, "\
                                    "object %r is not supported" % item)
            
            tname = 'combo'
        elif isinstance(v, unicode):
            tname = 'text'
        else:
            raise Exception("%s has non-supported value" % k)

        fields.append((unicode(k), tname, v))


    form = appuifw.Form(fields=fields, flags=appuifw.FFormEditModeOnly | \
                        appuifw.FFormDoubleSpaced)

    saved = [False]
    def save_hook(param):
        saved[0] = True
    form.save_hook = save_hook
    
    form.execute()

    # return true if user saved, false otherwise
    if not saved[0]:
        return False
    
    for label, tname, value in form:
        if tname == 'combo':
            value = (value[0], int(value[1]))

        cfg[str(label)] = cfg.parse_value(value)

    return True


def no_action():
    pass

def applicable_functions(obj,allowed_function_names):
    function_names = [function_name for function_name in dir(obj) if function_name in allowed_function_names]
    return [eval('obj.%s'%function_name) for function_name in function_names]

def get_key(key_name):
    if key_name == '':
        key = None
    else:
        key=eval('EKey%s'%key_name)
    return key

def all_key_names():
    return filter(lambda entry:entry[0:4]=='EKey',dir(key_codes))
def all_key_values():
    key_values=[
                EKey0,
                EKey1,
                EKey2,
                EKey3,
                EKey4,
                EKey5,
                EKey6,
                EKey7,
                EKey8,
                EKey9,
                EKeyStar,
                EKeyHash,
                ]
    return key_values


def save_gui(object):
    object.old_gui = appuifw.app.body
    object.old_menu = appuifw.app.menu
    object.old_exit_key_handler = appuifw.app.exit_key_handler
    object.old_title=appuifw.app.title
    object.lock = Ao_lock()

def restore_gui(object):
    appuifw.app.body = object.old_gui
    appuifw.app.menu = object.old_menu
    appuifw.app.exit_key_handler = object.old_exit_key_handler
    appuifw.app.title = object.old_title

def change_description_for_action(action,info=None):
    text = u'Enter action'
    if info:
        text = text+info
    new_description = appuifw.query(text,'text',action.description)
    if new_description:
        action.set_description(new_description)
        return True
    return False


def ask_for_action(project_name,proposition=None):
    if proposition == None:
        proposition = u'Context %s'%(project_name)
    action_line = appuifw.query(u'Enter action %s'%project_name,'text',proposition)
    if action_line == None:
        return None
    else:
        return parse_action(action_line)
def ask_for_info(proposition):
    return appuifw.query(u'Enter info','text',u'%s'%(proposition))

class SearchableListView(object):
    def __init__(self,title,entry_filters,binding_map):
        self.title = title
        self.exit_flag = False
        self.binding_map = binding_map
        self.current_entry_filter_index = 0
        self.entry_filters = entry_filters
        self.filtered_list = self.entry_filters[0]
        self.widgets = self.generate_widgets()
        self.lock = None
        self.view = appuifw.Listbox(self.all_widget_entries(),self.change_entry)

    def run(self):
        self.adjustment = None
        appuifw.app.screen=COMMON_CONFIG['screen'].encode('utf-8')
        save_gui(self)
        appuifw.app.title=self.title
        self.refresh()
        self.set_bindings_for_selection(0)
        appuifw.app.body=self.view
        appuifw.app.exit_key_handler=self.exit
        try:
            self.lock.wait()
            while not self.exit_flag:
                self.refresh()
                self.lock.wait()
        except:
            pass
        restore_gui(self)
    def exit(self):
        self.exit_flag = True
        self.lock.signal()

    def update(self,subject):
        if self.lock:
            self.lock.signal()
        #pass
    def refresh(self):
        self.widgets = self.generate_widgets()
        self.redisplay_widgets()
    def redisplay_widgets(self):
        index = self.selected_index()
        if index > len(self.widgets):
            index = len(self.widgets)
        self.view.set_list(self.all_widget_entries(),index)
    def all_widget_entries(self):
        return self.all_widget_texts()
    def all_widget_texts(self):
        return [entry.list_repr() for entry in self.widgets]
    def remove_all_key_bindings(self):
        for key in all_key_values():
            self.view.bind(key,no_action)
    def set_bindings_for_selection(self,selected_index):
        self.remove_all_key_bindings()
        menu_entries=[]
        for key,key_name,description,function in self.key_and_menu_bindings(selected_index):
            if key:
                self.view.bind(key,function)
            if description != '':
                if key:
                    if key_name == 'Backspace': key_name='C'
                    description='[%s] '%key_name +description
                else:
                    description='    '+description
                menu_entries.append((description,function))
        self.view.bind(EKeyUpArrow,lambda: self.index_changed(-1))
        self.view.bind(EKeyDownArrow,lambda: self.index_changed(1))
        menu_entries.append((u'Exit', self.exit))
        appuifw.app.menu=menu_entries

    def selected_index(self):
        return self.view.current()
    def index_changed(self,adjustment=None):
        if adjustment:
            index = self.selected_index() + adjustment
        else:
            index = self.selected_index()
        if index < 0:
            index = len(self.widgets) - 1
        if index >= len(self.widgets):
            index = 0
        self.set_bindings_for_selection(index)


    def search_item(self):
        selected_item = appuifw.selection_list(self.all_widget_texts(),search_field=1)
        if selected_item == None or selected_item == -1:
            selected_item = self.selected_index()
        self.view.set_list(self.all_widget_entries(),selected_item)
        self.set_bindings_for_selection(selected_item)
    def current_widget(self):
        return self.widgets[self.selected_index()]
    def switch_entry_filter(self):
        self.current_entry_filter_index += 1
        self.filtered_list = self.entry_filters[self.current_entry_filter_index % len(self.entry_filters)]
        self.refresh()


class EditableListView(SearchableListView):
    def __init__(self,title,entry_filters,binding_map):
        super(EditableListView, self).__init__(title,entry_filters,binding_map)
    
#    def function_exists(self,function_name):    
#        return function_name in dir(self.current_widget())
#    
#    def exec_if_function_exists(self,function_name):
#        if self.function_exists(function_name):
#            self.exec_and_update(function_name)
#            
#    def exec_and_update(self,function_name):
#        entry = self.current_widget()
#        exec('entry.%s()'%function_name)
#        self.refresh()

    def key_and_menu_bindings(self,selected_index):
        key_and_menu_bindings=[]
        for function in applicable_functions(self.widgets[selected_index],self.binding_map)+\
            applicable_functions(self,self.binding_map):
            execute_and_update_function = self.execute_and_update(function)
            (key,description) = self.binding_map[function.__name__]
            key_and_menu_bindings.append((get_key(key),key,description,execute_and_update_function))
        return key_and_menu_bindings

    def change_entry(self):
        #self.exec_if_function_exists('change')
        self.current_widget().change()
        self.refresh()
    def execute_and_update(self,function):
        return lambda: (function(),self.refresh(),self.index_changed())


class ProjectListView(EditableListView):
    def __init__(self,projects):
        self.projects = projects
        self.projects.attach(self)
        super(ProjectListView, self).__init__(u'Projects', [projects.get_current_projects,projects.get_all_projects,projects.get_inactive_projects],PROJECT_LIST_KEYS_AND_MENU)
        thread.start_new_thread(projects.process,())
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
        action = ask_for_action("without project",u"Context Action-Description")
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
        edit_view = ActionListView(self.project)
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

class DisplayableFunction:
    def __init__(self,display_name,function):
        self.display_name = display_name
        self.function = function
    def list_repr(self):
        return self.display_name
    def execute(self):
        function()

class ActionListView(EditableListView):
    def __init__(self,project):
        self.project = project
        super(ActionListView, self).__init__(self.project_name(), [self.project.not_done_actions,self.project.get_actions,self.project.inactive_actions], ACTION_LIST_KEYS_AND_MENU)

    def exit(self):
        EditableListView.exit(self)
        self.project.write()
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
        if change_description_for_action(self.action):
            self.project.dirty=True

    def change_context(self):
        new_context = appuifw.query(u'Enter new context','text',self.action.context)
        if new_context:
            self.action.set_context(model.parse_context(new_context))
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
        if change_description_for_action(action,' for '+self.context):
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
