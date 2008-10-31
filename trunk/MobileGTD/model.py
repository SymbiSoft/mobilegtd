import io,os,re,config
from time import *

from logging import logger
from config import *
from io import *
unprocessed = 0
processed = 1
done = 2
tickled = 3
inactive = 4
someday = 5
info = 2
#logger.log(u'new version')
action_regexp = re.compile('(?P<status>[+-/!])?\s*(?P<context>\S*)\s*(?P<description>[^\(]*)(\((?P<info>[^\)]*))?',re.U)
context_regexp = re.compile('(?P<numbers>\d*)(?P<text>\D?.*)',re.U)

def make_string_stripper(to_strip):
    return lambda x: x.replace(to_strip,'')



def invert_dictionary(dictionary):
    return dict([[v,k] for k,v in dictionary.items()])

sign_status_map = {u'+':done,u'-':processed,u'!':inactive,u'/':tickled,u'':unprocessed,u'~':someday}
status_sign_map = invert_dictionary(sign_status_map)
status_string_map = {done:u'Done',processed:u'Processed',inactive:u'Inactive',tickled:u'Tickled',unprocessed:u'Unprocessed'}
project_dir_status_map = {u'Done':done,u'Review':inactive,u'Someday':someday,u'Tickled':tickled}
status_project_dir_map = invert_dictionary(project_dir_status_map)

file_name_regexp = re.compile('/?(?P<path>.*/)*(?P<file_name>.*)\....',re.U)

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

def parse_action_line(string):
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
    return context,description,info,status    

def parse_action(string):
    context,description,info,status  = parse_action_line(string)
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

def add_action_to_project(action,project):
    action.process()
    project.add_action(action)
    project.write()
def compare_by_status(x,y):
    return y.status - x.status


class ItemWithStatus(object):
    def status_string(self):
        status = self.get_status()
        if status == unprocessed:
            return u''
        else:
            return u'%s '%status_sign_map[status]


class WriteableItem(ItemWithStatus):
    def __init__(self):
        super(WriteableItem, self).__init__()
    def write(self):
        io.write(u'%s/%s'%(self.path(),self.file_name()),self.file_string())
    def move_to(self,directory):
        self.write()
        new_file_name = u_join(directory,self.file_name())
        old_file_name = u_join(self.path(),self.file_name())
        try:
            os.renames(old_file_name.encode('utf-8'),new_file_name.encode('utf-8'))
            ##logger.log(u'Moved %s to %s'%(repr(old_file_name),repr(new_file_name)))
            return new_file_name
        except OSError:
            #logger.log(u'Cannot move %s to %s: File already exists'%(repr(old_file_name),repr(new_file_name)))
            return old_file_name



class Info:
    def __init__(self,text=u''):
        self.text=unicode(text)
    def file_string(self):
        return u'# %s'%self.text

    def gui_string(self):
        return self.text

