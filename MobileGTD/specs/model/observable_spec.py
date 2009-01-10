import unittest
from mock import Mock
from model.observable import ObservableList

class ObservableListBehaviour(unittest.TestCase):
    def setUp(self):
        self.list = ObservableList()
        self.observer = Mock()
        self.list.observers.append(self.observer)
        
    def add_item(self):
        p = Mock()
        self.list.append(p)
        return p

    def assert_observed(self,name,new=None,old=None):
        self.observer.notify.assert_called_with(self.list,name,new=new,old=old)

    def test_should_be_iterable(self):
        for item in self.list:
            pass

    def test_should_notify_observers_if_item_was_added(self):
        p = self.add_item()
        self.assert_observed('add_item',new=p,old=None)

    def test_should_remember_added_items(self):
        p = self.add_item()
        self.assertTrue(p in self.list)
        


class EmptyObservableListBehaviour(ObservableListBehaviour):

    def test_should_be_empty(self):
        self.assertEqual(len(self.list),0)

    def test_should_raise_exception_when_trying_to_remove_a_item(self):
        self.assertRaises(ValueError,self.list.remove,Mock())

    

class NotEmptyObservableListBehaviour(ObservableListBehaviour):

    def setUp(self):
        super(NotEmptyObservableListBehaviour,self).setUp()
        self.add_item()
    
    def test_should_notify_observers_if_item_was_removed(self):
        i = self.list[0]
        self.list.remove(i)
        self.assert_observed('remove_item', i, None)