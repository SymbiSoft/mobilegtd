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

    def test_should_notify_observer_of_added_actions(self):
        action = Mock()
        action.status = done
        self.project.add_action(action)
        calls = self.observer.notify.call_args_list
        self.assertTrue(((self.project,'add_action',action),{}) in calls)

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


class ProjectWithActionsBehaviour(ProjectBehaviour):
    
    def setUp(self):
        super(ProjectWithActionsBehaviour,self).setUp()
        self.action = self.create_action()
        self.project.add_action(self.action)
#        self.project.actions.add

    def create_action(self):
        action = Mock()
        try:
            action.status = self.action_status()
        except:
            pass
        return action

    def test_should_contain_all_added_actions(self):
        self.assertEqual(self.project.actions,[self.action])

    def test_should_forget_removed_actions(self):
        self.project.remove_action(self.action)
        self.assertFalse(self.action in self.project.actions)
    
    def test_should_register_itself_as_observer_for_added_actions(self):
        self.action.observers.append.assert_called_with(self.project)


    def test_should_remove_itself_as_observer_for_removed_actions(self):
        self.project.remove_action(self.action)
        self.action.observers.remove.assert_called_with(self.project)

    def test_should_set_action_to_done_before_removing(self):
        self.project.remove_action(self.action)
        assert self.action.status == done

    def test_should_notify_observer_of_removed_actions(self):
        self.project.remove_action(self.action)
        calls = self.observer.notify.call_args_list
        self.assertTrue(((self.project,'remove_action',self.action),{}) in calls)

    def test_should_become_inactive_if_no_active_action_remains(self):
        self.project.remove_action(self.action)
        self.assertNotEqual(self.project.status,active)

def test_generator(field):
    def test_should_notify_observer_of_changes_in_actions(self):
        self.project.notify(self.action, field, 'new %s'%field)
        self.observer.notify.assert_called_with(self.project,'changed_action',self.action)
    return test_should_notify_observer_of_changes_in_actions

for field in ['description','info','context']:
    test_name = 'test_should_notify_observer_of_changes_in_action_%s' % field
    test = test_generator(field)
    setattr(ProjectWithActionsBehaviour, test_name, test)
        

class ProjectWithInactiveActionsBehaviour(ProjectWithActionsBehaviour,InactiveProjectBehaviour):

    def action_status(self):
        return inactive

    def test_should_become_active_when_inactive_actions_become_active(self):
        self.action.status = active
        self.project.notify(self.action,'status',active)
        self.assert_status(active)

    def test_should_return_the_inactive_action(self):
        self.assertEqual(self.project.actions_with_status(inactive),[self.action])

    def test_should_return_no_active_action(self):
        self.assertEqual(self.project.actions_with_status(active),[])



class ProjectWithActiveActionsBehaviour(ProjectWithActionsBehaviour):
    
    def action_status(self):
        return active

    def test_should_become_inactive_when_active_actions_become_inactive(self):
        self.project.status = active
        self.action.status = done
        self.project.notify(self.action,'status',done)
        self.assert_status(inactive)

    def test_should_return_the_active_action(self):
        self.assertEqual(self.project.actions_with_status(active),[self.action])

    def test_should_return_no_inactive_action(self):
        self.assertEqual(self.project.actions_with_status(inactive),[])

class ProjectWithInfosBehaviour(ProjectBehaviour):
    
    def setUp(self):
        super(ProjectWithInfosBehaviour,self).setUp()
        self.info = Mock()
        self.project.add_info(self.info)

    def test_should_contain_all_added_infos(self):
        self.assertEqual(self.project.infos,[self.info])

    def test_should_really_forget_removed_infos(self):
        self.project.remove_info(self.info)
        self.assertFalse(self.info in self.project.infos)

    def test_should_register_itself_as_observer_for_added_infos(self):
        self.info.observers.append.assert_called_with(self.project)

    def test_should_deregister_itself_as_observer_for_removed_infos(self):
        self.project.remove_info(self.info)
        self.info.observers.remove.assert_called_with(self.project)


    def test_should_notify_observer_of_removed_infos(self):
        self.project.remove_info(self.info)
        calls = self.observer.notify.call_args_list
        self.assertTrue(((self.project,'remove_info',self.info),{}) in calls)

    def test_should_notify_observer_of_changes_in_infos(self):
        self.project.notify(self.info, 'text', 'new text')
        self.observer.notify.assert_called_with(self.project,'changed_info',self.info)

        


