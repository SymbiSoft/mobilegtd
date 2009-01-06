import unittest
import os,tempfile,shutil

class FileBasedBehaviour(unittest.TestCase):
	def setUp(self):
		self.current_dir = os.getcwd()
		self.tempdir = tempfile.mkdtemp()
		os.chdir(self.tempdir)
	def tearDown(self):
		os.chdir(self.current_dir)
		shutil.rmtree(self.tempdir,True)

	def file_content(self):
		f=file(self.path(),'r')
		raw=f.read()
		f.close()
		return raw

__all__= ["FileBasedBehaviour"]