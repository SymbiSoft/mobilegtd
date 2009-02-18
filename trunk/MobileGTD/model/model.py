import os,re,sys
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

def no_transition_policy(self,owner):
	return self



class Status(object):
    symbols = {}
    names = {}
    def __init__(self,name,value=0,symbol=u'',transition_policy=no_transition_policy):
        self.name = name
        self.value = value
        self.symbol = symbol
        Status.symbols[symbol] = self
        Status.names[name] = self
        self.transition_policy = transition_policy

    def __eq__(self,other):
#    	print "Called eq with %s (%s) and %s (%s)"%(repr(self),type(self),repr(other),type(other))
#    	if self == other:
#    		return True
    	if (not self and other) or (not other and self):
    		return False
    	return self.name == other.name #and self.value == other.value and type(self) == type(other)
    
    def __cmp__(self,other):
        if not other:
            return 1
        return other.value - self.value

    def __str__(self):
        return self.name

    def __repr__(self):
    	return "%s %s %s (%s)"%(type(self),self.value, self.name,id(self))
     
    def symbol(self):
        return self.symbol
    
    def get_status(symbol):
        return Status.symbols[symbol]
    get_status = staticmethod(get_status)

    def get_status_for_name(name):
    	return Status.names[name]
    get_status_for_name = staticmethod(get_status_for_name)

    def update(self,owner):
        return self.transition_policy(self,owner)


	
class ItemWithStatus(object):
	def __init__(self,status):
		self.status = status

	def status_symbol(self):
		if self.status.symbol and len(self.status.symbol) > 0:
			return self.status.symbol + u' '
		else:
			return u''

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
			logger.log(u'Moved %s to %s'%(repr(old_file_name),repr(new_file_name)))
			return new_file_name
		except OSError,e:
			logger.log(u'Cannot move %s to %s: %s'%(repr(old_file_name),repr(new_file_name),e.strerror))
			raise e

		
	def directory(self):
		return os.path.dirname(self.encoded_path())
	def file_name(self):
		return os.path.basename(self.encoded_path())
	def remove(self,path=None):
		if not path:
			encoded_path = self.encoded_path()
		else:
			encoded_path = path.encode('utf-8')
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

	def notify(self,action,attribute,new=None,old=None):
		self.write()

# Public API
__all__= (
		'WriteableItem',   
		'ItemWithStatus',
		'ObservableItem',
		'invert_dictionary',
		'Status'
	  
		  )
