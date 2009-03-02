import os
from inout import io

class FileLogger:
    def __init__(self,file_path=u'C:/mobile_gtd.log',log_level = 8):
        self.entries = []
        self.file_path = file_path
        self.file_path = 'C:/Data/GTD/mobile_gtd.log'
        self.log_level = log_level
        #self.log_file = file(io.os_encode(file_path),'w')
        io.create_file(self.file_path).close
        self.log_file = file(self.file_path,'a')
    def log_stderr(self):
        import sys
        self.old_stderr = sys.stderr
        sys.stderr = self.log_file
        sys.stderr.write('stderr logged from logging\n')
        self.log_file.flush()

    def unlog_stderr(self):
        import sys
        sys.stderr = self.old_stderr
    def log(self,text,level=0):
        if level < self.log_level:          
            self.log_file.write(io.os_encode(text)+'\n')
            self.log_file.flush()
    def close(self):
        #sys.stderr.flush()
        self.unlog_stderr()
        self.log(u'Closing log')
        self.log_file.flush()
        self.log_file.close()
        
        

class ConsoleLogger:
    def __init__(self,log_level = 8):
        self.log_level = log_level
    def log(self,text,level=0):
        import appuifw
        if level < self.log_level:
            appuifw.note(u''+repr(text))
    def close(self):
        pass

class NullLogger:
    def log(self,text,level=0):
        pass
    def log_stderr(self):
        pass
    def close(self):
        pass
        
#logger=FileLogger(gtd_directory+'gtd.log')
# Need NullLogger during initialization of FileLogger
#logger=NullLogger()
logger=FileLogger()
#logger=ConsoleLogger()
