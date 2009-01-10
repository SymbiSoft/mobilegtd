import unittest
import os,tempfile,shutil
import inout.io

class FileSystemBasedBehaviour(unittest.TestCase):
	def setUp(self):
		self.current_dir = os.getcwd()
		self.tempdir = tempfile.mkdtemp()
		os.chdir(self.tempdir)
	def tearDown(self):
		os.chdir(self.current_dir)
		shutil.rmtree(self.tempdir,True)

class FileBasedBehaviour(FileSystemBasedBehaviour):

	def file_content(self):
		f=file(self.path(),'r')
		raw=f.read()
		f.close()
		return raw

	def create_file(self):
		inout.io.create_file(self.path()).close()

	def write(self,content,path=None):
		if path == None:
			path = self.path()
		inout.io.write(path,content)

__all__= ["FileBasedBehaviour","FileSystemBasedBehaviour"]