import os,re,codecs,sys,appuifw,traceback
from inbox import EInbox,Inbox
from e32 import Ao_lock
from key_codes import *
import key_codes
from time import *


def u_join(father,son):
    return u'%s/%s'%(father,son)
console_encoding = "latin1"
file_name_encoding = "utf-8"
console_log_level = 2
file_log_level = 5

codec = 'utf-8'
unprocessed = 0
processed = 1
done = 2
tickled = 3
inactive = 4
someday = 5
info = 2

def invert_dictionary(dictionary):
    return dict([[v,k] for k,v in dictionary.items()])


sign_status_map = {u'+':done,u'-':processed,u'!':inactive,u'/':tickled,u'':unprocessed,u'~':someday}
status_sign_map = invert_dictionary(sign_status_map)
status_string_map = {done:u'Done',processed:u'Processed',inactive:u'Inactive',tickled:u'Tickled',unprocessed:u'Unprocessed'}
project_dir_status_map = {u'Done':done,u'Review':inactive,u'Someday':someday,u'Tickled':tickled}
status_project_dir_map = invert_dictionary(project_dir_status_map)
file_name_regexp = re.compile('/?(?P<path>.*/)*(?P<file_name>.*)\....',re.U)
action_regexp = re.compile('(?P<status>[+-/!])?\s*(?P<context>\S*)\s*(?P<description>[^\(]*)(\((?P<info>[^\)]*))?',re.U)
context_regexp = re.compile('(?P<numbers>\d*)(?P<text>\D?.*)',re.U)
configuration_regexp = re.compile('(?P<key>[^:]*):(?P<value>.*)',re.U)


def log(text,level=0):
    if level < file_log_level:
        log_file.write(text.encode('utf-8')+'\n')
    if level < console_log_level:
            #appuifw.note(u''+repr(text))
#        try:
            #print ' '*level,text.encode(console_encoding)
            log_entries.append(u' '*level+text)
#        except:
#            print ' '*level,repr(text.encode(console_encoding))


def guess_encoding(data):
    encodings = ['ascii','utf-8','utf-16']
    successful_encoding = None
    if data[:3]=='\xEF\xBB\xBF':
        log('Unicode BOM in %s'%repr(data),6)
        data = data[3:]

    for enc in encodings:
        if not enc:
            continue
        try:
            decoded = unicode(data, enc)
            successful_encoding = enc
            break
        except (UnicodeError, LookupError):
            pass
    if successful_encoding is None:
        raise UnicodeError('Unable to decode input data %s. Tried the'
            ' following encodings: %s.' %(repr(data), ', '.join([repr(enc)
                for enc in encodings if enc])))
    else:
        log('Decoded %s to %s'%(repr(data),repr(decoded)),6)
        return (decoded, successful_encoding)




def read_text_from_file(unicode_file_name):
    f=file(unicode_file_name.encode('utf-8'),'r')
    raw=f.read()
    (text,encoding)=guess_encoding(raw)

    return text
def parse_file_to_line_list(unicode_complete_path):
    text = read_text_from_file(unicode_complete_path)
    lines = text.splitlines()
    return lines


from UserDict import UserDict

class odict(UserDict):
    def __init__(self, dict = None):
        self._keys = []
        UserDict.__init__(self, dict)

    def __setitem__(self, key, item):
        UserDict.__setitem__(self, key, item)
        if key not in self._keys: self._keys.append(key)

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys
    def __repr__(self):
        return repr(self.items())

    def values(self):
        return map(self.get, self._keys)

def read_configuration(file_name,ordered=False):
    if ordered:
        configuration=odict()
    else:
        configuration ={}
    if not os.path.isfile(file_name.encode('utf-8')):
        log(u'Configuration file %s does not exist'%file_name)
        return configuration
    for line in parse_file_to_line_list(file_name):
        if line[0] == '#': continue
        matching = configuration_regexp.match(line)
        key = matching.group('key')
        value = matching.group('value').rstrip(u' \r\n')
        if ',' in value:
            value=value.split(',')

        configuration[key]=value
    return configuration





main_config_file = 'C:/System/Data/mobile_gtd.cfg'

