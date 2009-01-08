
class ObservableItem(object):
    
    def __init__(self):
        self.observers = []
    def __setattr__(self,name,value):
        #print 'Setting %s to %s'%(name,value)
        self.notify_observers(name, value)
        super(ObservableItem,self).__setattr__(name,value)

    def notify_observers(self,name,value):
        if 'observers' in self.__dict__:
            for observer in self.observers:
                observer.notify(self,name,value)



#class ObservableList(list): 
#    INSERT_ACTION=0 
#    REMOVE_ACTION=1 
#    MODIFY_ACTION=2 
#    def __init__(self, content=None): 
#      """ 
#      @type content: list 
#      @param content: elements to initialize the list's content 
#      """ 
#      # call a super class method can be done two different ways: 
#      # - superClass.method(self, ...) 
#      # - super(superClass, self).method(...) 
#      # It's better to use the second way because if derived class inherits from several classes, 
#      # super will try to find the method in other super classes before 
#      super(ObservableList, self).__init__() 
#      # views can register update callbacks on this notifier 
#      # to be aware of any change in the model 
#      # On change, this object calls Notifier.notify(args) 
#      # which calls every registred function with args 
#      # args = action (insert, remove, modify), elems list, position 
#      self.onChangeNotifier=Notifier() 
#      if content: 
#        self.extend(content) 
#   
#    def __getinitargs__(self): 
#      """Returns the args to pass to the __init__ method to construct this object. 
#      It is usefull to save ObservableList object to minf format. 
#      @rtype: tuple 
#      @return: arg content to pass to the __init__ method for creating a copy of this object 
#      """ 
#      content=[] 
#      content.extend(self) 
#      return (content) 
#   
#    def __reduce__( self ): 
#      """This method is redefined for enable deepcopy of this object (and potentially pickle). 
#      It gives the arguments to pass to the init method of the object when creating a copy 
#   
#      @rtype: tuple 
#      @return: class name, init args, state, iterator on elements to copy, dictionary iterator 
#      """ 
#      # class name, init args, parameters for setstate, elements iterator, dictionary iterator 
#      return ( self.__class__, (), None, iter( self ), None ) 
#   
#    def addListener(self, listener): 
#      """Registers the listener callback method in the notifier. 
#      The method must take 3 arguments : action, elems list, position 
#        - INSERT_ACTION : elems have been inserted at position in the list 
#        - REMOVE_ACTION : elems have been removed [at position] in the list 
#        - MODIFY_ACTION : at position, some elements have been replaced by elems 
#      The position given in the notify method will be between 0 and len(self) 
#   
#      @type listener: function 
#      @param listener: function to call to notify changes 
#      """ 
#      self.onChangeNotifier.add(listener) 
#   
#    def append(self, elem): 
#      """Adds the element at the end of the list. 
#      Notifies an insert action. 
#      """ 
#      index=len(self) 
#      super(ObservableList, self).append(elem) 
#      self.onChangeNotifier.notify(self.INSERT_ACTION, [elem], index) 
#   
#    def extend(self, l): 
#      """Adds the content of the list l at the end of current list. 
#      Notifies an insert action. """ 
#      index=len(self) 
#      super(ObservableList, self).extend(l) 
#      self.onChangeNotifier.notify(self.INSERT_ACTION, l, index) 
#   
#    def insert(self, pos, elem): 
#      """Inserts elem at position pos in the list. 
#      Notifies an insert action. 
#      """ 
#      index=self.getPositiveIndex(pos) 
#      super(ObservableList, self).insert( pos, elem) 
#      self.onChangeNotifier.notify(self.INSERT_ACTION, [elem], index) 
#   
#    def remove(self, elem): 
#      """Removes the first occurence of elem in the list. 
#      Notifies a remove action. """ 
#      super(ObservableList, self).remove( elem) 
#      self.onChangeNotifier.notify(self.REMOVE_ACTION, [elem]) 
#   
#    def pop(self, pos=None): 
#      """Removes the element at position pos or the last element if pos is None. 
#      Notifies a remove action. 
#      @return: the removed element""" 
#      if pos: 
#        index=self.getPositiveIndex(pos) 
#        elem=super(ObservableList, self).pop( pos) 
#      else: 
#        index=len(self)-1 
#        elem=super(ObservableList, self).pop() 
#      self.onChangeNotifier.notify(self.REMOVE_ACTION, [elem], index) 
#      return elem 
#   
#    def sort(self, func=None): 
#      """Sorts the list using function func to compare elements. 
#      Notifies a modify action. 
#      @type func: function elem*elem->int 
#      @param func: comparison function, return -1 if e1<e2, 1 if e1>e2, 0 if e1==e2 
#      """ 
#      super(ObservableList, self).sort( func) 
#      # all the elements of the list could be modified 
#      self.onChangeNotifier.notify(self.MODIFY_ACTION, self, 0) 
#   
#    def reverse(self): 
#      """Inverses the order of the list. 
#      Notifies a modify action.""" 
#      super(ObservableList, self).reverse() 
#      self.onChangeNotifier.notify(self.MODIFY_ACTION, self, 0) 
#   
#    def __setitem__(self, key, value): 
#      """Sets value to element at position key in the list. 
#      Notifies a modify action. 
#   
#      C{l[key]=value} 
#      """ 
#      index=self.getPositiveIndex(key) 
#      super(ObservableList, self).__setitem__( key, value) 
#      self.onChangeNotifier.notify(self.MODIFY_ACTION, [value], index) 
#   
#    def __delitem__(self, key): 
#      """Removes the element at position key in the list. 
#      Notifies a remove action. 
#   
#      C{del l[key]} 
#      """ 
#      index=self.getPositiveIndex(key) 
#      super(ObservableList, self).__delitem__( key) 
#      self.onChangeNotifier.notify(self.REMOVE_ACTION, [], index) 
#   
#    def __setslice__(self, i, j, seq): 
#      """Sets values in seq to elements in the interval i,j. 
#   
#      If i and j are negative numbers, there are converted before this call in index+len(self) 
#      Notifies a modify action. 
#   
#      C{l[i:j]=seq}""" 
#      indexI=self.getIndexInRange(i) 
#      indexJ=self.getIndexInRange(j) 
#      super(ObservableList, self).__setslice__( i, j, seq) 
#      # if the interval is empty, action is insertion at the first position 
#      if indexI>=indexJ: 
#        self.onChangeNotifier.notify(self.INSERT_ACTION, seq, indexI) 
#      else: 
#        lenSeq=len(seq) 
#        lenInter=indexJ-indexI 
#        # if values sequence has same or lower length as the interval in the list, 
#        # all values are written to the list from the first index 
#        # the rest of the interval (if interval is longer than sequence) is left unchanged 
#        if lenInter>=lenSeq: 
#          self.onChangeNotifier.notify(self.MODIFY_ACTION, seq, indexI) 
#        else: 
#          # if the interval is shorter than the sequence of values, 
#          # values in the interval are used to modify the list, 
#          # the rest is inserted at indexJ position 
#          self.onChangeNotifier.notify(self.MODIFY_ACTION, seq[0:lenInter], indexI) 
#          self.onChangeNotifier.notify(self.INSERT_ACTION, seq[lenInter:lenSeq], indexJ) 
#   
#    def __delslice__(self, i, j): 
#      """Removes elements in the interval i,j. 
#   
#      If i and j are negative numbers, there are converted before this call in index+len(self). 
#      Notifies a remove action. 
#   
#      C{del l[i:j]}""" 
#      indexI=self.getIndexInRange(i) 
#      indexJ=self.getIndexInRange(j) 
#      seq=self[indexI:indexJ] 
#      super(ObservableList, self).__delslice__( i, j) 
#      # if the interval is empty, the list is not modified 
#      if indexI<indexJ: 
#        self.onChangeNotifier.notify(self.REMOVE_ACTION, seq, indexI) 
#   
#    def __iadd__(self, l): 
#      """C{list+=l} <=> C{list.extend(l)} 
#   
#      Notifies insert action.""" 
#      index=len(self) 
#      newList=super(ObservableList, self).__iadd__( l) 
#      self.onChangeNotifier.notify(self.INSERT_ACTION, l, index) 
#      return newList 
#   
#    def __imul__(self, n): 
#      """C{list*=n} 
#   
#      Notifies insert action.""" 
#      index=len(self) 
#      newList=super(ObservableList, self).__imul__( n) 
#      self.onChangeNotifier.notify(self.INSERT_ACTION, self[index:], index) 
#      return newList 
#   
#
__all__ = ["ObservableItem"]#,"ObservableList"]