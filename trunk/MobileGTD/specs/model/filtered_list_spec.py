import unittest
from mock import Mock
import random
from model.filtered_list import FilteredList

class FilteredListBehaviour(unittest.TestCase):

    def setUp(self):
        self.list = FilteredList([])

    def test_should_return_filtered_lists(self):
        l = self.list.with_property(lambda x:True)
        self.assertEqual(type(l),FilteredList)
        

class EmptyFilteredListBehaviour(FilteredListBehaviour):
    
    def test_should_a_new_empty_filtered_list_on_with(self):
        l = self.list.with_property(lambda x:True)
        self.assertEqual(l,[])

class NonEmptyFilteredListBehaviour(FilteredListBehaviour):

    def setUp(self):
        super(NonEmptyFilteredListBehaviour,self).setUp()
        
        self.items,self.items_with_property,self.items_without_property = self.create_items(random.randint(0, 20) ,random.randint(0, 20))
        for item in self.items:
            self.list.append(item)
    def property(self):
        return lambda x:x.has_property(0)
    def create_items(self,number_of_items_with_property=1,number_of_items_without_property=1):
        items_with_property = []
        for i in range(0,number_of_items_with_property):
            item = Mock()
            item.has_property.return_value = True
            items_with_property.append(item)
        
        items_without_property = []
        for i in range(0,number_of_items_without_property):
            item = Mock()
            item.has_property.return_value = False
            items_without_property.append(item)
        items = items_with_property+items_without_property
        random.shuffle(items)
        return (items,items_with_property,items_without_property)

    def filter_results(self):
        return self.list.with_property(self.property())

    def test_should_test_the_property_on_its_items(self):
        self.filter_results()
        for item in self.items:
            item.has_property.assert_called_with(0)

    def test_should_return_all_items_which_fulfill_the_property(self):
        filtered = self.filter_results()
        for item in self.items_with_property:
            self.assertTrue(item in filtered)
        for item in filtered:
            self.assertTrue(item in self.items_with_property)
            

    def test_should_return_none_of_the_items_which_dont_fulfill_the_property(self):
        filtered = self.filter_results()
        for item in self.items_without_property:
            self.assertFalse(item in filtered)
        for item in filtered:
            self.assertFalse(item in self.items_without_property)
