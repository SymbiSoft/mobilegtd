# SIS_VERSION = 0.8.1
                                             
import os,re,codecs,sys,appuifw,traceback
from inbox import EInbox,Inbox
from e32 import Ao_lock
from key_codes import *
import key_codes
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


sign_status_map = {u'+':done,u'-':processed,u'!':inactive,u'/':tickled,u'':unprocessed}
status_sign_map = invert_dictionary(sign_status_map)
status_string_map = {done:u'Done',processed:u'Processed',inactive:u'Inactive',tickled:u'Tickled',unprocessed:u'Unprocessed'}
project_dir_status_map = {u'Done':done,u'Review':inactive,u'Someday':someday}
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
    #print repr(file_name),type(file_name)
    f=file(unicode_file_name.encode('utf-8'),'r')
    raw=f.read()
    (text,encoding)=guess_encoding(raw)

    return text
def parse_file_to_line_list(unicode_complete_path):
    text = read_text_from_file(unicode_complete_path)
    #log(text)
    lines = text.splitlines()
    #print lines
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
    if not os.path.isfile(file_name):
        log(u'Configuration file %s does not exist'%file_name)
        return configuration
    for line in parse_file_to_line_list(file_name):
        if line[0] == '#': continue
        matching = configuration_regexp.match(line)
        key = matching.group('key')
        value = matching.group('value').rstrip(u' \r\n')
        if ',' in value:
            value=value.split(',')
        #if value=='':

        configuration[key]=value
    return configuration





main_config_file = 'C:/System/Data/mobile_gtd.cfg'

COMMON_CONFIG = read_configuration(main_config_file)
gtd_directory = COMMON_CONFIG['path'].encode('utf-8')
project_directory = gtd_directory+'@Projects/'
review_directory = project_directory+'@Review/'
done_directory = project_directory+'@Done/'
someday_directory = project_directory+'@Someday/'
project_dir_name = '@Projects/'

log_file=file(gtd_directory+'gtd.log','w')
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



def list_projects(root):
    all_projects =[]
    if not os.path.exists(root):
        return []
    for name in os.listdir(root):
        if (name.endswith('.prj')):
            project_file_name = unicode(os.path.join(root, name),file_name_encoding)
            #print repr(project)
            all_projects.append(Project(project_file_name))
        #print 'In '+root+' found ', all_files
    return all_projects

class ItemWithStatus(object):
    def __init__(self,status=unprocessed):
        self.status = status
    def status_string(self):
        if self.status == unprocessed:
            return u''
        else:
            return u'%s '%status_sign_map[self.status]
    
class Action(ItemWithStatus):

    def __init__(self,description,context,project,info='',status=unprocessed):
        super(Action, self).__init__(status)
        self.project = project
        self.description = description
        self.context = context
        self.info = info

    def update(self,path=gtd_directory):
        context_path = (u'%s/%s'%(path,self.context)).encode('utf-8')
        #log(repr(context_path),4)
        if (self.status == unprocessed):
            log('Processing %s'%self.description,3)
            self.process()
            return True
        elif(self.status == processed):
            file_name = self.proposed_file_name()
            path_and_file=os.path.join(context_path,file_name)
            log(repr(path_and_file),4)

            if not os.path.isfile(path_and_file):
                self.status = done
                return True
        return False
    def path(self,path=gtd_directory):
        return (u'%s/%s'%(path,self.context)).encode('utf-8')

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
    def write(self):
        safe_chdir(self.path())
        file_name = self.proposed_file_name()
        f = file(file_name,'w')
        f.write(self.action_file_string().encode('utf-8'))
        f.close()
    def path_and_file(self):
        return '%s/%s'%(self.path(),self.proposed_file_name())
    def remove(self):
        if os.path.isfile(self.path_and_file()):
            os.remove(self.path_and_file())
    def is_active(self):
        return self.status in [processed,unprocessed]
    def proposed_file_name(self):
        return (u'%s.act'%self.description).encode('utf-8')
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

    def action_file_string(self):
        string = self.project_file_string()
        if len(self.project)>0:
            string = string+u'\nProject: %s'%self.project
        return string
    def project_file_string(self,entry_separator=' '):
        return u'%s%s'%(self.status_string(),self.context_description_info())
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

