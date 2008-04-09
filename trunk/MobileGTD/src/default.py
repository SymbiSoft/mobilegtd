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
