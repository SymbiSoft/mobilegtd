from action_view import edit_action
from model.action import *
class ActionWidget:
    def __init__(self,action):
        self.action = action

    def change(self):
        if edit_action(self.action):
            self.action.status = active

    def change_status(self):
        
        if self.action.status == active:
            self.action.status = done
        elif self.action.status == done:
            self.action.status = inactive
        else:
            self.action.status = active
    def list_repr(self):
        return self.action.__str__()
