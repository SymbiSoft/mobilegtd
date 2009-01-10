import re
from model import *

class ActionStatus:
    signs = {}
    def __init__(self,name,value=0,sign=u''):
        self.name = name
        self.value = value
        self.sign = sign
        ActionStatus.signs[sign] = self
    def __cmp__(self,other):
        if not other:
            return 1
        return other.value - self.value
        
    def sign(self):
        return self.sign
    
    def get_status(sign):
        return ActionStatus.signs[sign]
    get_status = staticmethod(get_status)



unprocessed = ActionStatus('unprocessed',0)
active = ActionStatus('active',1,u'-')
done = ActionStatus('done',2,u'+')
tickled = ActionStatus('tickled',3,u'/')
inactive = ActionStatus('inactive',4,u'!')
someday = ActionStatus('someday',5,u'~')
info = ActionStatus('info',0)

action_regexp = re.compile('(?P<status>[+-/!])?\s*(?P<context>\S*)\s*(?P<description>[^\(]*)(\((?P<info>[^\)]*))?',re.U)
context_regexp = re.compile('(?P<numbers>\d*)(?P<text>\D?.*)',re.U)
ABBREVIATIONS = {} # Configuration("abbreviations.cfg",default_abbreviations)

def parse_action_line(string):
    matching = action_regexp.match(string)
    description = matching.group('description').rstrip(u' \r\n')
    status_string = matching.group('status')
    if (status_string == None):
        status_string = u''
    status = ActionStatus.get_status(status_string)
    info = matching.group('info')
    context = parse_context(matching.group('context'))
    if(info==None):
        info=u''
    return context,description,info,status    


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


class Action(ObservableItem,ItemWithStatus):
    def parse(string):
        context,description,info,status  = parse_action_line(string)
        return Action(description,context,u'',info,status)
    
    parse = staticmethod(parse)
    
    def __init__(self,description,context,project=None,info=u'',status=unprocessed):
        super(Action, self).__init__()
        self.project = project
        self.description = description
        self.context = context
        self.info = info
        self.status = status
        
    def is_active(self):
        return self.status in [active,unprocessed]
    
    def is_reviewable(self):
        return self.status in [unprocessed,inactive]
    
    def is_not_done(self):
        return self.status in [active,unprocessed,inactive]
        
    def __repr__(self):
        advanced_info = ''
        if self.project and len(self.project)>0:
            advanced_info = advanced_info+' Project: '+self.project
        if len(self.info) > 0:
            advanced_info = advanced_info +' Info: '+self.info
        if len(advanced_info) > 0:
            advanced_info = '   ('+advanced_info+' )'
        return repr(self.description)+' @'+repr(self.context)+repr(advanced_info)
    
    def project_file_string(self,entry_separator=' '):
        return ('%s%s'%(self.status_string(),self.context_description_info())).strip()
    
    def context_description_info(self,entry_separator=' '):
        return u'%s%s%s%s%s'%(\
                self.context,entry_separator,\
                self.description,entry_separator,\
                self.info_string())

    def info_string(self,entry_separator=''):
        info_string = u''
        if (len(self.info) > 1):
            info_string = u'%s(%s)'%(entry_separator,self.info)
        return info_string

    def status_string(self):
        sign = self.status.sign
        if len(sign)>0:
            sign = sign+' '
        return sign
    def __cmp__(self,other):
        return self.status.__cmp__(other.status)


__all__ = ["Action","active","done","tickled","inactive","someday","info","unprocessed"]
