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
try:
    import e32
    from e32 import Ao_lock
    e32.ao_yield()
    #appuifw.note(u'Vor Imports')
    #display(sys.path)
    import config, defaultconfig
    
    import gui,model
    import io
    from config import *
    

    
    #import appswitch

    import os
    if not os.path.exists(project_directory):
        os.makedirs(project_directory)
    
    
    import logging
    from logging import logger
    logger.log_stderr()
    sys.stderr.write('stderr logged from default')

#    logger.log(u'Configuration')
#    logger.log(repr(COMMON_CONFIG))
#    logger.log(u'Abbreviations')
#    logger.log(repr(ABBREVIATIONS))
#    logger.log(u'Keys and Menus')
#    logger.log(repr(ACTION_LIST_KEYS_AND_MENU))
    projects = model.Projects(project_directory)
    projects_view = gui.ProjectListView(projects)
    projects_view.run()
    #logger.close()
except Exception, e:
    def display(objects):
        strings=[]
        for object in objects:
            strings.append(u'%s'%object)
        appuifw.selection_list(strings)
    import logging
    from logging import logger
    import appuifw,traceback
    error_text = unicode(repr(e.args))
    t = appuifw.Text()
    for trace_line in traceback.extract_tb(sys.exc_info()[2]):
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

logger.close()
#tr.stop()
