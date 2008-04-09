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







def no_action():
    pass

def applicable_functions(obj,allowed_function_names):
    function_names = [function_name for function_name in dir(obj) if function_name in allowed_function_names]
    return [eval('obj.%s'%function_name) for function_name in function_names]


lock=None
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