class Project(ItemWithStatus):
    def __init__(self,file_name):
        self.file_name=file_name
        self.actions=None
        self.infos=None
        self.dirty = False
        super(Project, self).__init__(self.get_status_from_path())
        log(u'Project %s is %s'%(self.name(),self.status))

    def read(self):
        if not os.path.isfile(self.file_name.encode('utf-8')):
            self.actions=[]
            self.infos=[]
        else:
            action_strings = parse_file_to_line_list(self.file_name)
            #print action_strings
            (self.actions,self.infos) = parse_lines(action_strings)
            for action in self.actions:
                action.project = self.name()

    def write(self):
        lines = []
        for info in self.get_infos():
            lines.append((u'# %s\n'%info).encode('utf-8'))
        self.sort_actions()
        for action in self.get_actions():
            lines.append((u'%s\n'%action.project_file_string()).encode('utf-8'))
        log( u'Writing %s to %s'%(lines,self.file_name),2)
        f = file(self.file_name.encode('utf-8'),'w')
        f.writelines(lines)
        f.close()
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
    #   print "Here"
        matching = file_name_regexp.match(self.file_name)
        file_name=matching.group('file_name')
    #    print u"There he",file_name,u"is"
        return file_name
    def active_actions(self):
        return filter(lambda action: action.is_active() ,self.actions)
    def inactive_actions(self):
        return filter(lambda action: not action.is_active() ,self.actions)
    def add_action(self,action):
        self.get_actions().append(action)
        self.dirty = True
    def add_info(self,info):
        self.get_infos().append(info)
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
        return os.path.dirname(self.file_name)
    def file_name_without_path(self):
        return os.path.basename(self.file_name)
    def move_to(self,directory):
        self.write()
        new_file_name = directory+self.file_name_without_path()
        os.renames(self.file_name.encode('utf-8'),(new_file_name).encode('utf-8'))
        self.file_name = new_file_name
    def review(self):
        self.status = inactive
        self.move_to(review_directory)
    def set_done(self):
        self.status = done
        self.move_to(done_directory)
    def unreview(self):
        self.status = processed
        self.move_to(project_directory)
    def get_status_from_path(self):
        status_string = self.status_part_of_path()
        if status_string == 'Projects':
            return processed
        else:
            return project_dir_status_map[status_string]
    def status_part_of_path(self):
        return self.path().split('/')[-1][1:]
    def scheduled_for_review(self):
        return self.path().endswith('@Review')

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
    def __init__(self,title,binding_map):
        self.title = title
        self.binding_map = binding_map
        self.view = appuifw.Listbox(self.all_items(),self.change_entry)
    def run(self):
        self.old_index = None
        self.adjustment = None
        appuifw.app.screen=COMMON_CONFIG['screen'].encode('utf-8')
        save_gui(self)
        appuifw.title=self.title
        self.update()
        self.set_bindings_for_selection(0)
        appuifw.app.body=self.view

        appuifw.app.exit_key_handler=self.exit
        self.lock.wait()
    def exit(self):
        self.lock.signal()
        restore_gui(self)

    def update(self):
        self.items = self.all_items()
        index = self.selected_index()
        if index > len(self.items):
            index = len(self.items)
        self.view.set_list(self.items,index)

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

    def index_changed(self,adjustment=None):
        #log('Index changed with adjustment %s'%adjustment)
        if adjustment:
            index = self.selected_index() + adjustment
            #log('Cursor moving %s to %s'%(adjustment,index))
        else:
            index = self.selected_index()
        if index < 0 or index >= len(self.items):
            #log('Index %s out of bounds'%index)
            return

        if self.should_bindings_change(self.old_index,self.selected_index()):
            self.set_bindings_for_selection(index)
        #log('Index changed from %s to %s'%(self.old_index,self.selected_index()))
        self.old_index = self.selected_index()
    def exit(self):
        self.lock.signal()
        appuifw.app.body=self.old_gui
        appuifw.app.menu=self.old_menu
        appuifw.app.exit_key_handler = self.old_exit_key_handler
    def selected_index(self):
        return self.view.current()
    def search_item(self):
        selected_item = appuifw.selection_list(self.all_items(),search_field=1)
        if selected_item == None:
            selected_item = self.selected_index()
        self.view.set_list(self.all_items(),selected_item)
        self.set_bindings_for_selection(selected_item)
    def current_entry(self):
        return self.entries[self.selected_index()]


