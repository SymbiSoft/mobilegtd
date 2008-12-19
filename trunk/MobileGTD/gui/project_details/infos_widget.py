class InfosWidget:
    def __init__(self,project):
        self.project = project
    def change(self):
        info = ask_for_info(self.project.name())
        if info:
            self.project.add_info(model.Info(info),0)
            self.project.dirty=True
    def list_repr(self):
        return u'Infos'
