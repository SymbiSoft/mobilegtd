from mock import Mock
import file_based_spec
import model.persistance.project_file
from model.model import *

import os
import inout.io


class ProjectFileBehaviour(file_based_spec.FileBasedBehaviour):

	def setUp(self):
		super(ProjectFileBehaviour,self).setUp()
		self.project = self.create_project()
		self.project.name = 'some project'
		self.action1 = Mock()
		self.action1.project_file_string.return_value = 'first action'
		self.action2 = Mock()
		self.action2.project_file_string.return_value = 'second action'
		self.project.actions = [self.action1,self.action2]
		self.info = Mock()
		self.info.file_string.return_value = 'important info'
		self.project.infos = [self.info]
		self.project_file = model.persistance.project_file.ProjectFile(self.project)

	def create_project(self):
		project = Mock()
		try:
			project.status = self.status()
		except:
			pass
		return project


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

	def create_file(self):
		inout.io.create_file(self.path()).close()





class ExistingProjectFileBehaviour:
	
	def setUp(self):
		super(ExistingProjectFileBehaviour,self).setUp()
	
	def assert_moved_file_to_correct_directory_if_status_changes(self,status,subdir):
		self.create_file()
		self.project_file.notify(self.project, 'status', status)
		self.project.status = status
		assert os.path.isfile(self.path_in_subdirectory(subdir))
	
	def test_should_move_file_correctly_to_review_directory(self):
		self.assert_moved_file_to_correct_directory_if_status_changes(inactive,'@Review')

	def test_should_move_file_correctly_to_active_directory(self):
		self.assert_moved_file_to_correct_directory_if_status_changes(active,'')

	def test_should_move_file_correctly_to_someday_directory(self):
		self.assert_moved_file_to_correct_directory_if_status_changes(someday,'@Someday')

	def test_should_rename_file_if_project_name_changes(self):
		name = 'new name'
		self.create_file()
		self.project_file.notify(self.project, 'name', name)
		self.project.name = name
		assert os.path.isfile(self.path())
		
	def test_should_calc_path_correctly(self):
		self.assertEqual(self.project_file.path(),self.path())

	def test_should_write_if_notified_of_changes(self):
		self.project_file.notify(self.project, 'add_action', Mock())		
		assert os.path.isfile(self.path())

	def test_should_write_the_project_description_in_file(self):
#		pass
		self.project_file.write()
		content = self.file_content()
		assert len(content) > 0
		assert self.info.file_string() in content
		assert self.action1.project_file_string() in content
		assert self.action2.project_file_string() in content



class ActiveProjectFileBehaviour(ProjectFileBehaviour,ExistingProjectFileBehaviour):

	def status(self):
		return active

	def subdir(self):
		return ''

		


class SomedayProjectFileBehaviour(ProjectFileBehaviour,ExistingProjectFileBehaviour):

	def status(self):
		return someday

	def subdir(self):
		return '@Someday'		


class InactiveProjectFileBehaviour(ProjectFileBehaviour,ExistingProjectFileBehaviour):
	def status(self):
		return inactive
		
	def subdir(self):
		return '@Review'


if __name__ == '__main__':
	unittest.main()