import unittest,mox
import logic.review_visitor
import model.project,model.projects,model.action
from model.model import *

class ReviewVisitorBehaviour(unittest.TestCase):

    def setUp(self):
        self.dao = self.mox.CreateMock(PersonDao)
        self.manager = PersonManager(self.dao)

    def testCreatePersonWithAccess(self):
        self.dao.InsertPerson(test_person)
        self.mox.ReplayAll()
        self.manager.CreatePerson(test_person, 'stevepm')
        self.mox.VerifyAll()

        
    def setUp(self):
        self.mox = mox.Mox()
        self.project1 = model.project.Project('project1')
        self.add_action(self.project1,'unprocessed1',unprocessed)
        self.add_action(self.project1,'processed1',active)
        self.project2 = model.project.Project('project2')
        self.add_action(self.project2,'processed2',active)
        self.add_action(self.project2,'unprocessed2',unprocessed)
        self.reviewer = logic.review_visitor.ReviewVisitor()

    def add_action(self,project,action_name,action_status):
        action = self.mox.CreateMock(model.action.Action)
        action.status = action_status
        action.description = action_name
        project.actions.append(action)
        

    def test_should_set_all_unprocessed_actions_to_processed(self):
        pass