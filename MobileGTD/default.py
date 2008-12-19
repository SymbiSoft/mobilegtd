# SYMBIAN_UID = 0xA0008CDC
# 0xA0008CDC
# 0x2001A1A0









def to_unicode():
    return lambda x:x.encode('utf-8')
import sys
from e32 import in_emulator
if in_emulator():
    sys.path.append('c:/python/')
#import traceS60
#tr=traceS60.trace() 
#tr.go()




lock=None
def run():
#try:
    import e32
    from e32 import Ao_lock
    e32.ao_yield()
    #appuifw.note(u'Vor Imports')
    #display(sys.path)
    import sys,os
#    pathname = os.path.dirname(sys.argv[0]) 
#    print pathname
#    print os.getcwd()  
#    for package in ['model','gui','config','io','logging']:
#        sys.path.append(os.path.abspath(pathname+'/'+package))
    
#    print sys.path

    import config.config, config.defaultconfig
    print "First imports done"
    
    import gui.gui
    from model.projects import Projects
    from gui.projects_list.project_list_view import ProjectListView
    print "Second imports done"
    import io.io
    print "Third imports done"
    from config.config import project_directory
    from config.config import gtd_directory
    print "Fourth imports done"

    
    #import appswitch

    import os
    if not os.path.exists(project_directory):
        os.makedirs(project_directory)
    
    
    import logging.logging
    from logging.logging import logger
    logger.log_stderr()
    sys.stderr.write('stderr logged from default')

#    logger.log(u'Configuration')
#    logger.log(repr(COMMON_CONFIG))
#    logger.log(u'Abbreviations')
#    logger.log(repr(ABBREVIATIONS))
#    logger.log(u'Keys and Menus')
#    logger.log(repr(ACTION_LIST_KEYS_AND_MENU))
    projects = Projects(project_directory)
    projects_view = ProjectListView(projects)
    projects_view.run()
    #logger.close()
#except Exception, e:
    import appuifw,traceback
    trace = traceback.extract_tb(sys.exc_info()[2])
    print e,trace
    def display(objects):
        strings=[]
        for object in objects:
            strings.append(u'%s'%object)
        appuifw.selection_list(strings)
    import logging
    from logging import logger
    
    error_text = unicode(repr(e.args))
    t = appuifw.Text()
    for trace_line in trace:
        formatted_trace_line = u'\nIn %s line %s: %s "%s"'%trace_line
        logger.log(formatted_trace_line,1)
        t.add(formatted_trace_line)
    logger.log(error_text,1)
    t.add(error_text)
    lock = Ao_lock()
    appuifw.app.menu=[(u'Exit', lock.signal)]

    appuifw.app.title=u'Error'
    appuifw.app.body=t
    #appuifw.app.exit_key_handler=gui.exit
    lock.wait()
run()
logger.close()
#tr.stop()
