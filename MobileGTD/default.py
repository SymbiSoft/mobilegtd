import os,re,codecs,sys,appuifw,traceback
import mobilegtd
import mobilegtd.gui,mobilegtd.model
import mobilegtd.config, mobilegtd.defaultconfig
import mobilegtd.logging
import mobilegtd.io,mobilegtd.parsing,mobilegtd.keys



from inbox import EInbox,Inbox
from e32 import Ao_lock
from mobilegtd.config import *
from mobilegtd.logging import logger
#import appswitch










if not os.path.exists(project_directory):
    os.makedirs(project_directory)





INBOX = Inbox(EInbox)
def to_unicode():
    return lambda x:x.encode('utf-8')





lock=None
try:

#    logger.log(u'Configuration')
#    logger.log(repr(COMMON_CONFIG))
#    logger.log(u'Abbreviations')
#    logger.log(repr(ABBREVIATIONS))
#    logger.log(u'Keys and Menus')
#    logger.log(repr(ACTION_LIST_KEYS_AND_MENU))
    projects = mobilegtd.model.Projects(project_directory)
    projects_view = mobilegtd.gui.ProjectListView(projects)
    projects_view.run()
except Exception, e:
    error_text = unicode(repr(e.args))
    t = appuifw.Text()
    t.add(error_text)
    for trace_line in traceback.extract_tb(sys.exc_info()[2]):
        formatted_trace_line = u'\nIn %s line %s: %s "%s"'%trace_line
        logger.log(formatted_trace_line,1)
        t.add(formatted_trace_line)
    appuifw.app.menu=[(u'Exit', mobilegtd.gui.exit)]

    appuifw.app.title=u'Error'
    appuifw.app.body=t
    lock = Ao_lock()
    #appuifw.app.exit_key_handler=mobilegtd.gui.exit
    lock.wait()

logger.close()
