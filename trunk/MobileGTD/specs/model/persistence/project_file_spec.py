import unittest
from mock import Mock
#print sys.path
import file_based_spec
import model.persistance.project_file
from model.model import *
from model.project import Project
import os


class ProjectFileBehaviour(file_based_spec.FileBasedBehaviour):

	def setUp(self):
		super(ProjectFileBehaviour,self).setUp()
		self.project = self.create_project()
		self.project.name = 'some project'
		self.project_file = model.persistance.project_file.ProjectFile(self.project)

	def create_project(self):
		return Mock()

	def test_should_calc_file_name_as_project_name_plus_extension(self):
		self.assertEqual(self.project_file.file_name(),self.project.name+'.prj')

class ActiveProjectFileBehaviour(ProjectFileBehaviour):

	def create_project(self):
		project = super(ActiveProjectFileBehaviour,self).create_project()
		project.status = active
		return project
		
	def test_should_calc_path_as_project_name_plus_extension(self):
		self.assertEqual(self.project_file.path(),self.project.name+'.prj')


#	def test_should_move_to_done_folder_when_set_to_done(self):
#		self.project.status = done
#		self.project_file
#		assert not os.path.isfile(self.file_name())
#
#	def test_should_remove_the_file_when_action_is_set_to_inactive(self):
#		self.action.status = inactive
#		assert not os.path.isfile(self.file_name())
#
#	def test_should_rename_the_file_when_description_is_changed(self):
#		self.action.description = 'other action'
#		assert os.path.isfile(self.file_name())
#
#	def test_should_move_the_file_when_context_is_changed(self):
#		self.action.context = 'other_context'
#		assert os.path.isfile(self.file_name())
#
#	def test_should_set_action_to_done_if_file_does_not_exist(self):
#		os.remove(self.file_name())
#		self.action_file.update_done_status()
#		assert self.action.status == done
#
#	def test_should_write_the_action_description_in_file(self):
#		content = self.file_content()
#		assert len(content) > 0
#		assert content == '%s %s'%(self.context,self.description)
class InactiveProjectFileBehaviour(ProjectFileBehaviour):

	def create_project(self):
		project = super(InactiveProjectFileBehaviour,self).create_project()
		project.status = inactive
		return project
		
	def test_should_calc_path_as_review_folder_plus_project_name(self):
		self.assertEqual(self.project_file.path(),os.path.join('@Review',self.project.name+'.prj'))




if __name__ == '__main__':
	unittest.main()