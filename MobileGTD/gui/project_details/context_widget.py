class ContextWidget:
    def __init__(self,context,project):
        self.context = context
        self.project = project
    def change(self):
        action = Action(self.project.name(),self.context,self.project.name())
        if edit_action(action):
            action.process()
            self.project.add_action(action)
    def list_repr(self):
        return u'@%s'%self.context
