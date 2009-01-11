from mock import Mock
import file_based_spec
from persistence.project_file import ProjectFile
from model import project
from model import action
from model import info
import os


class ProjectFileBehaviour(file_based_spec.FileBasedBehaviour):

    def setUp(self):
        super(ProjectFileBehaviour,self).setUp()
        self.project = self.create_project()
        self.project_file = ProjectFile(self.project)

    def create_project(self):
        project = Mock()
        project.status = self.status()
        project.name = 'some project'
        self.action1 = Mock()
        self.action1.status = action.active
        self.action1.project_file_string.return_value = 'first action'
        self.action2 = Mock()
        self.action2.status = action.inactive
        self.action2.project_file_string.return_value = 'second action'
        project.actions = [self.action1,self.action2]
        project.observers = []
        self.info = Mock()
        self.info.file_string.return_value = 'important info'
        project.infos = [self.info]
        return project
    def status(self):
        return project.active

    def test_should_have_registered_itself_as_observer(self):
        self.assertTrue(self.project_file in self.project.observers)
#        self.project.observers.append.assert_called_with(self.project_file)


    def test_should_calc_file_name_as_project_name_plus_extension(self):
        self.assertEqual(self.project_file.file_name(),self.project.name+'.prj')

    def path(self):
        return self.path_in_subdirectory(self.subdir())

    def path_in_subdirectory(self,subdir):
        project_file_name = self.project.name+'.prj'
        if subdir and len(subdir) > 0:
            return os.path.join(subdir,project_file_name)
        else:
            return project_file_name





class ExistingProjectFileBehaviour:
    
    def setUp(self):
        super(ExistingProjectFileBehaviour,self).setUp()
    
    def assert_moved_file_to_correct_directory_if_status_changes(self,status,subdir):
        self.create_file()
        old_status = self.project.status
        self.project.status = status
        self.project_file.notify(self.project, 'status', status,old_status)
        assert os.path.isfile(self.path_in_subdirectory(subdir))
    
    def test_should_move_file_correctly_to_review_directory(self):
        self.assert_moved_file_to_correct_directory_if_status_changes(project.inactive,'@Review')

    def test_should_move_file_correctly_to_active_directory(self):
        self.assert_moved_file_to_correct_directory_if_status_changes(project.active,'')

    def test_should_move_file_correctly_to_someday_directory(self):
        self.assert_moved_file_to_correct_directory_if_status_changes(project.someday,'@Someday')

    def test_should_rename_file_if_project_name_changes(self):
        name = 'new name'
        self.create_file()
        self.project_file.notify(self.project, 'name', name)
        self.project.name = name
        assert os.path.isfile(self.path())
        
    def test_should_calc_path_correctly(self):
        self.assertEqual(self.project_file.path(),self.path())

    def test_should_write_if_notified_of_changes(self):
        self.project_file.notify(self.project, 'add_action', Mock(),None)        
        assert os.path.isfile(self.path())

class WritingProjectFileBehaviour(ExistingProjectFileBehaviour):
    def test_should_write_the_project_description_in_file(self):
#        pass
        self.project_file.write()
        content = self.file_content()
        assert len(content) > 0
        assert self.info.file_string() in content
        assert self.action1.project_file_string() in content
        assert self.action2.project_file_string() in content



class ActiveProjectFileBehaviour(ProjectFileBehaviour,ExistingProjectFileBehaviour):

    def status(self):
        return project.active

    def subdir(self):
        return ''

        


class SomedayProjectFileBehaviour(ProjectFileBehaviour,ExistingProjectFileBehaviour):

    def status(self):
        return project.someday

    def subdir(self):
        return '@Someday'        


class InactiveProjectFileBehaviour(ProjectFileBehaviour,ExistingProjectFileBehaviour):
    def status(self):
        return project.inactive
        
    def subdir(self):
        return '@Review'


class ProjectFileReaderBehaviour(ProjectFileBehaviour,ExistingProjectFileBehaviour):
    def setUp(self):
        super(ProjectFileReaderBehaviour,self).setUp()
        
    def create_project(self):
        self.original_project = project.Project('Example Project')
        self.original_project.add_info(info.Info('some info'))
        active_action = action.Action('active action','Online/Google')
        self.original_project.add_action(active_action)
        project_file = ProjectFile(self.original_project)
        self.write(project_file.file_string(),project_file.path())
        return ProjectFile.read(project_file.path())
        
    def path(self):
        return self.project_file.path()
    
    def test_should_read_the_project_name_correctly(self):
        self.assertEqual(self.project.name,'Example Project')

    def test_should_read_the_infos_correctly(self):
        self.assertEqual(self.original_project.infos,[info.Info('some info')])

    def test_should_read_the_actions_correclty(self):
        self.assertEqual(self.original_project.actions,self.project.actions)
        
