from mock import Mock
import file_based_spec
import unittest
from persistence import project_file
from persistence.project_file import ProjectFile,ProjectFileCreator
from model import project
from model import action
from model import info
from persistence.action_file import ActionFile
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

    def test_should_calc_file_name_as_project_name_plus_extension(self):
        self.assertEqual(self.project_file.file_name(),self.project.name+'.prj')

    def path(self):
        return self.path_in_subdirectory(self.subdir())

    def path_in_subdirectory(self,subdir):
        project_file_name = self.project.name+'.prj'
        if subdir and len(subdir) > 0:
            return os.path.join('@Projects',subdir,project_file_name)
        else:
            return os.path.join('@Projects',project_file_name)

    def test_should_create_an_action_file_if_notified_of_added_action(self):
        a = Mock()
        a.observers = []
        a.status = action.inactive
        self.project_file.notify(self.project, 'add_action', a, None)
        self.assertTrue(has_added_action_file_as_observer(a))




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
#        self.project.add_action.side_effect = lambda a:self.project_file.notify(self.project, 'add_action', a, None)
        
    def create_project(self):
        self.original_project = self.create_original_project()
        self.original_project.add_info(info.Info('some info'))
        active_action = action.Action('active action','Online/Google',status=action.inactive)
        self.original_project.add_action(active_action)
        p_file = ProjectFile(self.original_project)
        self.write(p_file.file_string(),p_file.path())
        return project_file.read(p_file.path())

    def create_original_project(self):
        return project.Project('Example Project')

    def path(self):
        return self.project_file.path()
    
    def test_should_read_the_project_name_correctly(self):
        self.assertEqual(self.project.name,'Example Project')

    def test_should_infer_the_status_from_the_path(self):
        self.assertEqual(self.project.status,self.original_project.status)

    def test_should_read_the_infos_correctly(self):
        self.assertEqual(self.project.infos,[info.Info('some info')])

    def test_should_read_the_actions_correctly(self):
        a = action.Action('active action','Online/Google',status=action.inactive)
        a.project = self.project
        self.assertEqual(self.project.actions,[a])
        
    def test_should_create_action_files_for_all_actions(self):
        for a in self.project.actions:
            self.assertTrue(has_added_action_file_as_observer(a))

class DoneProjectFileReaderBehaviour(ProjectFileReaderBehaviour):
    def create_original_project(self):
        p = ProjectFileReaderBehaviour.create_original_project(self)
        p.status = project.done
        return p


def has_added_action_file_as_observer(a):
    has_action_file=False
    for o in a.observers:
        if type(o) == ActionFile and o.action == a:
            has_action_file=True
    return has_action_file