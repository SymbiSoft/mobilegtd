import os,re,io,defaultconfig
import appuifw
configuration_regexp = re.compile('(?P<key>[^:]*):(?P<value>.*)',re.U)


class odict(dict):
    def __init__(self):
        self._keys = []
        dict.__init__(self)

    def __setitem__(self, key, item):
        dict.__setitem__(self, key, item)
        if key not in self._keys: self._keys.append(key)

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys
    def __repr__(self):
        return repr(self.items())

    def values(self):
        return map(self.get, self._keys)








class Configuration(odict):
    def __init__(self,complete_file_path,defaults={}):
        odict.__init__(self)
        self.file_path=complete_file_path

        self.read()
        if self.merge(defaults):
            self.write()
            self.read()
    def read(self):
        if not os.path.isfile(self.file_path.encode('utf-8')):
            logger.log(u'Configuration file %s does not exist'%self.file_path)
            return
        for line in io.parse_file_to_line_list(self.file_path):
            if len(line)<1:continue
            if line[0] == '#': continue
            matching = configuration_regexp.match(line)
            key = matching.group('key')
            value = matching.group('value').rstrip(u' \r\n')
    
            self[key]=self.parse_value(value)
    def parse_value(self,value):
        if ',' in value:
            value=value.split(',')
        return value

    def merge(self, other):
        changed = False
        for key in other:
            if key not in self:
                self[key] = other[key]
                changed = True
        return changed

                
    def write(self):
        content = u'\n'.join([u'%s:%s'%(key,self.format_value(value)) for (key,value) in self.items()])
        io.write(self.file_path,content)
    def format_value(self,value):
        if isinstance(value,list):
            return ','.join(value)
        else:
            return value



COMMON_CONFIG = Configuration(defaultconfig.main_config_file,defaultconfig.default_configuration)




gtd_directory = COMMON_CONFIG['path']
inactivity_threshold = int(COMMON_CONFIG['inactivity_threshold'])
read_sms = int(COMMON_CONFIG['read_sms'])
project_directory = gtd_directory+'@Projects/'
ABBREVIATIONS = Configuration(gtd_directory+"abbreviations.cfg",defaultconfig.default_abbreviations)
