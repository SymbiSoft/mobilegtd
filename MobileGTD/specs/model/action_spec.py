import unittest
import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')))
print sys.path
import model.action
from model import action
from mock import Mock



class UnprocessedStatusBehaviour(unittest.TestCase):
	def setUp(self):
		self.status = action.unprocessed
	
	def test_should_return_active_on_update(self):
		self.assertEqual(self.status.update(None),action.active)



class ActionBehaviour(unittest.TestCase):

	def setUp(self):
		self.action = model.action.Action('oldey','some_context')
		self.observer = Mock()
		self.action.observers.append(self.observer)

	def test_should_be_unprocessed_by_default(self):
		self.assertEqual(self.action.status,action.unprocessed)

	def test_should_have_new_field_value_when_set(self):
		self.action.description='newey'
		assert self.action.description == 'newey'

	def test_should_notify_observers_when_field_is_changed_externally(self):
		self.action.description='newea'
		self.observer.notify.assert_called_with(self.action,'description',new='newea',old='oldey')

	def test_should_notify_observers_when_status_changes(self):
		self.action.status = action.active
		self.observer.notify.assert_called_with(self.action,'status',new=action.active,old=action.unprocessed)
		


class ActionParseBehaviour(unittest.TestCase):
	
	def setUp(self):
		self.description = 'some action'
		self.context = 'context/sub_context'
		self.info = 'additional stuff'
		self.status_string = '-'
		self.action = model.action.Action.parse(u'%s %s %s (%s)'%(self.status_string,self.context,self.description,self.info))
		
	def test_should_read_the_description_correctly(self):
		self.assertEqual(self.action.description, self.description)

	def test_should_read_the_context_correctly(self):
		self.assertEqual(self.action.context, self.context)

	def test_should_read_the_status_correctly(self):
		self.assertEqual(self.action.status, action.active)

	def test_should_read_the_info_correctly(self):
		self.assertEqual(self.action.info, self.info)
