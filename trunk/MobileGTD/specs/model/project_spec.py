import unittest
from mock import Mock
import model.project

from model.project import Project
from model import project
from model import action
import copy

class ProjectBehaviour(unittest.TestCase):

    def setUp(self):
        self.name = 'project'
        self.status = self.initial_status()
        self.actions = self.initial_actions()
        self.infos = self.initial_infos()
        self.project = model.project.Project(self.name,self.status,copy.copy(self.actions),copy.copy(self.infos))
        self.observer = Mock()
        self.project.observers.append(self.observer)

    def initial_actions(self):
        return []

    def create_action(self):
        a = Mock()
        a.status = self.action_status()
        return a

    def action_status(self):
        return None

    def initial_infos(self):
        return []

    def initial_status(self):
        return project.inactive

    def test_should_remember_its_name(self):
        self.assertEqual(self.project.name,self.name)

    def test_should_notify_observer_of_name_change(self):
        self.project.name = 'new name'
        self.assert_observed('name','new name',self.name)

    def test_should_notify_observer_of_status_change(self):
        self.project.status = project.done
        self.assert_observed_status(project.done)

    def create_action_with_status(self,status=action.inactive):
        a = Mock()
        a.status=status
        return a    
    def test_should_register_itself_as_project_for_added_actions(self):
        a = self.create_action_with_status()
        self.project.add_action(a)
        self.assertEqual(a.project,self.project)
    
    def test_should_register_itself_as_observer_for_added_actions(self):
        a = self.create_action()
        self.project.add_action(a)
        a.observers.append.assert_called_with(self.project)

    def test_should_notify_observer_of_added_actions(self):
        a = Mock()
        a.status = action.done
        self.project.add_action(a)
        self.assert_observed('add_action', a)

    def test_should_be_equal_if_name_and_status_are_identical(self):
        other = Mock()
        other.name = self.name
        other.status = self.status
        self.assertTrue(self.project == other)
        self.assertFalse(self.project != other)
        other.name = 'other name'
        self.assertTrue(self.project != other)

    def assert_observed(self,attribute,new=None,old=None):
        calls = self.observer.notify.call_args_list
        self.assertTrue(((self.project,attribute),{'new':new,'old':old}) in calls,
                        'Expected notification from %s concerning the change of %s from %s to %s\n  Only got these calls:\n%s'%(self.project,attribute,old,new,repr(calls)))

    def assert_observed_status(self,status):
        self.assert_status(status)
        self.assert_observed('status',status,self.status)

    def assert_status(self,status):
        self.assertEqual(self.project.status,status)

class ActiveProjectBehaviour(ProjectBehaviour):

    def initial_actions(self):
        a = self.create_action_with_status(action.active)
        return [a]
    
    def initial_status(self):
        return project.active

    def test_should_be_active(self):
        self.assert_status(project.active)

    def test_should_contain_active_actions(self):
        self.assertTrue(self.project.has_active_actions())

    def test_should_become_inactive_if_no_active_action_remains(self):
        self.project.status = project.active
        for a in self.project.actions_with_status(action.active):
            self.project.remove_action(a)
        self.assert_observed_status(project.inactive)

    def test_should_become_inactive_when_active_actions_become_inactive(self):
        self.project.status = project.active
        for a in self.project.actions_with_status(action.active):
            a.status = action.done
            self.project.notify(a,'status',action.done)
        self.assert_observed_status(project.inactive)


class InactiveProjectBehaviour(ProjectBehaviour):
    def initial_status(self):
        return project.inactive
    def test_should_be_inactive(self):
        self.assert_status(project.inactive)

    def test_should_become_active_if_active_actions_are_added(self):
        a = Mock()
        a.status = action.active
        self.project.add_action(a)
        self.assertEqual(self.project.status,project.active)


class EmptyProjectBehaviour(InactiveProjectBehaviour):    

    def test_should_return_an_empty_list_of_actions(self):
        self.assertEqual(self.project.actions,[])
        
    def test_should_return_an_empty_list_of_infos(self):
        self.assertEqual(self.project.infos,[])


