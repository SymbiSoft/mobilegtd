import unittest
from mock import Mock
from persistence.projects_directory import ProjectsDirectory
from file_based_spec import FileSystemBasedBehaviour
from model.project import Project
class ProjectsDirectoryBehaviour(FileSystemBasedBehaviour):

    def setUp(self):
        super(ProjectsDirectoryBehaviour,self).setUp()
        self.projects = Mock()
        self.projects_directory = ProjectsDirectory(self.projects,'.')
        print repr(self.projects_directory)

    def create_project_file(self,name,subdir=None):
        file_name = name+'.prj'
        if subdir:
            filename = os.path.join(subdir,file_name)
        self.create_file(file_name)

    def assert_project_added(self,project_name):
        calls = self.projects.append.call_args_list
        self.assertTrue(((Project(project_name),),{}) in calls)

#        self.projects.append.assert_called_with(Project(project_name))
    
class EmptyProjectsDirectoryBehaviour(ProjectsDirectoryBehaviour):

    def test_should_not_read_any_projects(self):
        self.projects_directory.read()
        self.assertFalse(self.projects.append.called)


        
class NonEmptyProjectsDirectoryBehaviour(ProjectsDirectoryBehaviour):
    
    def create_project_files(self,names):
        for name in names:
            self.create_project_file(name)
        
    
    def test_should_read_all_projects_in_this_directory(self):
        project_names = ['First Project','other project','third something']
        self.create_project_files(project_names)
        self.projects_directory.read()
        for p in project_names:
            self.assert_project_added(p)

    def test_should_read_only_project_files(self):
        self.create_file('First something.txt')
        self.projects_directory.read()
        self.assertFalse(self.projects.append.called)
