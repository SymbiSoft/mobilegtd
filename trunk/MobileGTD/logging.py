import os, io
from config import gtd_directory

class FileLogger:
    def __init__(self,file_path=u'C:/mobile_gtd.log',log_level = 8):
        self.entries = []
        self.file_path = file_path
        self.log_level = log_level
        io.write(file_path,u'')
        #self.log_file = file(file_path.encode('utf-8'),'w')
    def log(self,text,level=0):
        if level < self.log_level:
            self.log_file = file(self.file_path,'a')
            self.log_file.write(text.encode('utf-8')+'\n')
            self.log_file.close()
    def close(self):
        self.log_file.close()

class ConsoleLogger:
    def __init__(self,log_level = 8):
        self.log_level = log_level
    def log(self,text,level=0):
        if level < self.log_level:
            appuifw.note(u''+repr(text))
    def close(self):
        pass

class NullLogger:
    def log(self,text,level=0):
        pass
    def close(self):
        pass
        
#logger=FileLogger(gtd_directory+'gtd.log')
#logger=NullLogger()
logger=FileLogger()