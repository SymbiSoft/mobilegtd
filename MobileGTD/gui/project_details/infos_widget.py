from model.info import Info
import project_view

class InfosWidget:
    def __init__(self,project):
        self.project = project
    def change(self):
        info = project_view.ask_for_info(self.project.name)
        if info:
            self.project.add_info(Info(info),0)
            self.project.dirty=True
    def list_repr(self):
        return u'Infos'
