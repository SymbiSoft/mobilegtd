import io.io,os,re,config.config
from time import *

from logging.logging import logger
from config.config import *
from io.io import *
unprocessed = 0
processed = 1
done = 2
tickled = 3
inactive = 4
someday = 5
info = 2
#logger.log(u'new version')

def make_string_stripper(to_strip):
    return lambda x: x.replace(to_strip,'')



def invert_dictionary(dictionary):
    return dict([[v,k] for k,v in dictionary.items()])

sign_status_map = {u'+':done,u'-':processed,u'!':inactive,u'/':tickled,u'':unprocessed,u'~':someday}
status_sign_map = invert_dictionary(sign_status_map)
status_string_map = {done:u'Done',processed:u'Processed',inactive:u'Inactive',tickled:u'Tickled',unprocessed:u'Unprocessed'}
project_dir_status_map = {u'Done':done,u'Review':inactive,u'Someday':someday,u'Tickled':tickled}
status_project_dir_map = invert_dictionary(project_dir_status_map)

file_name_regexp = re.compile('/?(?P<path>.*/)*(?P<file_name>.*)\....',re.U)

def parse_lines(lines):
    actions = []
    infos = []
    for line in lines:
        if len(line) < 3:
            continue
        elif line[0]=='#':
            infos.append(Info(line[1:].strip()))
        else:
            actions.append(parse_action(line))
    return (actions,infos)



def compare_by_status(x,y):
    return y.status - x.status


class ItemWithStatus(object):
    def status_string(self):
        status = self.get_status()
        if status == unprocessed:
            return u''
        else:
            return u'%s '%status_sign_map[status]


class WriteableItem(ItemWithStatus):
    def __init__(self):
        super(WriteableItem, self).__init__()
    def write(self):
        io.write(u'%s/%s'%(self.path(),self.file_name()),self.file_string())
    def move_to(self,directory):
        self.write()
        new_file_name = u_join(directory,self.file_name())
        old_file_name = u_join(self.path(),self.file_name())
        try:
            os.renames(old_file_name.encode('utf-8'),new_file_name.encode('utf-8'))
            ##logger.log(u'Moved %s to %s'%(repr(old_file_name),repr(new_file_name)))
            return new_file_name
        except OSError:
            #logger.log(u'Cannot move %s to %s: File already exists'%(repr(old_file_name),repr(new_file_name)))
            return old_file_name






# Public API
__all__= ('Projects',
          'Project',
          'Action',
          'Info',
          'unprocessed',
            'processed',
            'done',
            'tickled',
            'inactive',
            'someday',
            'info',
            'parse_action',
            'parse_action_line',
            'parse_context'
          
          )
