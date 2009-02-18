import unittest
import logic.review_visitor
from logic import review_visitor
import model.project,model.projects
from model import action
from model import project
from model import datetime
from model.model import *
from mock import Mock,patch_object,patch
import random

class ReviewVisitorBehaviour(unittest.TestCase):
    pass

    def setUp(self):
        self.positive_property_actions = [self.create_action() for i in range(10)]
        self.negative_property_actions =[self.create_action() for i in range(9)]
     
        
        self.project1 = self.create_project()
        self.project2 = self.create_project()

        self.project1.actions_with_status.return_value = self.positive_property_actions[:7]
        self.project1.actions = self.project1.actions_with_status()+self.negative_property_actions[:1]
        self.project2.actions_with_status.return_value = self.positive_property_actions[7:]
        self.project2.actions = self.project2.actions_with_status()+self.negative_property_actions[1:]

        self.projects = [self.project1,self.project2]
        self.reviewer = logic.review_visitor.ReviewVisitor()
    
    def create_project(self):
        p = Mock()
        p.status.update.return_value = p.status
        p.last_modification_date.return_value = datetime.datetime.now()
        return p

    def create_action(self):
        a = Mock(spec=action.Action)
        a.status = action.unprocessed
        return a
        

    def create_action_with_status(self,status):
        a = self.create_action()
        a.status = status
        return a
        
    def review(self):
        self.reviewer.review(self.projects)

    
    
    def test_should_set_all_unprocessed_actions_to_active(self):
        for a in self.positive_property_actions:
            a.status = action.unprocessed
        for a in self.negative_property_actions:
            a.status = random.choice([action.done,action.inactive])
        self.review()
        for a in self.positive_property_actions:
            self.assertEqual(a.status,action.active)
        for a in self.negative_property_actions:
            self.assertNotEqual(a.status,action.active)

    
    def test_should_untickle_projects_with_tickle_date_present_or_past(self):
        self.project1.status = project.Tickled(datetime.date.now())
        self.project2.status = project.Tickled(datetime.date(2030, 12, 2))
        self.review()
        self.assertEqual(self.project1.status,project.active)
        self.assertEqual(self.project2.status,project.tickled)
    
    def test_should_schedule_projects_with_a_certain_period_of_inactivity_for_review(self):
        self.project1.last_modification_date.return_value = datetime.datetime(2009, 1, 1)
        self.project2.last_modification_date.return_value = datetime.datetime(2030, 12, 2)
        project2_previous_status = self.project2.status
        self.review()
        self.assertEqual(self.project1.status,project.inactive)
        self.assertEqual(self.project2.status,project2_previous_status)