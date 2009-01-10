class FilteredList(list):
#    def __init__(self,iterable=None):
#        super(FilteredList,self).__init__(iterable)
        
    def with_property(self,property):
        result = FilteredList()
        for item in self:
            if property(item):
                result.append(item)
        return result
    
    