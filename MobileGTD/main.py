# SYMBIAN_UID = 0xA0008CDC
# 0xA0008CDC
# 0x2001A1A0

#from logging import traceS60
#tr=traceS60.trace() 
#tr.go()

def run():
    import sys
    import e32
    if e32.in_emulator():
        sys.path.append('c:/python/')
        
        
    import os.path
    print sys.path
#    print os.path.dirname(__file__)
#    sys.path.append(os.path.dirname(__file__))
    import log.logging
    from log.logging import logger
    import sys,os
    logger.log_stderr()
    sys.stderr.write('stderr logged from default')
    
    
    
    lock=None
    
    from config.config import gtd_directory,read_configurations
    read_configurations()

    from inout.io import safe_chdir
    safe_chdir(gtd_directory)
    print os.getcwd() 
    try:
        e32.ao_yield()
        import sys,os
    
        import config.config, config.defaultconfig
        import gui.gui
        from model.projects import Projects
        from gui.projects_list.project_list_view import ProjectListView
        import inout.io
        from persistence.projects_directory import ProjectsDirectory
    
        directory = os.path.join(config.config.gtd_directory,'@Projects')

        projects = Projects()
        projects_directory = ProjectsDirectory(projects)
        projects_directory.add_directory(directory)
        projects_directory.add_directory(os.path.join(directory,'@Review'))
        projects_directory.read()
#        projects.process()
        projects_view = ProjectListView(projects)
        projects_view.run()
        #logger.close()
    except Exception, e:
        import appuifw,traceback
        trace = traceback.extract_tb(sys.exc_info()[2])
        print e,trace
        def display(objects):
            strings=[]
            for object in objects:
                strings.append(u'%s'%object)
            appuifw.selection_list(strings)
        
        error_text = unicode(repr(e.args))
        t = appuifw.Text()
        for trace_line in trace:
            formatted_trace_line = u'\nIn %s line %s: %s "%s"'%trace_line
            logger.log(formatted_trace_line,1)
            t.add(formatted_trace_line)
        logger.log(error_text,1)
        t.add(error_text)
        lock = e32.Ao_lock()
        appuifw.app.menu=[(u'Exit', lock.signal)]
    
        appuifw.app.title=u'Error'
        appuifw.app.body=t
        #appuifw.app.exit_key_handler=gui.exit
        lock.wait()

    logger.close()

if __name__ == "__main__":
    run()
#tr.stop()
