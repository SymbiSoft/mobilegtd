from model import ObservableItem
class Info(ObservableItem):
    def __init__(self,text=u''):
        super(Info,self).__init__()
        self.text=text
    def file_string(self):
        return u'# %s'%self.text

    def __str__(self):
        return self.text
    def __repr__(self):
        return repr(self.text)
    def __eq__(self,other):
        return self.text == other.text
    
    def __neq__(self,other):
        return not self.__eq__(other)