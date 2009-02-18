import unittest
from mock import Mock,patch_object,patch
from persistence.projects_directory import ProjectsDirectory
from file_based_spec import FileSystemBasedBehaviour
from model.project import Project,active
from persistence.project_file import ProjectFile
from persistence import project_file
from sets import Set
class ProjectsDirectoryBehaviour(FileSystemBasedBehaviour):

    def setUp(self):
        super(ProjectsDirectoryBehaviour,self).setUp()
        self.projects = Mock()
        self.project_list = []
        self.projects.__iter__ = self.project_list.__iter__
        self.projects_directory = ProjectsDirectory(self.projects)
        self.projects_directory.add_directory('.')

    def create_project_file(self,name,subdir=None):
        file_name = name+'.prj'
        if subdir:
            filename = os.path.join(subdir,file_name)
        self.create_file(file_name)

    def assert_project_added(self,project_name):
        calls = self.projects.append.call_args_list
        self.assertTrue(((Project(project_name,active),),{}) in calls,"Project %s was not created:\n%s"%(repr(Project(project_name)),calls))

#        self.projects.append.assert_called_with(Project(project_name))

    def test_should_register_itself_as_observer(self):
        self.projects.observers.append.assert_called_with(self.projects_directory)

    def read(self):
        self.projects_directory.read()
        


class EmptyProjectsDirectoryBehaviour(ProjectsDirectoryBehaviour):

    def test_should_not_read_any_projects(self):
        self.read()
        self.assertFalse(self.projects.append.called)


        
class NonEmptyProjectsDirectoryBehaviour(ProjectsDirectoryBehaviour):

    def setUp(self):
        super(NonEmptyProjectsDirectoryBehaviour,self).setUp()
        self.project_names = Set(['First Project','other project','third something'])
        self.create_project_files(self.project_names)

    
    def create_project_files(self,names):
        for name in names:
            self.create_project_file(name)

    def test_should_read_all_projects_in_this_directory(self):
        self.read()
        for p in self.project_names:
            self.assert_project_added(p)

    def test_should_read_only_project_files(self):
        self.create_file('First something.txt')
        self.read()
        self.assertEqual(len(self.projects.append.call_args_list),len(self.project_names))
        self.assertFalse(((Project('First something.txt'),),{}) in self.projects.append.call_args_list)

    def has_project_file(self,p):
        has_project_file = False
        for o in p.observers:
            if type(o) == ProjectFile:
                if has_project_file:
                    self.fail("Added ProjectFile twice")
                has_project_file = True
        return has_project_file

    def test_should_add_read_projects_to_projects(self):
#        self.projects.append.side_effect = self.mock_notify
        self.read()
        read_project_names = Set()
        for call in self.projects.append.call_args_list:
            read_project_names.add(call[0][0].name)
        self.assertEqual(read_project_names,self.project_names)

    def test_should_clear_the_projects_before_reading(self):
        self.read()
        self.read()
        self.assertEqual(len(self.projects.pop.call_args_list),len(self.project_names))

    def test_should_create_project_files_when_notified_of_added_projects(self):
        p = Mock()
        p.observers = []
        self.projects_directory.notify(self.projects,'add_item',p, None)
        self.assertTrue(self.has_project_file(p),"Should have registered ProjectFile on 'add_project' notification")

    @patch('persistence.project_file.read')
    def test_should_make_the_project_file_read_the_file_contents(self,read_method):
        read_method.return_value=(None,[],[])
        self.read()
        self.assertEqual(len(read_method.call_args_list),len(self.project_names))
        