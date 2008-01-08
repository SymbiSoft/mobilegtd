import os,re,codecs,sys,appuifw,traceback
from inbox import EInbox,Inbox
from e32 import Ao_lock
from key_codes import *
import key_codes
#import appswitch
from time import *

main_config_file = 'C:/System/Data/mobile_gtd.cfg'

default_configuration = {"screen":"normal",
"path":"C:/Data/GTD/",
"inactivity_threshold":"7"
}

default_actions_menu = {
"switch_entry_filter":"1,Toggle Active/All/Inactive Actions",
"add_action":"2,Add Action",
"add_info":"4,Add Info",
"change_context":"5,Change Context",
"change_status":"7,Change Status",
"change":"8,Change Text",
"add_action_to_context":"9,Add Action to Context",
"search_item":"0,Search Item",
"remove_entry":"Backspace,Remove Item",
}

default_projects_menu = {
"switch_entry_filter":"1,Toggle Active/All/Inactive Projects",
"activate":"2,Schedule as active",
"defer":"3,Defer Project",
"reread_projects":"4,Reread Projects",
"process":"5,Process Project",
"process_all":"6,Process all Projects",
"review":"7,Review Project",
"tickle":"8,Tickle project",
"rename":"9,Rename project",
"search_item":"0,Search Item",
"remove":"Backspace,Set project to done"
}


default_abbreviations = {
"1":"Agenda/",
"2":"Computer/",
"26":"Computer/Online/",
"26":"Computer/Online/Mail ",
"3":"Errands/",
"4":"Anywhere/",
"42":"Anywhere/Brainstorm/",
"47":"Anywhere/Phone/",
"46":"Anywhere/MobilePhone/",
"9":"WaitingFor/"
}

def u_join(father,son):
    return u'%s/%s'%(father,son)


console_log_level = 2
file_log_level = 5


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

def safe_chdir(path_unicode):
    try:
        path = path_unicode.encode('utf-8')
    except UnicodeError:
        logger.log('Error decoding path %s'%repr(path_unicode))
        return
    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)

def write(file_path,content):
        safe_chdir(os.path.dirname(file_path.encode('utf-8')))
        f = file(os.path.basename(file_path.encode('utf-8')),'w')
        f.write(content.encode('utf-8'))
        f.close()

def list_dir(root,recursive=False,filter=None):
    if not os.path.exists(root.encode('utf-8')):
        return []
    all_files_and_dirs = []
    for name in os.listdir(root.encode('utf-8')):
        file_name = u_join(root,name.decode('utf-8'))
        if recursive and os.path.isdir(file_name.encode('utf-8')):
            all_files_and_dirs.extend(list_dir(file_name, True,filter))
        if filter and filter(file_name):
            all_files_and_dirs.append(file_name)
    return all_files_and_dirs

class FileLogger:
    def __init__(self,file_path=u'C:/mobile_gtd.log',log_level = 8):
        self.entries = []
        self.file_path = file_path
        self.log_level = log_level
        write(file_path,u'')
        self.log_file = file(file_path.encode('utf-8'),'w')
    def log(self,text,level=0):
        if level < self.log_level:
            self.log_file.write(text.encode('utf-8')+'\n')

    def close(self):
        self.log_file.close()

class ConsoleLogger:
    def __init__(self,log_level = 8):
        self.log_level = log_level
    def log(self,text,level=0):
        if level < self.log_level:
            appuifw.note(u''+repr(text))
    def close(self):
        pass

def guess_encoding(data):
    encodings = ['ascii','utf-8','utf-16']
    successful_encoding = None
    if data[:3]=='\xEF\xBB\xBF':
        logger.log('Unicode BOM in %s'%repr(data),6)
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
        #logger.log('Decoded %s to %s'%(repr(data),repr(decoded)),6)
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


class odict(dict):
    def __init__(self):
        self._keys = []
        dict.__init__(self)

    def __setitem__(self, key, item):
        dict.__setitem__(self, key, item)
        if key not in self._keys: self._keys.append(key)

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys
    def __repr__(self):
        return repr(self.items())

    def values(self):
        return map(self.get, self._keys)








