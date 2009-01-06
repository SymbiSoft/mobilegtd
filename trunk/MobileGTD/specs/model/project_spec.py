import unittest
from mock import Mock
import model.project
from model.model import *



class ProjectBehaviour(unittest.TestCase):

    def setUp(self):
        self.name = 'project'
        self.project = model.project.Project(self.name)
        self.observer = Mock()
        self.project.observers.append(self.observer)

    def test_should_remember_its_name(self):
        self.assertEqual(self.project.name,self.name)

    def test_should_notify_observer_of_name_change(self):
        self.project.name = 'new name'
        self.observer.notify.assert_called_with(self.project,'name','new name')

    def test_should_notify_observer_of_status_change(self):
        self.project.status = done
        self.assert_status(done)

    def assert_status(self,status):
        self.assertEqual(self.project.status,status)
        self.observer.notify.assert_called_with(self.project,'status',status)

class ActiveProjectBehaviour:
    def test_should_be_active(self):
        self.assertEqual(self.project.status,active)



class InactiveProjectBehaviour:
    def test_should_be_inactive(self):
        self.assertEqual(self.project.status,inactive)



class EmptyProjectBehaviour(ProjectBehaviour,InactiveProjectBehaviour):    

    def test_should_return_an_empty_list_of_actions(self):
        self.assertEqual(self.project.actions,[])
        
    def test_should_return_an_empty_list_of_infos(self):
        self.assertEqual(self.project.infos,[])

    def test_should_register_itself_as_observer_for_added_actions(self):
        action = Mock()
        self.project.add_action(action)
        action.observers.append.assert_called_with(self.project)



class ProjectWithActionsBehaviour(ProjectBehaviour):
    
    def setUp(self):
        super(ProjectWithActionsBehaviour,self).setUp()
        self.action = self.create_action()
        self.project.add_action(self.action)
#        self.project.actions.add

    def test_should_remove_itself_as_observer_for_removed_actions(self):
        self.project.remove_action(self.action)
        self.action.observers.remove.assert_called_with(self.project)

    def create_action(self):
        return Mock()


class ProjectWithInactiveActionsBehaviour(ProjectWithActionsBehaviour,InactiveProjectBehaviour):

    def create_action(self):
        action = Mock()
        action.status = inactive
        return action

    def test_should_become_active_when_inactive_actions_become_active(self):
        self.action.status = active
        self.project.notify(self.action,'status',active)
        self.assert_status(active)

    def test_should_return_the_inactive_action(self):
        self.assertEqual(self.project.actions_with_status(inactive),[self.action])

    def test_should_return_no_active_action(self):
        self.assertEqual(self.project.actions_with_status(active),[])

class ProjectWithActiveActionsBehaviour(ProjectWithActionsBehaviour,ActiveProjectBehaviour):

    def create_action(self):
        action = Mock()
        action.status = active
        return action

    def test_should_become_inactive_when_active_actions_become_inactive(self):
        self.action.status = done
        self.project.notify(self.action,'status',done)
        self.assert_status(inactive)

    def test_should_return_the_active_action(self):
        self.assertEqual(self.project.actions_with_status(active),[self.action])

    def test_should_return_no_inactive_action(self):
        self.assertEqual(self.project.actions_with_status(inactive),[])
