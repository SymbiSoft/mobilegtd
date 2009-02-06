from model.action import Action
from action_view import edit_action
class ContextWidget:
    def __init__(self,context,project):
        self.context = context
        self.project = project
    def change(self):
        a = Action(self.project.name,self.context,self.project)
        if edit_action(a):
            self.project.add_action(a)
    def list_repr(self):
        return u'@%s'%self.context
