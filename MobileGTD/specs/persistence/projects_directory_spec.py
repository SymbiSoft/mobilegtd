import unittest
from mock import Mock
from model.persistance.projects_directory import ProjectsDirectory
from file_based_spec import FileSystemBasedBehaviour
class ProjectsDirectoryBehaviour(FileSystemBasedBehaviour):
    def setUp(self):
        self.projects = Mock()
        self.projects_directory = ProjectsDirectory(self.projects,'.')
        print repr(self.projects_directory)
    
class EmptyProjectsDirectoryBehaviour(ProjectsDirectoryBehaviour):
    def test_should_not_read_any_projects(self):
        self.projects_directory.read()
        
        