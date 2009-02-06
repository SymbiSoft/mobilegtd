import appuifw #Only temporary
from model import project
class ProjectWidget:
    def __init__(self,projects,project):
        self.project = project
        self.projects = projects
    def change(self):
#        appuifw.note(u'Opening')
        from gui.project_details.project_view import ProjectView
        edit_view = ProjectView(self.project)
        edit_view.run()

    def add_action(self):
        action = ask_for_action(u'for project %s'%self.project.name())
        if action:
            action.process()
            add_action_to_project(action,self.project)
            self.project.write()

    def add_info(self):
        info = ask_for_info(self.project.name())
        if info:
            self.project.add_info(Info(info))
            self.project.write()
    def review(self):
        self.projects.review(self.project)
    def activate(self):
        self.project.status = project.active
    def process(self):
        appuifw.note(u'Processing %s'%self.project.name())
        self.projects.process(self.project)
        
    def rename(self):
        new_name = appuifw.query(u'Enter new project name','text',u'%s'%self.project.name())
        if new_name != None:
            self.project.set_name(new_name)
    def remove(self):
        self.project.status = project.done
    def list_repr(self):
        return self.project.status_symbol_and_name()
    def name_and_details(self):
        if self.project.has_active_actions():
            details=self.project.active_actions()[0].summary()
        else:
            details=u'Something' #self.project.additional_info()
        return (self.list_repr(),details)

    
    def tickle(self):
        self.choose_and_execute(self.projects.get_tickle_times(),self.projects.tickle)
    def defer(self):
        self.choose_and_execute(self.projects.get_someday_contexts(),self.projects.defer)
    def choose_and_execute(self,choices,function):
        if choices==None or len(choices)==0:
            function(self.project)
            return
        selected_item = appuifw.selection_list(choices,search_field=1)   
        
        if not selected_item==None:
            function(self.project,choices[selected_item])
        
    def review(self):
        self.projects.review(self.project)
