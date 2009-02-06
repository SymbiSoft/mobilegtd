from action_view import edit_action
from model.action import *
class ActionWidget:
    def __init__(self,action,project):
        self.action = action
        self.project = project

    def change(self):
        if edit_action(self.action):
            self.project.dirty=True

    def change_status(self):
        
        if self.action.is_reviewable():
            self.action.status = active
        elif self.action.status == active:
            self.action.status = done
        elif self.action.status == done:
            self.action.status = inactive
    def list_repr(self):
        return str(self.action)
