class FilteredList(list):
#    def __init__(self,iterable=None):
#        super(FilteredList,self).__init__(iterable)
        
    def with_property(self,property):
        result = FilteredList()
        for item in self:
            if property(item):
                result.append(item)
        return result
    

class StatusFilteredList(FilteredList):
    def with_status(self,status):
        return self.with_property(lambda i:i.status == status)   