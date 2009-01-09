import re,os
from model.model import *



class ActionFile(WriteableItem):
	def __init__(self,action):
		self.action = action
		self.action.observers.append(self)
		self.update_methods = {'status':self.update_status,'description':self.update_description,'context':self.set_context,'info':self.set_info}
		
	def notify(self,action,attribute,value):
		if attribute in self.update_methods:
			self.update_methods[attribute](value)
			
	def update_description(self,value):
		if self.action.status == active:
			self.rename(value)
			self.write_if_active()

	def write_if_active(self,status = None):
		if status == None:
			status = self.action.status
		if status == active:
			self.write()
	def update_status(self,value):
		self.write_if_active(value)
		if value == inactive or value == done:
			self.remove()

	def set_info(self,info):
			self.write_if_active()
#		pass

	def set_context(self,context):
		if self.action.status == active:
			self.move_to(context)
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