COMMON_CONFIG = read_configuration(main_config_file)
def read_config(key):
    if not COMMON_CONFIG.has_key(key):
        error_text = u'%s does not contain a configuration key for %s'%(main_config_file,key)
        appuifw.note(error_text)
        appuifw.note(u'Maybe you need to install the newest version of the data package')
        log(error_text)
    else:
        return COMMON_CONFIG[key]

gtd_directory = read_config('path')
log_file=file(gtd_directory+'gtd.log','w')
inactivity_threshold = int(read_config('inactivity_threshold'))
project_directory = gtd_directory+'@Projects/'
review_directory = project_directory+'@Review/'
done_directory = project_directory+'@Done/'
someday_directory = project_directory+'@Someday/'
tickled_directory = project_directory+'@Tickled/'
project_dir_name = '@Projects/'

log_entries=[]



INBOX = Inbox(EInbox)




def safe_chdir(path_unicode):
    try:
        path = path_unicode.encode('utf-8')
    except UnicodeError:
        log('Error decoding path %s'%repr(path_unicode))
        return
    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)





class ItemWithStatus(object):
    def __init__(self,status):
        self.status = status
    def status_string(self):
        if self.status == unprocessed:
            return u''
        else:
            return u'%s '%status_sign_map[self.status]

class WriteableItem(ItemWithStatus):
    def __init__(self,status=unprocessed):
        super(WriteableItem, self).__init__(status)
    def write(self):
        safe_chdir(self.path())
        f = file(self.file_name().encode('utf-8'),'w')
        content = self.file_string().encode('utf-8')
        #log( (u'Writing %s to %s'%(content,file_name)).encode('utf-8'),2)
        f.write(content)
        f.close()
    def move_to(self,directory):
        self.write()
        new_file_name = u_join(directory,self.file_name())
        old_file_name = u_join(self.path(),self.file_name())
        log(u'Moving')
        log(repr(old_file_name.encode('utf-8')))
        log(repr(new_file_name.encode('utf-8')))
        os.renames(old_file_name.encode('utf-8'),new_file_name.encode('utf-8'))
        log(u'Done moving')
        return new_file_name


class Action(WriteableItem):

    def __init__(self,description,context,project,info='',status=unprocessed):
        super(Action, self).__init__(status)
        self.project = project
        self.description = description
        self.context = context
        self.info = info

    def update(self,path=gtd_directory):
        context_path = u_join(path,self.context)
        if (self.status == unprocessed):
            log('Processing %s'%self.description,3)
            self.process()
            return True
        elif(self.status == processed):
            file_name = self.file_name()
            path_and_file=u_join(context_path,file_name)
            log(repr(path_and_file),4)

            if not os.path.isfile(path_and_file.encode('utf-8')):
                self.status = done
                return True
        return False
    def path(self,context=None):
        if not context:
            context=self.context
        return u_join(gtd_directory,context)

    def unprocess(self):
        self.status = unprocessed
        self.remove()
    def done(self):
        self.status = done
        self.remove()
    def deactivate(self):
        self.status = inactive
        self.remove()
    def process(self):
        self.status = processed
        self.write()
    def path_and_file(self):
        return u_join(self.path(),self.file_name())
    def remove(self):
        encoded_path = self.path_and_file().encode('utf-8')
        if os.path.isfile(encoded_path):
            os.remove(encoded_path)
    def set_context(self,context):
        self.status = processed
        self.move_to(gtd_directory+'/'+context)
        self.context = context
        self.write()
    def is_active(self):
        return self.status in [processed,unprocessed]
    def is_not_done(self):
        return self.status in [processed,unprocessed,inactive]
    def file_name(self):
        return u'%s.act'%self.description
    def set_description(self,description):
        self.remove()
        self.description = description
        self.process()
    def __repr__(self):
        advanced_info = ''
        if len(self.project)>0:
            advanced_info = advanced_info+' Project: '+self.project
        if len(self.info) > 0:
            advanced_info = advanced_info +' Info: '+self.info
        if len(advanced_info) > 0:
            advanced_info = '   ('+advanced_info+' )'
        return repr(self.description)+' @'+repr(self.context)+repr(advanced_info)

    def file_string(self):
        string = self.project_file_string()
        if len(self.project)>0:
            string = string+u'\nProject: %s'%self.project
        return string
    def project_file_string(self,entry_separator=' '):
        return '%s %s'%(self.status_string(),self.context_description_info())
    def context_description_info(self,entry_separator=' '):
        return u'%s%s%s%s%s'%(\
            self.context,entry_separator,\
            self.description,entry_separator,\
            self.info_string())

    def info_string(self,entry_separator=' '):
        info_string = u''
        if (len(self.info) > 1):
            info_string = u'%s(%s)'%(entry_separator,self.info)
        return info_string