class Action(WriteableItem):
    def __init__(self,description,context,project,info=u'',status=unprocessed):
        super(Action, self).__init__()
        self.project = project
        self.description = description
        self.context = context
        self.info = info
        self.status = status
    def get_status(self):
        return self.status
    def update(self,path=gtd_directory):
        context_path = u_join(path,self.context)
        if (self.status == unprocessed):
            ##logger.log('Processing %s'%self.description,3)
            self.process()
            return True
        elif(self.status == processed):
            file_name = self.file_name()
            path_and_file=u_join(context_path,file_name)
            #logger.log(repr(path_and_file),4)

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
    def is_reviewable(self):
        return self.status in [unprocessed,inactive]
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
        super(Project, self).__init__()
        ##logger.log(u'Project %s is %s'%(self.name(),self.status))
        #self.read()
    def __eq__(self, project):
        return self.complete_file_path == project.complete_file_path
    def __ne__(self,project):
        return not self.__eq__(project)
    def read(self):
        if not os.path.isfile(self.complete_file_path.encode('utf-8')):
            self.actions=[]
            self.infos=[]
        else:
            action_strings = io.parse_file_to_line_list(self.complete_file_path)
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
        if self.get_status() == processed:
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
        return filter(lambda action: action.is_active() ,self.get_actions())
    def not_done_actions(self):
        return filter(lambda action: action.is_not_done() ,self.get_actions())
    def inactive_actions(self):
        return filter(lambda action: not action.is_active() ,self.get_actions())
    def add_action(self,action):
        self.get_actions().append(action)
        self.dirty = True
    def add_info(self,info,position=None):
        if position == None:
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
    def inactivate(self):
        for action in self.active_actions():
            action.deactivate()
        self.dirty = True
    def activate(self):
        for action in self.not_done_actions():
            action.process()
        self.dirty = True
        self.write()

    def get_status(self):
        status_and_path = self.status_part_of_path()
        status_string = status_and_path[0]
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
        #logger.log(repr('Counting inactivity for %s.'%file_name),3)
        return os.path.getmtime(file_name)
    def days_since_last_activity(self):
        days = (time()-self.date_of_last_activity())/86400
        #logger.log(u'No activity since %s days in %s'%(days,self.name()),3)
        return days
    def get_tickle_date(self):
        spp = self.status_part_of_path()
        return extract_datetime(spp)
    def should_not_be_tickled(self):
        tickle_path = u'/'.join(self.status_part_of_path()[-2:])
        return TickleDirectory(tickle_path).is_obsolete()
    def scheduled_for_review(self):
        return self.path().endswith('@Review')
    def set_name(self,name):
        self.write()
        new_file_name = u'%s.prj'%u_join(self.path(),name)
        
        #logger.log(u'Renaming to %s'%new_file_name)
        os.renames(self.complete_file_path.encode('utf-8'),new_file_name.encode('utf-8'))
        self.complete_file_path = new_file_name
    def process(self):

        for action in self.get_actions():
            if (action.update()):
                    self.dirty = True
        self.write()
        if not self.has_active_actions():
            return False
        days_since_last_activity = self.days_since_last_activity() 
        if days_since_last_activity > inactivity_threshold:
            return False
        return True
date_regexp = re.compile('(?P<number>\d{1,2})(\D.*)?\Z',re.U)
class TickleDirectory:
    
    def __init__(self,path):
        self.path = path
    def is_obsolete(self):
        import datetime
        date = self.date()
        if not date:
            # This directory is not a month-day directory
            return False
        obsolete = date <= datetime.datetime.now()
        return obsolete
    def date(self):
        import datetime
        spp = self.path.split(u'/')
        try:
            if len(spp) < 2 or len(spp[0]) == 0:
                month_match = date_regexp.match(spp[-1])
                if month_match == None:
                    return None
                month = int(month_match.group('number').rstrip(u' \r\n'))
                day = 1
            else:
                month_match = date_regexp.match(spp[-2])
                day_match = date_regexp.match(spp[-1])
                if month_match == None or day_match == None:
                    return None
                month = int(month_match.group('number').rstrip(u' \r\n'))
                day = int(day_match.group('number').rstrip(u' \r\n'))
        except ValueError:
            print repr(spp)
        return datetime.datetime(datetime.datetime.now().year,month,day)


