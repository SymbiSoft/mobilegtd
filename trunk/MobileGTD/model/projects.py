from project import Project


class Projects:
    def __init__(self,project_directory):
        self.review_directory = project_directory+'@Review/'
        self.done_directory = project_directory+'@Done/'
        self.someday_directory = project_directory+'@Someday/'
        self.tickled_directory = project_directory+'@Tickled/'
        self.project_dir_name = '@Projects/'

        self.tickle_times=None
        self.someday_contexts=None

        self.root = project_directory
        self.processed_projects = []
        self.review_projects = []
        self.someday_projects = []
        self.tickled_projects = []
        self.observers = []
    def attach(self, observer):
        if not observer in self.observers:
            self.observers.append(observer)

    def detach(self, observer):
        try:
            self.observers.remove(observer)
        except ValueError:
            pass

    def notify(self, modifier=None):
        for observer in self.observers:
            if modifier != observer:
                observer.update(self)
    
    def reread(self):
        self.processed_projects = None
        self.review_projects = None
        self.someday_projects = None
        self.tickled_projects = None
        self.tickle_times = None
        self.someday_contexts = None
        
    def get_tickle_times(self):
        if self.tickle_times == None:
                self.tickle_times=map(make_string_stripper(self.tickled_directory+'/'),io.list_dir(self.tickled_directory,True,io.is_dir))
        return self.tickle_times
    def get_someday_contexts(self):
        if self.someday_contexts == None:
            self.someday_contexts=map(make_string_stripper(self.someday_directory+'/'),io.list_dir(self.someday_directory,True,io.is_dir))
        return self.someday_contexts
        #self.notify()
    def read(self,root,recursive=False):
        # TODO Use generic read function
        return [Project(project_name) for project_name in io.list_dir(root, recursive, lambda name: name.endswith('.prj'))]
    def get_all_projects(self):
        return self.get_active_projects() + self.get_review_projects() + \
            self.get_tickled_projects() + self.get_someday_projects()
    def get_current_projects(self):
        return self.get_active_projects() + self.get_review_projects()
    def get_inactive_projects(self):
        return self.get_tickled_projects() + self.get_someday_projects()
    def get_active_projects(self):
        if self.processed_projects == None:
            self.processed_projects = self.read(self.root)
        return self.processed_projects
    def get_review_projects(self):
        if self.review_projects == None:
            self.review_projects = self.read(self.review_directory)
        return self.review_projects
    def get_tickled_projects(self):
        if self.tickled_projects == None:
            self.tickled_projects = self.read(self.tickled_directory,True)
        return self.tickled_projects
    def get_someday_projects(self):
        if self.someday_projects == None:
            self.someday_projects = self.read(self.someday_directory,True)
        return self.someday_projects
    def get_current_tickled_projects(self):
        current_tickled_projects = []
        tickled_projects = self.get_tickled_projects()
        for project in tickled_projects:
            if project.should_not_be_tickled():
                current_tickled_projects.append(project)
        return current_tickled_projects
                
    def add_project(self,project):
        # Projects are not being reread
        if self.processed_projects:
            self.get_active_projects().insert(0,project)
    def create_project(self,project_name):
        project_file_name = (project_directory+project_name+'.prj')
        project = Project(project_file_name)
        project.dirty=True
        project.write()
        self.add_project(project)
        return project


    def process(self):
        ##logger.log(u'Starting to process')

        self.reread()
        ##logger.log('Searching for projects without next action')
        for project in self.get_active_projects():
            #logger.log(project.name(),2)
            self.process_project(project)
        ##logger.log('Searching for projects that should be untickled')
        for project in self.get_current_tickled_projects():
            self.review(project)
            project.activate()
        ##logger.log('Removing obsolete tickle directories')
        for tickle_dir in self.get_tickle_times():
            if TickleDirectory(tickle_dir).is_obsolete():
                try:
                    os.removedirs(u'%s/%s'%(self.tickled_directory,tickle_dir))
                except OSError:
                    pass
            
        self.reread()
        self.notify()

    def process_project(self,project):
        is_active = project.process()
        if not is_active:
            self.review(project)
        
    def update_status(self,project):
        if project.has_active_actions() and project.get_status()==inactive:
            self.activate(project)
        elif not project.has_active_actions() and project.get_status() == processed:
            self.review(project)
    
    def review(self,project):
        project.move_to(self.review_directory)
    def set_done(self,project):
        project.inactivate()
        project.move_to(self.done_directory)
    def activate(self,project):
        project.move_to(self.root)

    def defer(self,project,context=''):
        project.inactivate()
        project.move_to(u'%s/%s'%(self.someday_directory,context))
    def tickle(self,project,time=''):
        project.inactivate()
        project.move_to(u'%s/%s'%(self.tickled_directory,time))
