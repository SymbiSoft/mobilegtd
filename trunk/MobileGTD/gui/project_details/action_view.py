from log.logging import logger
from model.action import *
import appuifw

def edit_action(action):
    f = ActionView(action)
    f.execute()
    return f.isSaved() == 1

class ActionView( object ):
    
    def __init__( self, action):
        self.action = action
        self.saved = False
 

 
 
    ## Displays the form.
    def execute( self ):
        self.saved = False
        fields = [(u'Context','text',self.action.context),
        (u'Description','text',self.action.description),
        (u'Info','text',self.action.info)]
        logger.log(repr(fields))
        self.form = appuifw.Form(fields, appuifw.FFormEditModeOnly)
        
        self.form.save_hook = self.markSaved
        self.form.flags = appuifw.FFormEditModeOnly
        self.form.execute( )
        if self.saved:
            self.save_fields()
 
    def save_fields(self):
        context = self.get_context()
        if len(context.strip()) == 0:
            context,description,info,status = parse_action_line(self.get_description())
        else:
            description = self.get_description()
            context = parse_context(context)
            
        if len(self.get_info().strip()) > 0:
            info = self.get_info()
        else:
            info = u""
        self.action.context = context
        self.action.description = description
        self.action.info = info
        
    ## save_hook send True if the form has been saved.
    def markSaved( self, saved ):
        #appuifw.note(u'save_hook called with %s'%saved)
        
        if saved and self.is_valid():
            self.saved = True
        return self.saved
    def isSaved( self ):
        return self.saved
 
    def get_description( self ):
        return unicode(self.form[1][2])
 
 

    def get_context( self ):
        return unicode(self.form[0][2])
    def is_valid(self):
        return len(self.form[0]) > 2 and len(self.form[1]) > 2
 

    def get_info( self ):
        return unicode(self.form[2][2])
