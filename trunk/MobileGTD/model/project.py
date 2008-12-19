from action import Action

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
def add_action_to_project(action,project):
	action.process()
    project.add_action(action)
    project.write()