class Projects:
    def __init__(self,project_directory):
        self.review_directory = project_directory+'@Review/'
        self.done_directory = project_directory+'@Done/'
        self.someday_directory = project_directory+'@Someday/'
        self.tickled_directory = project_directory+'@Tickled/'
        self.project_dir_name = '@Projects/'

        self.tickle_times=None
        self.someday_contexts=None

        self.root = project_directory
        self.processed_projects = []
        self.review_projects = []
        self.someday_projects = []
        self.tickled_projects = []
        self.observers = []
    def attach(self, observer):
        if not observer in self.observers:
            self.observers.append(observer)

    def detach(self, observer):
        try:
            self.observers.remove(observer)
        except ValueError:
            pass

    def notify(self, modifier=None):
        for observer in self.observers:
            if modifier != observer:
                observer.update(self)
    
    def reread(self):
        self.processed_projects = None
        self.review_projects = None
        self.someday_projects = None
        self.tickled_projects = None
        self.tickle_times = None
        self.someday_contexts = None
        
    def get_tickle_times(self):
        if self.tickle_times == None:
                self.tickle_times=map(make_string_stripper(self.tickled_directory+'/'),io.list_dir(self.tickled_directory,True,io.is_dir))
        return self.tickle_times
    def get_someday_contexts(self):
        if self.someday_contexts == None:
            self.someday_contexts=map(make_string_stripper(self.someday_directory+'/'),io.list_dir(self.someday_directory,True,io.is_dir))
        return self.someday_contexts
        #self.notify()
    def read(self,root,recursive=False):
        # TODO Use generic read function
        return [Project(project_name) for project_name in io.list_dir(root, recursive, lambda name: name.endswith('.prj'))]
    def get_all_projects(self):
        return self.get_active_projects() + self.get_review_projects() + \
            self.get_tickled_projects() + self.get_someday_projects()
    def get_current_projects(self):
        return self.get_active_projects() + self.get_review_projects()
    def get_inactive_projects(self):
        return self.get_tickled_projects() + self.get_someday_projects()
    def get_active_projects(self):
        if self.processed_projects == None:
            self.processed_projects = self.read(self.root)
        return self.processed_projects
    def get_review_projects(self):
        if self.review_projects == None:
            self.review_projects = self.read(self.review_directory)
        return self.review_projects
    def get_tickled_projects(self):
        if self.tickled_projects == None:
            self.tickled_projects = self.read(self.tickled_directory,True)
        return self.tickled_projects
    def get_someday_projects(self):
        if self.someday_projects == None:
            self.someday_projects = self.read(self.someday_directory,True)
        return self.someday_projects
    def get_current_tickled_projects(self):
        current_tickled_projects = []
        tickled_projects = self.get_tickled_projects()
        for project in tickled_projects:
            if project.should_not_be_tickled():
                current_tickled_projects.append(project)
        return current_tickled_projects
                
    def add_project(self,project):
        # Projects are not being reread
        if self.processed_projects:
            self.get_active_projects().insert(0,project)
    def create_project(self,project_name):
        project_file_name = (project_directory+project_name+'.prj')
        project = Project(project_file_name)
        project.dirty=True
        project.write()
        self.add_project(project)
        return project


    def process(self):
        ##logger.log(u'Starting to process')

        self.reread()
        ##logger.log('Searching for projects without next action')
        for project in self.get_active_projects():
            #logger.log(project.name(),2)
            self.process_project(project)
        ##logger.log('Searching for projects that should be untickled')
        for project in self.get_current_tickled_projects():
            self.review(project)
            project.activate()
        ##logger.log('Removing obsolete tickle directories')
        for tickle_dir in self.get_tickle_times():
            if TickleDirectory(tickle_dir).is_obsolete():
                try:
                    os.removedirs(u'%s/%s'%(self.tickled_directory,tickle_dir))
                except OSError:
                    pass
            
        self.reread()
        self.notify()

    def process_project(self,project):
        is_active = project.process()
        if not is_active:
            self.review(project)
        
    def update_status(self,project):
        if project.has_active_actions() and project.get_status()==inactive:
            self.activate(project)
        elif not project.has_active_actions() and project.get_status() == processed:
            self.review(project)
    
    def review(self,project):
        project.move_to(self.review_directory)
    def set_done(self,project):
        project.inactivate()
        project.move_to(self.done_directory)
    def activate(self,project):
        project.move_to(self.root)

    def defer(self,project,context=''):
        project.inactivate()
        project.move_to(u'%s/%s'%(self.someday_directory,context))
    def tickle(self,project,time=''):
        project.inactivate()
        project.move_to(u'%s/%s'%(self.tickled_directory,time))
# Public API
__all__= ('Projects',
          'Project',
          'Action',
          'Info',
          'unprocessed',
            'processed',
            'done',
            'tickled',
            'inactive',
            'someday',
            'info',
            'parse_action',
            'parse_action_line'
          
          )