class Project(WriteableItem):
    def __init__(self,file_name):
        self.complete_file_path=file_name
        self.actions=None
        self.infos=None
        self.dirty = False
        super(Project, self).__init__(self.get_status())
        log(u'Project %s is %s'%(self.name(),self.status))
        self.read()

    def read(self):
        if not os.path.isfile(self.complete_file_path.encode('utf-8')):
            self.actions=[]
            self.infos=[]
        else:
            action_strings = parse_file_to_line_list(self.complete_file_path)
            (self.actions,self.infos) = parse_lines(action_strings)
            for action in self.actions:
                action.project = self.name()

    def file_string(self):
        lines = []
        for info in self.get_infos():
            lines.append(u'# %s'%info)
        self.sort_actions()
        for action in self.get_actions():
            lines.append(action.project_file_string())
        return u'\n'.join(lines) 

    def write(self):
        if self.dirty:
            WriteableItem.write(self)
            self.dirty = False
    def sort_actions(self):
        self.get_actions().sort(compare_by_status)

    def get_actions(self):
        if self.actions == None:
            self.read()
        return self.actions
    def get_infos(self):
        if self.infos == None:
            self.read()
        return self.infos
    def status_string(self):
        if self.status == processed:
            return u''
        else:
            return ItemWithStatus.status_string(self)
    def name_with_status(self):
        return self.status_string()+self.name()
    def name(self):
        matching = file_name_regexp.match(self.complete_file_path)
        file_name=matching.group('file_name')
        return file_name
    def active_actions(self):
        return filter(lambda action: action.is_active() ,self.actions)
    def not_done_actions(self):
        return filter(lambda action: action.is_not_done() ,self.actions)
    def inactive_actions(self):
        return filter(lambda action: not action.is_active() ,self.actions)
    def add_action(self,action):
        self.get_actions().append(action)
        self.dirty = True
    def add_info(self,info,position=None):
        if not position:
            self.get_infos().append(info)
        else:
            self.get_infos().insert(position,info)
        self.dirty = True
    def remove_action(self,action):
        self.get_actions().remove(action)
        action.remove()
        self.dirty = True
    def remove_info(self,info):
        self.get_infos().remove(info)
        self.dirty = True
    def has_active_actions(self):
        return len(self.active_actions())>0
    def path(self):
        return os.path.dirname(self.complete_file_path.encode('utf-8')).decode('utf-8')
    def file_name(self):
        return os.path.basename(self.complete_file_path.encode('utf-8')).decode('utf-8')
    def move_to(self,directory):
        self.complete_file_path = WriteableItem.move_to(self,directory)
    def review(self):
        self.status = inactive
        self.move_to(review_directory)
    def set_done(self):
        self.status = done
        self.move_to(done_directory)
    def unreview(self):
        self.status = processed
        self.move_to(project_directory)
    def set_someday(self):
        self.status = someday
        self.move_to(someday_directory)
    def tickle(self):
        self.status = tickled
        self.move_to(tickled_directory)
    def get_status(self):
        status_and_path = self.status_part_of_path()
        log(u'Project with status %s'%status_and_path)
        status_string = status_and_path[0]
        log(u'Project with status %s'%status_string)
        if status_string == '':
            return processed
        else:
            return project_dir_status_map[status_string[1:]]
    def status_part_of_path(self):
        split_path = self.path().split('/')
        project_index = split_path.index('@Projects')
        if project_index == len(split_path)-1 or not split_path[project_index+1][0]=='@':
            return ['']+split_path[project_index+1:]
        else:
            return split_path[project_index+1:]
    def date_of_last_activity(self):
        file_name = self.complete_file_path.encode('utf-8')
        log(repr('Counting inactivity for %s.'%file_name),0)
        return os.path.getmtime(file_name)
    def days_since_last_activity(self):
        days = (time()-self.date_of_last_activity())/86400
        log(u'No activity since %s days in %s'%(days,self.name()),0)
        return days
    def scheduled_for_review(self):
        return self.path().endswith('@Review')
    def set_name(self,name):
        self.write()
        new_file_name = u'%s.prj'%u_join(self.path(),name)
        
        log(u'Renaming to %s'%new_file_name)
        os.renames(self.complete_file_path.encode('utf-8'),new_file_name.encode('utf-8'))
        self.complete_file_path = new_file_name
    def process(self):
        project_changed = False
        for action in self.get_actions():
            if (action.update()):
                    self.dirty = True
                    log(u'%s %s'%(status_string_map[action.status],action.description),2)
        self.write()
        if not self.has_active_actions():
            log(u'Inactive: %s'%self.name(),0)
            self.review()
            log(u'Review because of stalling: %s'%self.name(),0)
        days_since_last_activity = self.days_since_last_activity() 
        log(u'No change in %s since %s days.'%(self.name(),days_since_last_activity),0)
        
        if days_since_last_activity > inactivity_threshold:
            self.review()
            log(u'Review because of inactivity: %s'%self.name(),0)

