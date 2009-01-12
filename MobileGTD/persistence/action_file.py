import re,os
from model.action import *
from model.model import WriteableItem


class ActionFile(WriteableItem):
	def __init__(self,action):
		self.action = action
		self.update_methods = {'status':self.update_status,'description':self.update_description,'context':self.set_context}
		self.update_done_status()
		self.action.observers.append(self)
		
	def notify(self,action,attribute,new=None,old=None):
		super(ActionFile,self).notify(action,attribute,new=new,old=old)
		if attribute in self.update_methods:
			self.update_methods[attribute](new=new,old=old)
			
	def write(self):
		if self.action.status == active:
			super(ActionFile,self).write()
	
	def update_description(self,new,old=None):
		if self.action.status == active and old:
			self.remove(self.path(description=old))

	def update_status(self,new,old=None):
		if new == inactive or new == done:
			self.remove()

	def set_context(self,new,old=None):
		if self.action.status == active and old:
			self.remove(self.path(context=old))

	def update_done_status(self):
		if self.action.status == active and not self.exists():
			self.action.status = done
			
	def path(self,context=None,description=None):
		if not context:
			context = self.action.context
		if not description:
			description = self.action.description
		return os.path.join(context,description+'.act')
	
	
	def file_string(self):
		string = self.action.project_file_string()
		if self.action.project:
			string = string+u'\nProject: %s'%self.action.project
		return string

