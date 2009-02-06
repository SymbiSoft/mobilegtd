
class ObservableItem(object):
    
    def __init__(self):
        self.observers = []
    def __setattr__(self,name,new_value):
        #print 'Setting %s to %s'%(name,value)
        old_value = getattr(self,name,None)
        super(ObservableItem,self).__setattr__(name,new_value)
        self.notify_observers(name,new=new_value, old=old_value)

    def notify_observers(self,name,new=None,old=None):
        if 'observers' in self.__dict__:
            for observer in self.observers:
                observer.notify(self,name,new=new,old=old)



class ObservableList(list,ObservableItem):
    def __init__(self):
        ObservableItem.__init__(self)

    def append(self,item):
        super(ObservableList,self).append(item)
        self.notify_observers('add_item', item, None)   

    def remove(self,item):
        super(ObservableList,self).remove(item)
        self.notify_observers('remove_item', item, None)   

__all__ = ["ObservableItem","ObservableList"]