class Projects:
    def __init__(self):
        self.root = project_directory
        self.reread()

        
    def reread(self):
        self.review_projects = None
        self.someday_projects = None
        self.tickled_projects = None
        self.processed_projects = None
    def read(self,root,recursive=False):
        if not os.path.exists(root.encode('utf-8')):
            return []
        all_projects = []
        for name in os.listdir(root.encode('utf-8')):
            log(repr(name))
            file_name = u_join(root,name.decode('utf-8'))
            log(u'Reading %s'%file_name)
            if recursive and os.path.isdir(file_name.encode('utf-8')):
                all_projects.extend(self.read(file_name, True))
            if name.endswith('.prj'):
                all_projects.append(Project(file_name))
        return all_projects
    def get_all_projects(self):
        return self.get_processed_projects() + self.get_review_projects() + \
            self.get_tickled_projects() + self.get_someday_projects()
    def get_active_projects(self):
        return self.get_processed_projects() + self.get_review_projects()
    def get_inactive_projects(self):
        return self.get_tickled_projects() + self.get_someday_projects()
    def get_processed_projects(self):
        if self.processed_projects == None:
            self.processed_projects = self.read(self.root)
        return self.processed_projects
    def get_review_projects(self):
        if self.review_projects == None:
            self.review_projects = self.read(review_directory)
        return self.review_projects
    def get_tickled_projects(self):
        if self.tickled_projects == None:
            self.tickled_projects = self.read(tickled_directory,True)
        return self.tickled_projects
    def get_someday_projects(self):
        if self.someday_projects == None:
            self.someday_projects = self.read(someday_directory,True)
        return self.someday_projects
    def add_project(self,project):
        self.processed_projects.insert(0,project)
        
    def process(self):
        log(u'Updating Projects:')
        for project in self.get_active_projects():
            log(project.name(),2)
            project.process()
        return True

def save_gui(object):
    object.old_gui = appuifw.app.body
    object.old_menu = appuifw.app.menu
    object.old_exit_key_handler = appuifw.app.exit_key_handler
    object.title=appuifw.app.title
    object.lock = Ao_lock()

def restore_gui(object):
    appuifw.app.body = object.old_gui
    appuifw.app.menu = object.old_menu
    appuifw.app.exit_key_handler = object.old_exit_key_handler
    appuifw.app.title = object.title

