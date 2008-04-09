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
def exit():
    appuifw.app.body.add('Exit')
    appuifw.app.body=None
    lock.signal()
def change_description_for_action(action):
    new_description = appuifw.query(u'Enter action','text',action.description)
    if new_description:
        action.set_description(new_description)
        return True
    return False

def ask_for_action(project_name,proposition=None):
    if proposition == None:
        proposition = u'Context %s'%(project_name)
    action_line = appuifw.query(u'Create action for project %s'%project_name,'text',proposition)
    if action_line == None:
        return None
    else:
        return parse_action(action_line)
def ask_for_info(proposition):
    return appuifw.query(u'Enter info','text',u'%s'%(proposition))
def new_project(proposed_name=u'',info=None):
    if not info:
        info = u'Enter a name for the project'
    project_name = appuifw.query(info,'text',proposed_name.encode('utf-8'))
    if not project_name:
        return None
    logger.log(u'New project %s'%project_name)
    project_file_name = (project_directory+project_name+'.prj') #.encode( "utf-8" )
    project = Project(project_file_name)
    project.dirty=True
    return project

class SearchableListView(object):
    def __init__(self,title,entry_filters,binding_map):
        self.title = title
        self.binding_map = binding_map
        self.current_entry_filter_index = 0
        self.entry_filters = entry_filters
        self.filtered_list = self.entry_filters[0]
        self.widgets = self.generate_widgets()
        self.view = appuifw.Listbox(self.all_widget_entries(),self.change_entry)

    def run(self):
        self.adjustment = None
        appuifw.app.screen=COMMON_CONFIG['screen'].encode('utf-8')
        save_gui(self)
        appuifw.app.title=self.title
        self.reread_widgets()
        self.set_bindings_for_selection(0)
        appuifw.app.body=self.view
        appuifw.app.exit_key_handler=self.exit
        self.lock.wait()
    def exit(self):
        self.lock.signal()
        restore_gui(self)

        
    def reread_widgets(self):
        self.widgets = self.generate_widgets()
        self.update_existing_widgets()
    def update_existing_widgets(self):
        index = self.selected_index()
        if index > len(self.widgets):
            index = len(self.widgets)
        self.view.set_list(self.all_widget_entries(),index)
    def all_widget_entries(self):
        return self.all_widget_texts()
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
        self.reread_widgets()
    def all_widget_texts(self):
        return [entry.list_repr() for entry in self.widgets]


class EditableListView(SearchableListView):
    def __init__(self,title,entry_filters,binding_map):
        super(EditableListView, self).__init__(title,entry_filters,binding_map)
    
    def function_exists(self,function_name):    
        return function_name in dir(self.current_widget())
    
    def exec_if_function_exists(self,function_name):
        if self.function_exists(function_name):
            self.exec_and_update(function_name)
            
    def exec_and_update(self,function_name):
        entry = self.current_widget()
        exec('entry.%s()'%function_name)
        self.update_existing_widgets()

    def key_and_menu_bindings(self,selected_index):
        key_and_menu_bindings=[]
        for function in applicable_functions(self.widgets[selected_index],self.binding_map)+\
            applicable_functions(self,self.binding_map):
            execute_and_update_function = self.execute_and_update(function)
            (key,description) = self.binding_map[function.__name__]
            key_and_menu_bindings.append((get_key(key),key,description,execute_and_update_function))
        return key_and_menu_bindings

    def change_entry(self):
        self.exec_if_function_exists('change')

    def execute_and_update(self,function):
        return lambda: (function(),logger.log(u'Called %s'%function),self.reread_widgets(),self.index_changed())


class ProjectListView(EditableListView):
    def __init__(self,projects):
        self.projects = projects
        super(ProjectListView, self).__init__(u'Projects', [projects.get_active_projects,projects.get_all_projects,projects.get_inactive_projects],PROJECT_LIST_KEYS_AND_MENU)
    def add_project(self,project):
        self.projects.add_project(project)
        self.reread_widgets()
    def all_widget_entries(self):
        return [entry.name_and_details() for entry in self.widgets]

    def generate_widgets(self):
