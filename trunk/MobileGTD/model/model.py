import os,re
import config.config
import inout.io
from inout.io import u_join,write

from time import *
from observable import *
from log.logging import logger
from config.config import *
from inout.io import *
unprocessed = ('unprocessed',0)
active = ('active',1)
done = ('done',2)
tickled = ('tickled',3)
inactive = ('inactive',4)
someday = ('someday',5)
info = ('info',0)
#logger.log(u'new version')




def invert_dictionary(dictionary):
	return dict([[v,k] for k,v in dictionary.items()])

sign_status_map = {u'+':done,u'-':active,u'!':inactive,u'/':tickled,u'':unprocessed,u'~':someday}
status_sign_map = invert_dictionary(sign_status_map)
status_string_map = {done:u'Done',active:u'active',inactive:u'Inactive',tickled:u'Tickled',unprocessed:u'Unprocessed'}




		
class ItemWithStatus(object):
	def __init__(self,status=inactive):
		self.status = status
	def status_string(self):
		status = self.status
		if status == unprocessed:
			return u''
		else:
			return u'%s '%status_sign_map[status]
	def __cmp__(self,other):
		return other.status[1] - self.status[1]

class WriteableItem(ObservableItem):
	def __init__(self):
		super(WriteableItem, self).__init__()
	def write(self):
		write(self.path(),self.file_string())
	def move_to(self,directory):
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
		extension = os.path.splitext(self.encoded_path())[1]
		new_file_name = os.path.join(self.directory(),new_name+extension)
		
		#logger.log(u'Renaming to %s'%new_file_name)
		
		os.renames(self.encoded_path(),new_file_name.encode('utf-8'))


# Public API
__all__= (
		'unprocessed',
		'active',
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
