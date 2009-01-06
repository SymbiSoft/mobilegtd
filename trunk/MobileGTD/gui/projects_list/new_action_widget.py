
class NewActionWidget:
    def change(self):
        from gui.project_details.project_view import ask_for_action
        action = ask_for_action(u"No project")
        if action:
            action.process()
        return action

    def list_repr(self):
        return u'New action'
    def name_and_details(self):
        return (self.list_repr(), u'Sure? No project attached?')