class Configuration(odict):
    def __init__(self,complete_file_path,defaults={}):
        odict.__init__(self)
        self.file_path=complete_file_path
        self.read()
        if self.merge(defaults):
            self.write()
            self.read()
    def read(self):
        if not os.path.isfile(self.file_path.encode('utf-8')):
            logger.log(u'Configuration file %s does not exist'%self.file_path)
            return
        for line in parse_file_to_line_list(self.file_path):
            if len(line)<1:continue
            if line[0] == '#': continue
            matching = configuration_regexp.match(line)
            key = matching.group('key')
            value = matching.group('value').rstrip(u' \r\n')
    
            self[key]=self.parse_value(value)
    def parse_value(self,value):
        if ',' in value:
            value=value.split(',')
        return value

    def merge(self, other):
        changed = False
        for key in other:
            if key not in self:
                self[key] = other[key]
                changed = True
        return changed

                
    def write(self):
        content = u'\n'.join([u'%s:%s'%(key,self.format_value(value)) for (key,value) in self.items()])
        write(self.file_path,content)
    def format_value(self,value):
        if isinstance(value,list):
            return ','.join(value)
        else:
            return value
        
logger=FileLogger()
COMMON_CONFIG = Configuration(main_config_file,default_configuration)


      

gtd_directory = COMMON_CONFIG['path']
logger=FileLogger(gtd_directory+'gtd.log','w')
inactivity_threshold = int(COMMON_CONFIG['inactivity_threshold'])
project_directory = gtd_directory+'@Projects/'
review_directory = project_directory+'@Review/'
done_directory = project_directory+'@Done/'
someday_directory = project_directory+'@Someday/'
tickled_directory = project_directory+'@Tickled/'
project_dir_name = '@Projects/'

if not os.path.exists(project_directory):
    os.makedirs(project_directory)





INBOX = Inbox(EInbox)
def is_dir(unicode_path):
    return os.path.isdir(unicode_path.encode('utf-8'))
def to_unicode():
    return lambda x:x.encode('utf-8')
def make_string_stripper(to_strip):
    return lambda x: x.replace(to_strip,'')
tickle_times=map(make_string_stripper(tickled_directory+'/'),list_dir(tickled_directory,True,is_dir))
someday_contexts=map(make_string_stripper(someday_directory+'/'),list_dir(someday_directory,True,is_dir))








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
        #logger.log( (u'Writing %s to %s'%(content,file_name)).encode('utf-8'),2)
        f.write(content)
        f.close()
    def move_to(self,directory):
        self.write()
        new_file_name = u_join(directory,self.file_name())
        old_file_name = u_join(self.path(),self.file_name())
        logger.log(u'Moving')
        logger.log(repr(old_file_name.encode('utf-8')))
        logger.log(repr(new_file_name.encode('utf-8')))
        os.renames(old_file_name.encode('utf-8'),new_file_name.encode('utf-8'))
        logger.log(u'Done moving')
        return new_file_name

class Info:
    def __init__(self,text=u''):
        self.text=unicode(text)
    def file_string(self):
        return u'# %s'%self.text

    def gui_string(self):
        return self.text

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
            logger.log('Processing %s'%self.description,3)
            self.process()
            return True
        elif(self.status == processed):
            file_name = self.file_name()
            path_and_file=u_join(context_path,file_name)
            logger.log(repr(path_and_file),4)

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
    def summary(self):
        return self.context_description_info().split(u'/')[-1]