class EditableListView(SearchableListView):
    def __init__(self,title,binding_map):
        super(EditableListView, self).__init__(title,binding_map)
    
    def function_exists(self,function_name):    
        return function_name in dir(self.current_entry())
    
    def exec_if_function_exists(self,function_name):
        if self.function_exists(function_name):
            self.exec_and_update(function_name)
            
    def exec_and_update(self,function_name):
        entry = self.current_entry()
        exec('entry.%s()'%function_name)
        self.update()

    def key_and_menu_bindings(self,selected_index):
        key_and_menu_bindings=[]
        for function in applicable_functions(self.entries[selected_index],self.binding_map)+\
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
        return lambda: (function(),self.update(),self.index_changed())
    def all_items(self):
        self.update_entries()
        return [entry.list_repr() for entry in self.entries]

class ProjectListView(EditableListView):
    def __init__(self,project_search):
        self.project_search = project_search
        self.projects = self.project_search()
        #self.menu_bindings = [(description,eval('self.%s'%function)) for (function,(key,description)) in PROJECT_LIST_KEYS_AND_MENU.items()]
        super(ProjectListView, self).__init__(u'Projects', PROJECT_LIST_KEYS_AND_MENU)
        self.selected_project = 0

    def update_entries(self):
        self.entries = []
        self.entries.append(NewProjectEntry(self.projects))
        self.entries.append(NoProjectEntry())
        self.entries.extend([ProjectEntry(project) for project in self.projects])
        try:
            self.entries.extend([SMSEntry(sms_id,self.projects) for sms_id in Inbox(EInbox).sms_messages()])
        except Exception,e:
            log(u'No permission to access SMS inbox')
            log(unicode(repr(e.args)))
    def update_projects(self):
        self.projects = self.project_search()
        self.update()
    def process_all(self):
        appuifw.note(u'Processing all Projects')
        process(self.projects)
        self.update()


class SMSEntry:
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

class NoProjectEntry:
    def change(self):
        action = ask_for_action("No project")
        if action:
            action.process()

    def list_repr(self):
        return u'No project (R U Sure?)'

class NewProjectEntry:
    def __init__(self,projects):
        self.projects = projects
    def change(self):
        project = new_project()
        if project:
            self.projects.insert(0,project)
            project.write()
    def list_repr(self):
        return u'New project'

class ProjectEntry:
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
        #appuifw.note(u'Scheduling %s for Review'%self.project.name())
        self.project.review()
    def unreview(self):
        #appuifw.note(u'Scheduling %s as Active'%self.project.name())
        self.project.unreview()
    def process(self):
        appuifw.note(u'Processing %s'%self.project.name())
        process_project(self.project)
    def remove(self):
        self.project.set_done()
    def list_repr(self):
        return self.project.name_with_status()

class ActionListView(EditableListView):
    def __init__(self,project):
        self.project = project
        self.action_filters = [self.project.get_actions,self.project.active_actions,self.project.inactive_actions]
        self.current_action_filter_index = 0
        self.action_filter = self.project.get_actions
        super(ActionListView, self).__init__(u'Actions and Info',  ACTION_LIST_KEYS_AND_MENU)

    def exit(self):
        EditableListView.exit(self)
        self.project.write()

    def switch_action_filter(self):
        self.current_action_filter_index += 1
        self.action_filter = self.action_filters[self.current_action_filter_index % len(self.action_filters)]
        self.update()
    def actions(self):
        return self.action_filter()
    def infos(self):
        return self.project.get_infos()
    def update_entries(self):
        self.entries = []
        self.entries.append(InfosEntry(self.project))
        infos = self.infos()
        for info in infos:
            self.entries.append(InfoEntry(info,self.project))
        for (context,actions) in self.actions_by_context().items():
            self.entries.append(ContextEntry(context,self.project))
            for action in actions:
                self.entries.append(ActionEntry(action,self.project))

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
            self.project.add_info(info)
    def remove_entry(self):
        self.exec_if_function_exists('remove')
    def change_status(self):
        self.exec_if_function_exists('change_status')

