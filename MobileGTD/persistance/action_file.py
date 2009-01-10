import re,os
from model.action import *
from model.model import WriteableItem


class ActionFile(WriteableItem):
	def __init__(self,action):
		self.action = action
		self.action.observers.append(self)
		self.update_methods = {'status':self.update_status,'description':self.update_description,'context':self.set_context,'info':self.set_info}
		
	def notify(self,action,attribute,new=None,old=None):
		if attribute in self.update_methods:
			self.update_methods[attribute](new=new,old=old)
			
	def update_description(self,new,old=None):
		if self.action.status == active:
			self.rename(new,old)
			self.write_if_active()

	def write_if_active(self,status = None):
		if status == None:
			status = self.action.status
		if status == active:
			self.write()
	def update_status(self,new,old=None):
		self.write_if_active(new)
		if new == inactive or new == done:
			self.remove()

	def set_info(self,new,old=None):
			self.write_if_active()
#		pass

	def set_context(self,new,old=None):
		if self.action.status == active:
			self.move_to(new)
			self.write_if_active()
	def update_done_status(self):
		if self.action.status == active and not self.exists():
			self.action.status = done
			
	def path(self):
		return os.path.join(self.action.context,self.action.description+'.act')
	
	
	def file_string(self):
		string = self.action.project_file_string()
		if self.action.project:
			string = string+u'\nProject: %s'%self.action.project
		return string

