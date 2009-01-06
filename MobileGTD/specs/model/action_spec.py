import unittest
import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')))
print sys.path
import model.action
from model.model import *

class Observer(object):
	def __init__(self):
		self.notified = False
	def notify(self,object,name,value):
		self.object = object
		self.name = name
		self.value = value
		self.notified = True

class ActionBehaviour(unittest.TestCase):

	def setUp(self):
		self.action = model.action.Action('oldey','some_context')
		self.observer = Observer()
		self.action.observers.append(self.observer)

	def test_should_have_new_field_value_when_set(self):
		self.action.description='newey'
		assert self.action.description == 'newey'

	def test_should_notify_observers_when_changing_field(self):
		self.action.description='newea'
		assert self.observer.notified
		assert self.observer.object == self.action
		assert self.observer.name == 'description'
		assert self.observer.value == 'newea'
		


class ActionParseBehaviour(unittest.TestCase):
	
	def setUp(self):
		self.description = 'some action'
		self.context = 'context/sub_context'
		self.info = 'additional stuff'
		self.status_string = '-'
		self.action = model.action.Action.parse(u'%s %s %s (%s)'%(self.status_string,self.context,self.description,self.info))
		
	def test_should_read_the_description_correctly(self):
		assert self.action.description == self.description

	def test_should_read_the_context_correctly(self):
		assert self.action.context == self.context

	def test_should_read_the_status_correctly(self):
		assert self.action.status == active

	def test_should_read_the_info_correctly(self):
		assert self.action.info == self.info

		
if __name__ == '__main__':
	unittest.main()