class ActionEntry:
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
            self.action.context = parse_context(new_context)
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

class InfoEntry:
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

class ContextEntry:
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

class InfosEntry:
    def __init__(self,project):
        self.project = project
    def list_repr(self):
        return u'Infos'

def process(projects,path=gtd_directory):
    log(u'Updating Projects:')
    inactive_projects=[]
    for project in projects:
        process_project(project)
    return True

def process_project(project):
        project_changed = False
        #log(u'Updating %s'%project,1)
        for action in project.get_actions():
            #log(u'%s'%action,2)
            changed = action.update()
            if (changed):
                    project.dirty = True
                    log(u'%s %s'%(status_string_map[action.status],action.description),2)
        if project.dirty:
            log(project.name(),1)
            project.write()
        if not project.has_active_actions():
            log('Inactive: %s'%project.name(),0)
            project.review()
            #inactive_projects.append(project)

def new_project(proposed_name=u'',info=None):
    if not info:
        info = u'Enter a name for the project'
    project_name = appuifw.query(info,'text',proposed_name.encode('utf-8'))
    if not project_name:
        return None
    log(u'New project %s'%project_name)
    project_file_name = (project_directory+project_name+'.prj') #.encode( "utf-8" )
    project = Project(project_file_name)
    return project

def new_action(projects):
    names = [project.name() for project in projects]
    names.insert(0, u'New Project')
    selected_project = appuifw.selection_list(names,search_field=1)
    if (selected_project == None):
        return False
    if (selected_project == 0):
        pass
    else:
        project = projects[selected_project-1]
        log(u'Project %s'%project.name())
    if(not project in projects):
        projects.insert(0,project)
    (action,info)=ask_for_action_or_info(project.name())
    if action==None and info==None:
        pass
    elif info==None:
        add_action_to_project(action,project)
    else:
        project.get_infos().append(info)
        log(u'Added info %s'%info,1)

    project.write()
    log('Project written',2)
    return True

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
            break
        elif line[0]=='#':
            #print 'Comment %s'%line[1:]
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
        context=(ABBREVIATIONS[context_numbers]+context_text).rstrip(u'/')
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
#    key_values=[]
#    for key_name in all_key_names():
#        exec('key_values.append(%s)'%key_name)
    return key_values

def applicable_functions(obj,allowed_function_names):
    #log('Looking for functions for %s'%obj)
    function_names = [function_name for function_name in dir(obj) if function_name in allowed_function_names]
    return [eval('obj.%s'%function_name) for function_name in function_names]

try:

    ABBREVIATIONS = read_configuration(gtd_directory+"abbreviations.cfg")
    PROJECT_LIST_KEYS_AND_MENU = read_configuration(gtd_directory+"projects.cfg",True)
    ACTION_LIST_KEYS_AND_MENU = read_configuration(gtd_directory+"actions.cfg",True)
    #ACTION_LIST_MENU = read_configuration(gtd_directory+"actions.menu",True)
    log(u'Configuration')
    log(repr(COMMON_CONFIG))
    log(u'Abbreviations')
    log(repr(ABBREVIATIONS))
    log(u'Keys and Menus')
    log(repr(ACTION_LIST_KEYS_AND_MENU))
    all_projects=lambda:list_projects(project_directory)+list_projects(review_directory)
    projects_view = ProjectListView(all_projects)
    projects_view.run()
except Exception, e:
    error_text = unicode(repr(e.args))
    #log(error_text)
    t = appuifw.Text()
    t.add(error_text)
    for trace_line in traceback.extract_tb(sys.exc_info()[2]):
        formatted_trace_line = u'\nIn %s line %s: %s "%s"'%trace_line
        log(formatted_trace_line,1)
        t.add(formatted_trace_line)
        #(filename, line number, function name, text)
    appuifw.app.menu=[(u'Exit', exit)]

    appuifw.title=u'Error'
    appuifw.app.body=t
    lock = Ao_lock()
    appuifw.app.exit_key_handler=exit
    lock.wait()

log_file.close()
