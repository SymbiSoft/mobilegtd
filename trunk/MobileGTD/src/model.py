unprocessed = 0
processed = 1
done = 2
tickled = 3
inactive = 4
someday = 5
info = 2
def add_action_to_project(action,project):
    action.process()
    logger.log(u'Added action %s'%action.description,1)
    project.add_action(action)
    project.write()
def compare_by_status(x,y):
    return y.status - x.status


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
