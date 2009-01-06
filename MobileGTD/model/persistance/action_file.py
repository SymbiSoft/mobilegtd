import re,os
from model.model import *



class ActionFile(WriteableItem):
	def __init__(self,action):
		self.action = action
		self.action.observers.append(self)
		self.update_methods = {'status':self.update_status,'description':self.update_description,'context':self.set_context}
		
	def notify(self,action,attribute,value):
		if attribute in self.update_methods:
			self.update_methods[attribute](value)
			
	def update_description(self,value):
		if self.action.status == processed:
			self.rename(value)
			
	def update_status(self,value):
		if value == processed:
			self.write()
		elif value == inactive or value == done:
			self.remove()
		
	def set_context(self,context):
		if self.action.status == processed:
			self.move_to(context)
	def update_done_status(self):
		if self.action.status == processed and not self.exists():
			self.action.status = done
			
	def path(self):
		return os.path.join(self.action.context,self.action.description+'.act')
	
	
	def file_string(self):
		string = self.action.project_file_string()
		if self.action.project:
			string = string+u'\nProject: %s'%self.action.project
		return string