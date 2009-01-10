import os,re
import config.config
import inout.io
from inout.io import u_join,write

from time import *
from observable import *
from log.logging import logger
from config.config import *
from inout.io import *
#logger.log(u'new version')




def invert_dictionary(dictionary):
	return dict([[v,k] for k,v in dictionary.items()])





		
class ItemWithStatus(object):
	def __init__(self,status):
		self.status = status


class WriteableItem(ObservableItem):
	def __init__(self):
		super(WriteableItem, self).__init__()
	def write(self):
		write(self.path(),self.file_string())
	def move_to(self,directory,old_dir=None):
		new_file_name = os.path.join(directory,self.file_name())
		if old_dir == None:
			old_dir = self.directory()
		old_file_name = os.path.join(old_dir,self.file_name())
		try:
			os.renames(old_file_name.encode('utf-8'),new_file_name.encode('utf-8'))
			##logger.log(u'Moved %s to %s'%(repr(old_file_name),repr(new_file_name)))
			#print u'Moved %s to %s'%(repr(old_file_name),repr(new_file_name))
			return new_file_name
		except OSError:
			#logger.log(u'Cannot move %s to %s: File already exists'%(repr(old_file_name),repr(new_file_name)))
			return old_file_name
		
	def directory(self):
		return os.path.dirname(self.encoded_path())
	def file_name(self):
		return os.path.basename(self.encoded_path())
	def remove(self):
		encoded_path = self.encoded_path()
		if os.path.isfile(encoded_path):
			os.remove(encoded_path)
	def exists(self):
		return os.path.isfile(self.encoded_path())

	def encoded_path(self):
		return self.path().encode('utf-8')

	def extension(self):
		return os.path.splitext(self.encoded_path())[1]
	def rename(self,new_name,old=None):
		if not old:
			old = os.path.splitext(os.path.basename(self.encoded_path()))[0]
		
		
		new_file_name = os.path.join(self.directory(),new_name+self.extension())
		old_file_name = os.path.join(self.directory(),old+self.extension())
		#logger.log(u'Renaming %s to %s'%(old_file_name,new_file_name))
		#print(u'Renaming %s to %s'%(old_file_name,new_file_name))
		os.renames(old_file_name,new_file_name.encode('utf-8'))


# Public API
__all__= (
		'WriteableItem',   
		'ItemWithStatus',
		'ObservableItem',
		'invert_dictionary'
		
	  
		  )
