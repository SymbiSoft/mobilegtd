import nose
import os
from nose.selector import Selector
from nose.plugins import Plugin

import unittest


class MySelector(Selector):
    def wantDirectory(self, dirname):
        parts = dirname.split(os.path.sep)
        return 'specs' in parts
    def wantFile(self, filepath):
        
        # we want python modules under specs/
        dirname,filename = os.path.split(filepath)
        base, ext = os.path.splitext(filename)
        return self.wantDirectory(dirname) and ext == '.py' and base[0:2] != '__'
    def wantModule(self, module):
        # wantDirectory and wantFile above will ensure that
        # we never see an unwanted module
        return True
    def wantFunction(self, function):
        # never collect functions
        return False
    def wantClass(self, cls):
        # only collect TestCase subclasses
        return issubclass(cls, unittest.TestCase)

class UseMySelector(Plugin):
    enabled = True
    def configure(self, options, conf):
        pass # always on
    def prepareTestLoader(self, loader):
        loader.selector = MySelector(loader.config)
nose.main(plugins=[UseMySelector()])