class Project(WriteableItem):
    def __init__(self,file_name):
        self.complete_file_path=file_name
        self.actions=None
        self.infos=None
        self.dirty = False
        super(Project, self).__init__(self.get_status())
        logger.log(u'Project %s is %s'%(self.name(),self.status))
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
            lines.append(info.file_string())
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
        return self.status_string()+self.name() #+self.additional_info()
    def additional_info(self):
        # TODO
        status_part=self.status_part_of_path()
        if len(status_part)<=1:
            return u''
        else:
            return u'/'.join(status_part[2:])
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
    def activate(self):
        self.status = processed
        self.move_to(project_directory)
    def inactivate(self):
        for action in self.active_actions():
            action.deactivate()
        self.dirty = True
    def defer(self,context=''):
        self.inactivate()
        self.status = someday
        self.move_to(u'%s/%s'%(someday_directory,context))
    def tickle(self,time=''):
        self.inactivate()
        self.status = tickled
        self.move_to(u'%s/%s'%(tickled_directory,time))
    def get_status(self):
        status_and_path = self.status_part_of_path()
        logger.log(u'Project with status %s'%status_and_path)
        status_string = status_and_path[0]
        logger.log(u'Project with status %s'%status_string)
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
        logger.log(repr('Counting inactivity for %s.'%file_name),0)
        return os.path.getmtime(file_name)
    def days_since_last_activity(self):
        days = (time()-self.date_of_last_activity())/86400
        logger.log(u'No activity since %s days in %s'%(days,self.name()),0)
        return days
    def scheduled_for_review(self):
        return self.path().endswith('@Review')
    def set_name(self,name):
        self.write()
        new_file_name = u'%s.prj'%u_join(self.path(),name)
        
        logger.log(u'Renaming to %s'%new_file_name)
        os.renames(self.complete_file_path.encode('utf-8'),new_file_name.encode('utf-8'))
        self.complete_file_path = new_file_name
    def process(self):
        project_changed = False
        days_since_last_activity = self.days_since_last_activity() 
        if days_since_last_activity > inactivity_threshold:
            self.inactivate()
            self.review()
            logger.log(u'Review because of inactivity: %s'%self.name(),0)
        #logger.log(u'No change in %s since %s days.'%(self.name(),days_since_last_activity),0)

        for action in self.get_actions():
            if (action.update()):
                    self.dirty = True
                    logger.log(u'%s %s'%(status_string_map[action.status],action.description),2)
        self.write()
        if not self.has_active_actions():
            logger.log(u'Inactive: %s'%self.name(),0)
            self.review()
            logger.log(u'Review because of stalling: %s'%self.name(),0)
      

class Projects:
    def __init__(self):
        self.root = project_directory
        self.reread()
        self.status_to_list_map = { 
            processed :  self.processed_projects,
            unprocessed: self.review_projects,
            inactive :   self.review_projects,
            tickled:     self.tickled_projects,
            someday:     self.someday_projects,
            done: []
        }

        
    def reread(self):
        self.processed_projects = None
        self.review_projects = None
        self.someday_projects = None
        self.tickled_projects = None
    def read(self,root,recursive=False):
        # TODO Use generic read function
        return [Project(project_name) for project_name in list_dir(root, recursive, lambda name: name.endswith('.prj'))]
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
    def sort_projects(self):
        projects = self.get_all_projects()
        for project in projects:
           self.status_to_list_map[project.get_status()].append(project)
    def add_project(self,project):
        self.processed_projects.insert(0,project)
        
    def process(self):
        self.reread()
        logger.log(u'Updating Projects:')
        for project in self.get_active_projects():
            logger.log(project.name(),2)
            project.process()
        return True

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
#        logger.log(u'Project %s'%project.name())
#    if(not project in projects):
#        projects.insert(0,project)
#    (action,info)=ask_for_action_or_info(project.name())
#    if action==None and info==None:
#        pass
#    elif info==None:
#        add_action_to_project(action,project)
#    else:
#        project.get_infos().append(info)
#        logger.log(u'Added info %s'%info,1)
#    project.dirty=True
#    project.write()
#    logger.log('Project written',2)
#    return True

def add_action_to_project(action,project):
    action.process()
    logger.log(u'Added action %s'%action.description,1)
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
            infos.append(Info(line[1:].strip()))
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

    ABBREVIATIONS = Configuration(gtd_directory+"abbreviations.cfg",default_abbreviations)
    PROJECT_LIST_KEYS_AND_MENU = Configuration(gtd_directory+"projects.cfg",default_projects_menu)
    ACTION_LIST_KEYS_AND_MENU = Configuration(gtd_directory+"actions.cfg",default_actions_menu)
#    logger.log(u'Configuration')
#    logger.log(repr(COMMON_CONFIG))
#    logger.log(u'Abbreviations')
#    logger.log(repr(ABBREVIATIONS))
#    logger.log(u'Keys and Menus')
#    logger.log(repr(ACTION_LIST_KEYS_AND_MENU))
    projects = Projects()
    projects_view = ProjectListView(projects)
    projects_view.run()
except Exception, e:
    error_text = unicode(repr(e.args))
    t = appuifw.Text()
    t.add(error_text)
    for trace_line in traceback.extract_tb(sys.exc_info()[2]):
        formatted_trace_line = u'\nIn %s line %s: %s "%s"'%trace_line
        logger.log(formatted_trace_line,1)
        t.add(formatted_trace_line)
    appuifw.app.menu=[(u'Exit', exit)]

    appuifw.app.title=u'Error'
    appuifw.app.body=t
    lock = Ao_lock()
    appuifw.app.exit_key_handler=exit
    lock.wait()

logger.close()
