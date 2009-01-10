import unittest
from model.projects import Projects
from mock import Mock

class ProjectsBehaviour(unittest.TestCase):
    def setUp(self):
        self.projects = Projects()
        self.observer = Mock()
        self.projects.observers.append(self.observer)
        
    def create_project(self,name=None,status=None):
        p = Mock()
        if name != None:
            p.name = name
        if status != None:
            p.status = status
        return p
    
    def assert_observed(self,attribute,new=None,old=None):
        self.observer.notify.assert_called_with(self.projects,attribute,new=new,old=old)
    
    def test_should_notify_observers_when_project_is_added(self):
        p = self.create_project()
        self.projects.append(p)
        self.assert_observed('add_item',new=p,old=None)
        

class EmptyProjectsBehaviour(ProjectsBehaviour):
    def test_should_not_contain_any_projects(self):
        self.assertEqual(self.projects,[])

class NonEmptyProjectsBehaviour(ProjectsBehaviour):

    def setUp(self):
        super(NonEmptyProjectsBehaviour,self).setUp()
        self.searched_projects = [self.create_project(status=0),self.create_project(status=0)]
        for p in self.searched_projects:
            self.projects.append(p)
        self.not_searched_projects = [self.create_project(status=1),self.create_project(status=2)]
        for p in self.not_searched_projects:
            self.projects.append(p)
    
    def test_should_remember_all_added_projects(self):
        for p in self.searched_projects+self.not_searched_projects:
            self.assertTrue(p in self.projects)

    def test_should_be_able_to_filter_projects_by_status(self):
        self.assertEqual(self.projects.with_status(0),self.searched_projects)

    def test_should_notify_observers_when_project_is_removed(self):
        p = self.projects[0]
        self.projects.remove(p)
        self.assert_observed('remove_item',new=p,old=None)
