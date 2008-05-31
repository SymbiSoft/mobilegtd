# SYMBIAN_UID = 0xA0008CDC
# 0xA0008CDC
# 0x2001A1A0










def to_unicode():
    return lambda x:x.encode('utf-8')





lock=None
try:
    import e32
    import os,re,codecs,sys,appuifw,traceback
    e32.ao_yield()
    def display(objects):
        strings=[]
        for object in objects:
            strings.append(u'%s'%object)
        appuifw.selection_list(strings)
    from e32 import Ao_lock
    #appuifw.note(u'Vor Imports')
    #display(sys.path)
    sys.path.append('c:/python/')

    import logging
    from logging import logger
    
    import gui,model
    import config, defaultconfig
    import io
    from config import *
    
    
    
    #import appswitch

    if not os.path.exists(project_directory):
        os.makedirs(project_directory)
    
    
    
    

#    logger.log(u'Configuration')
#    logger.log(repr(COMMON_CONFIG))
#    logger.log(u'Abbreviations')
#    logger.log(repr(ABBREVIATIONS))
#    logger.log(u'Keys and Menus')
#    logger.log(repr(ACTION_LIST_KEYS_AND_MENU))
    projects = model.Projects(project_directory)
    projects_view = gui.ProjectListView(projects)
    projects_view.run()
except Exception, e:
    error_text = unicode(repr(e.args))
    t = appuifw.Text()
    t.add(error_text)
    for trace_line in traceback.extract_tb(sys.exc_info()[2]):
        formatted_trace_line = u'\nIn %s line %s: %s "%s"'%trace_line
        #logger.log(formatted_trace_line,1)
        t.add(formatted_trace_line)
    appuifw.app.menu=[(u'Exit', gui.exit)]

    appuifw.app.title=u'Error'
    appuifw.app.body=t
    lock = Ao_lock()
    #appuifw.app.exit_key_handler=gui.exit
    lock.wait()

#logger.close()