#        self.projects.sort_projects()
        widgets = []
        widgets.append(NewProjectWidget(self))
        widgets.append(NoProjectWidget())
        widgets.extend([ProjectWidget(project) for project in self.filtered_list()])
        try:
            widgets.extend([SMSWidget(sms_id,self.projects) for sms_id in Inbox(EInbox).sms_messages()])
        except Exception,e:
            logger.log(u'No permission to access SMS inbox')
            logger.log(unicode(repr(e.args)))
        return widgets

    def process_all(self):
        appuifw.note(u'Processing all Projects')
        self.projects.process()
        self.update_existing_widgets()
    def reread_projects(self):
        self.projects.reread()
        self.reread_widgets()

class SMSWidget:
    def __init__(self,sms_id,projects):
        self.sms_id = sms_id
        self.projects = projects
    def content(self):
        return INBOX.content(self.sms_id)
    def change(self):
        self.view_sms()
    def create_project(self):
        project = new_project(self.sender())
        if project:
            for line in self.content().splitlines():
                project.add_info(Info(line))
            self.projects.add_project(project)
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
        lock = Ao_lock()
        appuifw.app.exit_key_handler=self.exit_sms_view
    def exit_sms_view(self):
        self.lock.signal()
        restore_gui(self)

class NoProjectWidget:
    def change(self):
        action = ask_for_action("No project")
        if action:
            action.process()

    def list_repr(self):
        return u'No project'
    def name_and_details(self):
        return (self.list_repr(), u'Sure? No project attached?')

class NewProjectWidget:
    def __init__(self,projects):
        self.projects = projects
    def change(self):
        project = new_project()
        if project:
            self.projects.add_project(project)
            project.write()
    def list_repr(self):
        return u'New project'
    def name_and_details(self):
        return (self.list_repr(), u'')

class ProjectWidget:
    def __init__(self,project):
        self.project = project
    def change(self):
        edit_view = ActionListView(self.project)
        edit_view.run()

    def add_action(self):
        action = ask_for_action(self.project.name())
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
        self.project.review()
    def activate(self):
        self.project.activate()
    def process(self):
        appuifw.note(u'Processing %s'%self.project.name())
        self.project.process()
        
    def rename(self):
        new_name = appuifw.query(u'Enter new project name','text',u'%s'%self.project.name())
        if new_name != None:
            self.project.set_name(new_name)
    def remove(self):
        self.project.set_done()
    def list_repr(self):
        return self.project.name_with_status()
    def name_and_details(self):
        if self.project.has_active_actions():
            details=self.project.active_actions()[0].summary()
        else:
            details=self.project.additional_info()
        return (self.list_repr(),details)

    def change_status(self):
        status = self.project.get_status()
        if status == processed:
            self.project.review()
        elif status == inactive:
            self.project.tickle()
        elif status == tickled:
            self.project.defer()            
        else:
            self.project.activate()
            
    def tickle(self):
        self.choose_and_execute(tickle_times,self.project.tickle)
    def defer(self):
        self.choose_and_execute(someday_contexts,self.project.defer)
    def choose_and_execute(self,choices,function):
        if choices==None or len(choices)==0:
            function()
            return
        selected_item = appuifw.selection_list(choices,search_field=1)   
        
        if not selected_item==None:
            function(choices[selected_item])
        
    def review(self):
        self.project.review()

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
            self.project.add_info(Info(info),position)



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
        new_context = appuifw.query(u'Enter context','text',self.action.context)
        if new_context:
            self.action.set_context(parse_context(new_context))
        self.project.dirty=True
    def remove(self):
        self.action.remove()
        self.project.remove_action(self.action)
    def process(self,action):
        action.process()
        self.project.dirty=True
    def change_status(self):
        
        if self.action.status in [unprocessed,inactive]:
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
    def add_action_to_context(self):
        action = Action(self.project.name(),self.context,self.project.name())
        if change_description_for_action(action):
            action.process()
            self.project.add_action(action)
    def list_repr(self):
        return u'@%s'%self.context

class InfosWidget:
    def __init__(self,project):
        self.project = project
    def list_repr(self):
        return u'Infos'
