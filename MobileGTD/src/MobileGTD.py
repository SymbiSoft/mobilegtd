import os,re,codecs,sys,appuifw,traceback
import gui,model,config,logging,io,parsing,keys
from inbox import EInbox,Inbox
from e32 import Ao_lock
from key_codes import *
import key_codes
#import appswitch
from time import *






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




if not os.path.exists(project_directory):
    os.makedirs(project_directory)





INBOX = Inbox(EInbox)
def to_unicode():
    return lambda x:x.encode('utf-8')
def make_string_stripper(to_strip):
    return lambda x: x.replace(to_strip,'')
tickle_times=map(make_string_stripper(tickled_directory+'/'),list_dir(tickled_directory,True,is_dir))
someday_contexts=map(make_string_stripper(someday_directory+'/'),list_dir(someday_directory,True,is_dir))













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



def compare_by_status(x,y):
    return y.status - x.status




def no_action():
    pass

def applicable_functions(obj,allowed_function_names):
    function_names = [function_name for function_name in dir(obj) if function_name in allowed_function_names]
    return [eval('obj.%s'%function_name) for function_name in function_names]

