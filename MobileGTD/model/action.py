
action_regexp = re.compile('(?P<status>[+-/!])?\s*(?P<context>\S*)\s*(?P<description>[^\(]*)(\((?P<info>[^\)]*))?',re.U)
context_regexp = re.compile('(?P<numbers>\d*)(?P<text>\D?.*)',re.U)


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