class SearchableListView(object):
    def __init__(self,title,entry_filters,binding_map):
        self.title = title
        self.binding_map = binding_map
        self.current_entry_filter_index = 0
        self.entry_filters = entry_filters
        self.filtered_list = self.entry_filters[0]
        self.widgets = self.generate_widgets()
        self.view = appuifw.Listbox(self.all_widget_texts(),self.change_entry)

    def run(self):
        self.old_index = None
        self.adjustment = None
        appuifw.app.screen=read_config('screen').encode('utf-8')
        save_gui(self)
        appuifw.title=self.title
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
        self.view.set_list(self.all_widget_texts(),index)

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
        if index < 0 or index >= len(self.widgets):
            return

        if self.should_bindings_change(self.old_index,self.selected_index()):
            self.set_bindings_for_selection(index)
        self.old_index = self.selected_index()

    def exit(self):
        self.lock.signal()
        appuifw.app.body=self.old_gui
        appuifw.app.menu=self.old_menu
        appuifw.app.exit_key_handler = self.old_exit_key_handler
    def search_item(self):
        selected_item = appuifw.selection_list(self.all_widget_texts(),search_field=1)
        if selected_item == None:
            selected_item = self.selected_index()
        self.view.set_list(self.all_widget_texts(),selected_item)
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
    def should_bindings_change(self,old_index,new_index):
        return True
        # TODO Return True only if necessary

    def change_entry(self):
        self.exec_if_function_exists('change')
    def remove_entry(self):
        if self.function_exists('remove'):
            self.exec_and_update('remove')
            #self.entries.remove(self.selected_index())
    def execute_and_update(self,function):
        return lambda: (function(),log(u'Called %s'%function),self.update_existing_widgets(),self.index_changed())
    def change_status(self):
        self.exec_if_function_exists('change_status')

class ProjectListView(EditableListView):
    def __init__(self,projects):
        self.projects = projects
        super(ProjectListView, self).__init__(u'Projects', [projects.get_active_projects,projects.get_all_projects,projects.get_inactive_projects],PROJECT_LIST_KEYS_AND_MENU)
    def add_project(self,project):
        self.projects.add_project(project)
        self.reread_widgets()
    def generate_widgets(self):
        widgets = []
        widgets.append(NewProjectWidget(self))
        widgets.append(NoProjectWidget())
        widgets.extend([ProjectWidget(project) for project in self.filtered_list()])
        try:
            widgets.extend([SMSWidget(sms_id,self.projects) for sms_id in Inbox(EInbox).sms_messages()])
        except Exception,e:
            log(u'No permission to access SMS inbox')
            log(unicode(repr(e.args)))
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
                project.add_info(line)
            self.projects.insert(0,project)
    def sender(self):
        return INBOX.address(self.sms_id)
    def list_repr(self):
        return u'SMS from %s'%self.sender()
    def view_sms(self):
        save_gui(self)
        t = appuifw.Text()
        t.add(self.list_repr())
        t.add(u':\n')
        t.add(self.content())
        appuifw.app.menu=[(u'Create Project', self.create_project),
                        (u'Exit', self.exit_sms_view)]

        appuifw.title=self.list_repr()
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
        return u'No project (R U Sure?)'

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
            self.project.add_info(info)
            self.project.write()
    def review(self):
        self.project.review()
    def unreview(self):
        self.project.unreview()
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
    def change_status(self):
        status = self.project.get_status()
        if status == processed:
            self.project.review()
        elif status == inactive:
            self.project.tickle()
        elif status == tickled:
            self.project.set_someday()            
        else:
            self.project.unreview()

class ActionListView(EditableListView):
    def __init__(self,project):
        self.project = project
        super(ActionListView, self).__init__(u'Actions and Info', [self.project.not_done_actions,self.project.get_actions,self.project.inactive_actions], ACTION_LIST_KEYS_AND_MENU)

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
            self.project.add_info(info,position)



class ActionWidget:
    def __init__(self,action,project):
        self.action = action
        self.project = project
    def action_done(self):
        self.action.done()
    def action_to_info(self):
        self.project.remove_action(self.action)
        self.project.add_info(self.action.context_description_info())
    def change(self):
        change_description_for_action(self.action)
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
    def change_status(self):
        
        if self.action.status in [unprocessed,inactive]:
            self.action.process()
        elif self.action.status == processed:
            self.action.done()
        elif self.action.status == done:
            self.action.deactivate()
    def list_repr(self):
        return u'  %s %s'%(self.action.status_string(),self.action.description)

class InfoWidget:
    def __init__(self,info,project):
        self.info = info
        self.project = project
    def remove(self):
        self.project.remove_info(self.info)
    def change_status(self):
        self.project.remove_info(self.info)
        action = parse_action(self.info)
        action.project=self.project.name()
        action.process()
        self.project.add_action(action)
    def change(self):
        new_info=ask_for_info(self.info)
        if new_info:
            self.project.remove_info(self.info)
            self.project.add_info(new_info)
    def list_repr(self):
        return u'  %s'%self.info

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



