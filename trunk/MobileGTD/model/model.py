import os,re
import config.config
import inout.io
from inout.io import u_join,write

from time import *

from log.logging import logger
from config.config import *
from inout.io import *
unprocessed = 0
processed = 1
done = 2
tickled = 3
inactive = 4
someday = 5
info = 2
#logger.log(u'new version')




def invert_dictionary(dictionary):
	return dict([[v,k] for k,v in dictionary.items()])

sign_status_map = {u'+':done,u'-':processed,u'!':inactive,u'/':tickled,u'':unprocessed,u'~':someday}
status_sign_map = invert_dictionary(sign_status_map)
status_string_map = {done:u'Done',processed:u'Processed',inactive:u'Inactive',tickled:u'Tickled',unprocessed:u'Unprocessed'}




class ObservableItem(object):
	
	def __init__(self):
		self.observers = []
	def __setattr__(self,name,value):
		#print 'Setting %s to %s'%(name,value)
		if 'observers' in self.__dict__:
			for observer in self.observers:
				observer.notify(self,name,value)
		super(ObservableItem,self).__setattr__(name,value)
		
class ItemWithStatus(object):
	def status_string(self):
		status = self.status
		if status == unprocessed:
			return u''
		else:
			return u'%s '%status_sign_map[status]
	def __cmp__(self,other):
		return other.status - self.status

class WriteableItem(ObservableItem):
	def __init__(self):
		super(WriteableItem, self).__init__()
	def write(self):
		write(self.path(),self.file_string())
	def move_to(self,directory):
		self.write()
		new_file_name = os.path.join(directory,self.file_name())
		old_file_name = self.path()
		try:
			os.renames(old_file_name.encode('utf-8'),new_file_name.encode('utf-8'))
			##logger.log(u'Moved %s to %s'%(repr(old_file_name),repr(new_file_name)))
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

	def rename(self,new_name):
		self.write()
		extension = os.path.splitext(self.encoded_path())[1]
		new_file_name = os.path.join(self.directory(),new_name+extension)
		
		#logger.log(u'Renaming to %s'%new_file_name)
		
		os.renames(self.encoded_path(),new_file_name.encode('utf-8'))


# Public API
__all__= (
		'unprocessed',
		'processed',
		'done',
		'tickled',
		'inactive',
		'someday',
		'info',
		'WriteableItem',   
		'ItemWithStatus',
		'ObservableItem',
		'sign_status_map',
		'status_sign_map',
		'status_string_map',
		'invert_dictionary'
		
	  
		  )
