import appuifw
from project_widget import ProjectWidget
from model.info import Info
class NewProjectWidget:
    def __init__(self,projects):
        self.projects = projects
    def change(self,proposed_name = 'Project name',infos=None):
        project_name = appuifw.query(u'Enter a name for the project','text',proposed_name)
        if not project_name:
            return
        project = self.projects.create_project(project_name)
        if infos:
            for info in infos:
                project.add_info(Info(info))
        ProjectWidget(self.projects,project).change()
        return project

    def list_repr(self):
        return u'New project'
    def name_and_details(self):
        return (self.list_repr(), u'')
