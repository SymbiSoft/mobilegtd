class Info:
    def __init__(self,text=u''):
        self.text=unicode(text)
    def file_string(self):
        return u'# %s'%self.text

    def gui_string(self):
        return self.text

