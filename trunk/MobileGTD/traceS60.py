import sys
import linecache
from e32 import ao_sleep
refresh=lambda:ao_sleep(0)

class trace:        
  def __init__(self,f_all=u'c:\\traceit.txt',f_main=u'c:\\traceitmain.txt'):
      self.out_all=open(f_all,'w')
      self.out_main=open(f_main,'w')
      
  def go(self):    
      sys.settrace(self.traceit)
      
  def stop(self):    
      sys.settrace(None)
      self.out_all.close()
      self.out_main.close()

  def traceit(self,frame, event, arg):
        lineno = frame.f_lineno
        name = frame.f_globals["__name__"]
        file_trace=frame.f_globals["__file__"]
        line=linecache.getline(file_trace,lineno)

        self.out_all.write("%s*%s*of %s(%s)\n*%s*\n" %(event,lineno,name,file_trace,line.rstrip()))
        refresh()
        return self.traceit



