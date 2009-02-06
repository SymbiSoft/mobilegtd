from model import model
import unittest

class StatusBehaviour(unittest.TestCase):
    def setUp(self):
        self.status = model.Status('schmactive',12,u's')
    
    def test_should_be_equal_to_other_status_with_identical_name_and_value(self):
        other = model.Status('schmactive',12)
        self.assertEqual(self.status,other)