class ProjectWithActionsBehaviour(ProjectBehaviour):
    def setUp(self):
        self.action = self.create_action()
        super(ProjectWithActionsBehaviour,self).setUp()
    
    def initial_actions(self):
        return [self.action]
    
    def test_should_contain_all_added_actions(self):
        self.assertEqual(self.project.actions,self.actions)

    def test_should_forget_removed_actions(self):
        self.project.remove_action(self.actions[0])
        self.assertFalse(self.actions[0] in self.project.actions)
    
    def test_should_remove_itself_as_observer_for_removed_actions(self):
        self.project.remove_action(self.actions[0])
        self.actions[0].observers.remove.assert_called_with(self.project)

    def test_should_set_action_to_done_before_removing(self):
        self.project.remove_action(self.actions[0])
        assert self.actions[0].status == action.done

    def test_should_notify_observer_of_removed_actions(self):
        self.project.remove_action(self.actions[0])
        self.assert_observed('remove_action',self.actions[0],None)

def test_generator(field):
    def test_should_notify_observer_of_changes_in_actions(self):
        self.project.notify(self.actions[0], field, 'new %s'%field)
        self.assert_observed('changed_action',self.actions[0])
    return test_should_notify_observer_of_changes_in_actions

for field in ['description','info','context']:
    no_change_on_action_becoming_active = 'test_should_notify_observer_of_changes_in_action_%s' % field
    test = test_generator(field)
    setattr(ProjectWithActionsBehaviour, no_change_on_action_becoming_active, test)
        

class ProjectWithInactiveActionsBehaviour(ProjectWithActionsBehaviour):

    def action_status(self):
        return action.inactive

    def test_should_become_active_when_inactive_actions_become_active(self):
        self.actions[0].status = action.active
        self.project.notify(self.actions[0],'status',action.active)
        self.assert_observed_status(project.active)

    def test_should_return_the_inactive_action(self):
        self.assertEqual(self.project.actions_with_status(action.inactive),[self.actions[0]])

    def test_should_return_no_active_action(self):
        self.assertEqual(self.project.actions_with_status(action.active),[])



class ProjectWithActiveActionsBehaviour(ProjectWithActionsBehaviour):
    
    def action_status(self):
        return action.active

    def test_should_return_the_active_action(self):
        self.assertEqual(self.project.actions_with_status(action.active),[self.actions[0]])

    def test_should_return_no_inactive_action(self):
        self.assertEqual(self.project.actions_with_status(action.inactive),[])



#class ActiveProjectWithActiveActionsBehaviour(ProjectWithActiveActionsBehaviour,ActiveProjectBehaviour):
    



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
        self.assert_observed('remove_info',self.info)

    def test_should_notify_observer_of_changes_in_infos(self):
        self.project.notify(self.info, 'text', 'new text')
        self.assert_observed('changed_info',self.info)




def generate_no_becoming_active_test(status):
    def initial_status(self):
        return status
    def test_should_not_change_status_if_actions_become_active(self):
        self.project.notify(self.actions[0], 'status', action.active)
        self.assertEqual(status,self.project.status)
    def test_should_not_change_status_if_active_actions_are_added(self):
        a = Mock()
        a.status = action.active
        self.project.add_action(a)
        self.assertEqual(status,self.project.status)
    return (initial_status,test_should_not_change_status_if_actions_become_active,test_should_not_change_status_if_active_actions_are_added)
#
for status in ['someday','done','tickled']:
    class_name = '%sProjectBehaviour'%status.capitalize()
    my_class=type(class_name,(ProjectWithActiveActionsBehaviour,),{})
    no_change_on_action_becoming_active = 'test_should_not_change_%s_status_if_actions_become_active' % status
    no_change_on_active_action_added= 'test_should_not_change_%s_status_if_active_actions_are_added' % status
    initial_status,no_change_on_action_becoming_active_test,no_change_on_active_action_added_test = generate_no_becoming_active_test(getattr(model.project,status))
    
    setattr(my_class, 'initial_status', initial_status)
    setattr(my_class, no_change_on_action_becoming_active, no_change_on_action_becoming_active_test)
    setattr(my_class, no_change_on_active_action_added, no_change_on_active_action_added_test)
    globals()[class_name]=my_class


           



