import sys,os,unittest
sys.path.append(os.path.abspath(os.path.join(os.getcwd(),'..','..','..')))
#print sys.path
import file_based_spec
import model.persistance.action_file
#from model.model import *
from model.action import *



class ActionFileBasedBehaviour(file_based_spec.FileBasedBehaviour):

    def setUp(self):
        super(ActionFileBasedBehaviour,self).setUp()
        self.context = 'context/sub_context'
        self.description = 'some action'
        self.action = Action(self.description, self.context)
        self.action_file = model.persistance.action_file.ActionFile(self.action)

    def path(self):
        return os.path.join(self.action.context,self.action.description+'.act')


class ActiveActionFileBehaviour(ActionFileBasedBehaviour):

    def setUp(self):
        super(ActiveActionFileBehaviour,self).setUp()
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
        self.assertTrue(len(content) > 0)
        self.assertEqual(content, '- %s %s'%(self.context,self.description))

    def test_should_write_if_the_info_changed(self):
        info = 'new info'
        self.action.info = info 
        content = self.file_content()
        self.assertTrue(len(content) > 0)
        self.assertEqual(content, '- %s %s (%s)'%(self.context,self.description,info))




def generate_test_for_write_on_change_notification(field):
    def test_should_write_if_notified_of_changes(self):
    	d = 'new %s'%field
    	setattr(self.action,field, d)
    	self.action_file.notify(self.action, field, d)
    	self.assertTrue(d in self.file_content())
    return test_should_write_if_notified_of_changes

for field in ['description','info','context']:
    test_name = 'test_should_write_when_notified_of_changed_%s' % field
    test = generate_test_for_write_on_change_notification(field)
    setattr(ActiveActionFileBehaviour, test_name, test)



class UnprocessedActionFileBehaviour(ActionFileBasedBehaviour):

    def setUp(self):
        super(UnprocessedActionFileBehaviour,self).setUp()
        self.action.status = unprocessed

    def test_should_not_have_created_a_file(self):
        assert not os.path.isfile(self.path())    	
       
    def test_should_create_a_file_when_action_is_set_active(self):
        self.action.status = active
        assert os.path.isfile(self.path())
                
    def test_should_not_create_the_file_when_description_is_changed(self):
        self.action.description = 'other action'
        assert not os.path.isfile(self.path())

    def test_should_move_the_file_when_context_is_changed(self):
        self.action.context = 'other_context'
        assert not os.path.isfile(self.path())

def generate_test_for_not_writing_on_change_notification(field):
    def test_should_not_write_if_notified_of_changes(self):
    	d = 'new %s'%field
    	setattr(self.action,field, d)
    	self.action_file.notify(self.action, field, d)
        self.assertFalse(os.path.isfile(self.path()))
    return test_should_not_write_if_notified_of_changes

for field in ['description','info','context']:
    test_name = 'test_should_not_write_when_notified_of_changed_%s' % field
    test = generate_test_for_not_writing_on_change_notification(field)
    setattr(UnprocessedActionFileBehaviour, test_name, test)


class DoneActionFileBehaviour(UnprocessedActionFileBehaviour):
    def setUp(self):
        super(DoneActionFileBehaviour,self).setUp()
        self.action.status = done


    
class InactiveActionFileBehaviour(UnprocessedActionFileBehaviour):
    def setUp(self):
        super(InactiveActionFileBehaviour,self).setUp()
        self.action.status = inactive

