import appuifw
from log.logging import logger
from project_widget import ProjectWidget
from model.project import Project
from model.info import Info
class NewProjectWidget:
    def __init__(self,projects):
        self.projects = projects
    def change(self,proposed_name = 'Project name',infos=None):
        project_name = unicode(appuifw.query(u'Enter a name for the project','text',proposed_name))
        logger.log(u'New project: %s'% project_name)
        if not project_name:
            return
        project = Project(project_name)
        self.projects.append(project)
        if infos:
            for info in infos:
                project.add_info(Info(info))
        ProjectWidget(self.projects,project).change()
        return project

    def list_repr(self):
        return u'New project'
    def name_and_details(self):
        return (self.list_repr(), u'')
