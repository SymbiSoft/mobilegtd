import sys,os,unittest
sys.path.append(os.path.abspath(os.path.join(os.getcwd(),'..','..','..')))
#print sys.path
import file_based_spec
import model.persistance.action_file
from model.model import *
from model.action import Action



class ActionFileBasedBehaviour(file_based_spec.FileBasedBehaviour):

	def setUp(self):
		super(ActionFileBasedBehaviour,self).setUp()
		self.context = 'context/sub_context'
		self.description = 'some action'
		self.action = Action(self.description, self.context)
		self.action_file = model.persistance.action_file.ActionFile(self.action)
	def path(self):
		return os.path.join(self.action.context,self.action.description+'.act')


class ProcessedActionFileBehaviour(ActionFileBasedBehaviour):

	def setUp(self):
		super(ProcessedActionFileBehaviour,self).setUp()
		self.action.status = active

	def test_should_remove_the_file_when_action_is_set_to_done(self):
		self.action.status = done
		assert not os.path.isfile(self.path())

	def test_should_remove_the_file_when_action_is_set_to_inactive(self):
		self.action.status = inactive
		assert not os.path.isfile(self.path())

	def test_should_rename_the_file_when_description_is_changed(self):
		self.action.description = 'other action'
		assert os.path.isfile(self.path())

	def test_should_move_the_file_when_context_is_changed(self):
		self.action.context = 'other_context'
		assert os.path.isfile(self.path())

	def test_should_set_action_to_done_if_file_does_not_exist(self):
		os.remove(self.path())
		self.action_file.update_done_status()
		assert self.action.status == done

	def test_should_write_the_action_description_in_file(self):
		content = self.file_content()
		assert len(content) > 0
		assert content == '%s %s'%(self.context,self.description)

class UnprocessedActionFileBehaviour(ActionFileBasedBehaviour):

	def setUp(self):
		super(UnprocessedActionFileBehaviour,self).setUp()
		self.action.status = unprocessed
		
	def test_should_create_a_file_when_action_is_set_active(self):
		self.action.status = active
		assert os.path.isfile(self.path())
				
	def test_should_not_create_the_file_when_description_is_changed(self):
		self.action.description = 'other action'
		assert not os.path.isfile(self.path())

	def test_should_move_the_file_when_context_is_changed(self):
		self.action.context = 'other_context'
		assert not os.path.isfile(self.path())



class DoneActionFileBehaviour(UnprocessedActionFileBehaviour):
	def setUp(self):
		super(DoneActionFileBehaviour,self).setUp()
		self.action.status = done


	
class InactiveActionFileBehaviour(UnprocessedActionFileBehaviour):
	def setUp(self):
		super(InactiveActionFileBehaviour,self).setUp()
		self.action.status = inactive



if __name__ == '__main__':
	unittest.main()