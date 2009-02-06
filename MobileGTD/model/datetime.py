import time as t
import calendar
from types import InstanceType
    
MINYEAR = 1
MAXYEAR = 9999
    
class DaysInMonth:
    def calculate(self, year, month):
        return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month] + (month == 2 and self.isleap(year))
    
    def isleap(self, year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    
    def test(self):
        passed = True
        for year in range (1,9999):
            for month in range(1,12):
                if DaysInMonth().calculate(year, month) <> calendar.monthrange(year, month)[1]:
                    print "Failed on %s-%s."%(year, month)
                    passed = False
        if not passed:
            print "FAILED"
        else:
            print "PASSED"
        return passed
        
    def weekday(self, year, month, day):
        secs = mktime((year, month, day, 0, 0, 0, 0, 0, 0))
        tuple = localtime(secs)
        return tuple[6]
    
    

daysInMonth = DaysInMonth()
       
class datetime:
    def __init__(self,year,month,day,hour=0,minute=0,second=0,microsecond=0):
        dates = ['year','month','day','hour','minute']
        counter = 0
        for item in [year,month,day,hour,minute]:
            if type(item) not in [type(1), type(1L)]:
                raise TypeError("The variable '%s' should be an integer."%dates[counter])
            counter += 1
        
        if type(second) not in [type(1), type(1L)]:# and type(second) <> type(1.004):
            raise ValueError("The variable 'second' should be an Integer or a Long.")# or a float.")

        # Very basic error checking and initialisation.
        if year < MINYEAR or year > MAXYEAR:
            raise ValueError('The year value must be between %s and %s inclusive.'%(MINYEAR, MAXYEAR))
        else:
            self.year = year
        if month < 1 or month > 12:
            raise ValueError('The month value must be between 1 and 12 inclusive.')
        else:
            self.month = month
        if day < 1 or day > daysInMonth.calculate(year, month):
            raise ValueError('The day value must be between 1 and %s inclusive.'%daysInMonth.calculate(year, month))
        else:    
            self.day = day
        if hour < 0 or hour > 23:
            raise ValueError('The hour value must be between 0 and 23 inclusive.')
        else:
            self.hour = hour
        if minute < 0 or minute > 59:
            raise ValueError('The minutes value must be between 0 and 59 inclusive.')
        else:
            self.minute = minute
        if second < 0 or second > 59:
            raise ValueError('The seconds value must be between 0 and 59 inclusive.')
        else:    
            self.second = second 
        if microsecond < 0 or microsecond > 1000000:
            raise ValueError('The microseconds value must be between 0 and 1000000 inclusive.')
        else:    
            self.microsecond = microsecond
    
    def now(self=None):
        now = t.localtime()
        return datetime(now[0],now[1],now[2],now[3],now[4],now[5])
    now = staticmethod(now)

#
# Comparison Operators.
#

    def _compareDate(self, other):
        if self.year == other.year:
            if self.month == other.month:
                if self.day == other.day:
                    return 0
                elif self.day > other.day:
                    return 1
                else:
                    return -1
            elif self.month > other.month:
                return 1
            else:
                return -1
        elif self.year > other.year:
            return 1
        else:
            return -1
            
    def _compareTime(self, other):
        if self.hour == other.hour:
            if self.minute == other.minute:
                if self.second == other.second:
                    return 0
                elif self.second > other.second:
                    return 1
                else:
                    return -1
            elif self.minute > other.minute:
                return 1
            else:
                return -1
        elif self.hour > other.hour:
            return 1
        else:
            return -1
            
                        
    def __cmp__(self, other):
        if type(other) is type(None):
            raise Exception('Comparison of %s (%s) with %s (%s) is not supported'%(self,type(self),other,type(other)))
        elif type(other) is InstanceType:
#            if other.__class__.__name__ == self.__class__.__name__:
                if other.__class__.__name__ == 'date':
                    return self._compareDate(other)
                elif other.__class__.__name__ == 'time':
                    return self._compareTime(other)
                elif other.__class__.__name__ == 'datetime':
                    date = self._compareDate(other)
                    if date == 0:
                        return self._compareTime(other)
                    else:
                        return date
                else:
                    raise Exception('Comparison of %s (%s) with %s (%s) is not supported'%(self,type(self),other,type(other)))
#            else:
#                raise Exception('Comparison of %s (%s) with %s (%s) is not supported'%(self,self.__class__,other,other.__class__))
        else:
            raise Exception('Comparison of %s (%s) with %s (%s) is not supported'%(self,type(self),other,type(other)))
            
    def __eq__(self, other):
        if type(other) is InstanceType:
            if other.__class__.__name__ == self.__class__.__name__:
                if other.__class__.__name__ == 'date':
                    if self._compareDate(other) == 0:
                        return 1
                    else:
                        return 0
                elif other.__class__.__name__ == 'time':
                    if self._compareTime(other) == 0:
                        return 1
                    else:
                        return 0
                elif other.__class__.__name__ == 'datetime':
                    date = self._compareDate(other)
                    if date == 0:
                        if self._compareTime(other) == 0:
                            return 1
                        else:
                            return 0
                    else:
                        return 0
                else:
                    return 0
            else:
                return 0
        else:
            return 0
            
    def __ne__(self, other):
        if self.__eq__(other):
            return 0
        else:
            return 1
            
    def __str__(self):
        return self.isoformat()

    def __repr__(self):
        return "datetime.datetime(%s,%s,%s,%s,%s,%s)"%(self.year, self.month, self.day, self.hour, self.minute, self.second)
    
    def __getitem__(self, item):
        if item == 'year':
            return self.year
        elif item == 'month':
            return self.month
        elif item == 'day':
            return self.day
        elif item == 'hour':
            return self.hour
        elif item == 'minute':
            return self.minute
        elif item == 'second':
            return self.second
        else:
            raise KeyError("'%s' is not a valid attribute for a Date class."%item)

#
# Formatting
#

    def _addZeros(self,num,s):
        s = str(s)
        while( len(s) < num ):
            s = '0'+s
        return s
        
    def _isodate(self):
        return str(self._addZeros(4,self.year))+"-"+str(self._addZeros(2,self.month))+"-"+str(self._addZeros(2,self.day))

    def _isotime(self):
        return str(self._addZeros(2,self.hour))+":"+str(self._addZeros(2,self.minute))+":"+str(self._addZeros(2,self.second))#str(self._addZeros(2,int(self.second)))+'.'+s
   
    def strftime(self, format):
        #raise Exception(self.timetuple())
        return t.strftime(format, self.timetuple()) 

    

#
# Conversion
#

    def timetuple(self):
        sql =  self.isoformat()
        wday = calendar.weekday(int(sql[0:4]),int(sql[5:7]),int(sql[8:10]))
        return (int(sql[0:4]),int(sql[5:7]),int(sql[8:10]),int(sql[11:13]),int(sql[14:16]),int(sql[17:19]),wday,0,-1)#,0,0,-1) ,0,0,-1) 
        
    def isoformat(self):
        return self._isodate() + ' ' + self._isotime()

    
class date(datetime):
    def __init__(self,year,month,day):
        
        dates = ['year','month','day']
        counter = 0
        for item in [year,month,day]:
            if type(item) not in [ type(1), type(1L)]:
                raise TypeError("The variable '%s' should be an Integer or a Long."%dates[counter])
            counter += 1
        
     
        # Very basic error checking and initialisation.
        if year < MINYEAR or year > MAXYEAR:
            raise ValueError('The year value must be between %s and %s inclusive.'%(MINYEAR, MAXYEAR))
        else:
            self.year = year
        if month < 1 or month > 12:
            raise ValueError('The month value must be between 1 and 12 inclusive.')
        else:
            self.month = month
        if day < 1 or day > daysInMonth.calculate(year, month):
            raise ValueError('The day value must be between 1 and %s inclusive.'%daysInMonth.calculate(year, month))
        else:    
            self.day = day
        
    def __repr__(self):
        return "datetime.date(%s,%s,%s)"%(self.year,self.month, self.day)
        
    def isoformat(self):
        return self._isodate()
        
    def timetuple(self):
        sql = self.isoformat()
        wday = calendar.weekday(int(sql[0:4]),int(sql[5:7]),int(sql[8:10]))
        return (int(sql[0:4]),int(sql[5:7]),int(sql[8:10]),0,0,0,wday,0,-1)
    
    def now(self=None):
        now = t.localtime()
        return date(now[0],now[1],now[2])
    now = staticmethod(now)

    def in_x_days(number_of_days=0):
        secs = t.mktime(t.localtime())
        day_secs = secs+24*60*60*number_of_days
        day = t.localtime(day_secs)
        return date(day[0],day[1],day[2])
    in_x_days=staticmethod(in_x_days)  
    
    def tomorrow():
        return date.in_x_days(1)
    tomorrow = staticmethod(tomorrow)
        
class time(datetime):
    
    def __init__(self,hour=0,minute=0,second=0,microsecond=0):
        
        dates = ['hour','minute']
        counter = 0
        for item in [hour,minute]:
            if type(item) not in [type(1), type(1L)]:
                raise TypeError("The variable '%s' should be an Integer or a Long."%dates[counter])
            counter += 1
        
        if type(second) <> type(1):# and type(second) <> type(1.004):
            raise ValueError("The variable 'second' should be an integer.")# or a float.")

        # Very basic error checking and initialisation.
       
        if hour < 0 or hour > 23:
            raise ValueError('The hour value must be between 0 and 23 inclusive.')
        else:
            self.hour = hour
        if minute < 0 or minute > 59:
            raise ValueError('The minutes value must be between 0 and 59 inclusive.')
        else:
            self.minute = minute
        if second < 0 or second > 59:
            raise ValueError('The seconds value must be between 0 and 59 inclusive.')
        else:    
            self.second = second
        if microsecond < 0 or microsecond > 1000000:
            raise ValueError('The microseconds value must be between 0 and 1000000 inclusive.')
        else:    
            self.microsecond = microsecond
        
    def __repr__(self):
        return "datetime.time(%s,%s,%s)"%(self.hour, self.minute, self.second)
        
    def isoformat(self):
        return self._isotime()
        
    def timetuple(self):
        raise AttributeError('time objects do not have a timetuple method.')

    def now(self):
        now = t.localtime()
        return time(now[3],now[4],now[5])
        