def new_project(proposed_name=u'',info=None):
    if not info:
        info = u'Enter a name for the project'
    project_name = appuifw.query(info,'text',proposed_name.encode('utf-8'))
    if not project_name:
        return None
    log(u'New project %s'%project_name)
    project_file_name = (project_directory+project_name+'.prj') #.encode( "utf-8" )
    project = Project(project_file_name)
    project.dirty=True
    return project

#def new_action(projects):
#    names = [project.name() for project in projects]
#    names.insert(0, u'New Project')
#    selected_project = appuifw.selection_list(names,search_field=1)
#    if (selected_project == None):
#        return False
#    if (selected_project == 0):
#        pass
#    else:
#        project = projects[selected_project-1]
#        log(u'Project %s'%project.name())
#    if(not project in projects):
#        projects.insert(0,project)
#    (action,info)=ask_for_action_or_info(project.name())
#    if action==None and info==None:
#        pass
#    elif info==None:
#        add_action_to_project(action,project)
#    else:
#        project.get_infos().append(info)
#        log(u'Added info %s'%info,1)
#    project.dirty=True
#    project.write()
#    log('Project written',2)
#    return True

def add_action_to_project(action,project):
    action.process()
    log(u'Added action %s'%action.description,1)
    project.add_action(action)
    project.write()
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


def parse_lines(lines):
    actions = []
    infos = []
    for line in lines:
        if len(line) < 3:
            continue
        elif line[0]=='#':
            infos.append(line[1:].strip())
        else:
            actions.append(parse_action(line))
    return (actions,infos)


def parse_action(string):
    matching = action_regexp.match(string)
    description = matching.group('description').rstrip(u' \r\n')
    status_string = matching.group('status')
    if (status_string == None):
        status_string = u''
    status = sign_status_map[status_string]
    info = matching.group('info')
    context = parse_context(matching.group('context'))
    if(info==None):
        info=u''
    return Action(description,context,u'',info,status)
def parse_context(context):
    context_matching = context_regexp.match(context)
    context_numbers = context_matching.group('numbers')
    context_text = context_matching.group('text')
    if(context_numbers in ABBREVIATIONS):
        context=(unicode(ABBREVIATIONS[context_numbers])+context_text).rstrip(u'/')
    else:
        context=context_text
    if (len(context)<2):
        context = u'None'
    return context

def compare_by_status(x,y):
    return y.status - x.status



lock=None
def no_action():
    pass
def exit():
    appuifw.app.body.add('Exit')
    appuifw.app.body=None
    lock.signal()
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

def applicable_functions(obj,allowed_function_names):
    function_names = [function_name for function_name in dir(obj) if function_name in allowed_function_names]
    return [eval('obj.%s'%function_name) for function_name in function_names]

try:

    ABBREVIATIONS = read_configuration(gtd_directory+"abbreviations.cfg")
    PROJECT_LIST_KEYS_AND_MENU = read_configuration(gtd_directory+"projects.cfg",True)
    ACTION_LIST_KEYS_AND_MENU = read_configuration(gtd_directory+"actions.cfg",True)
    log(u'Configuration')
    log(repr(COMMON_CONFIG))
    log(u'Abbreviations')
    log(repr(ABBREVIATIONS))
    log(u'Keys and Menus')
    log(repr(ACTION_LIST_KEYS_AND_MENU))
    projects = Projects()
    projects_view = ProjectListView(projects)
    projects_view.run()
except Exception, e:
    error_text = unicode(repr(e.args))
    t = appuifw.Text()
    t.add(error_text)
    for trace_line in traceback.extract_tb(sys.exc_info()[2]):
        formatted_trace_line = u'\nIn %s line %s: %s "%s"'%trace_line
        log(formatted_trace_line,1)
        t.add(formatted_trace_line)
    appuifw.app.menu=[(u'Exit', exit)]

    appuifw.title=u'Error'
    appuifw.app.body=t
    lock = Ao_lock()
    appuifw.app.exit_key_handler=exit
    lock.wait()

log_file.close()
