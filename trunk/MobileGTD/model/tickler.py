import re
date_regexp = re.compile('(?P<number>\d{1,2})(\D.*)?\Z',re.U)
class TickleDirectory:
    
    def __init__(self,path):
        self.path = path
    def is_obsolete(self):
        import datetime
        date = self.date()
        if not date:
            # This directory is not a month-day directory
            return False
        obsolete = date <= datetime.datetime.now()
        return obsolete
    def date(self):
        import datetime
        spp = self.path.split(u'/')
        year = datetime.datetime.now().year
        try:
            if len(spp) < 2 or len(spp[0]) == 0:
                month_match = date_regexp.match(spp[-1])
                if month_match == None:
                    return None
                month = int(month_match.group('number').rstrip(u' \r\n'))
                day = 1
            else:
                month_match = date_regexp.match(spp[-2])
                day_match = date_regexp.match(spp[-1])
                if month_match == None or day_match == None:
                    return None
                month = int(month_match.group('number').rstrip(u' \r\n'))
                day = int(day_match.group('number').rstrip(u' \r\n'))
                
                if len(spp) > 2:
                    try:
                        year = int(spp[-3].rstrip(u' \r\n'))
                    except:
                        pass
                               
                
        except ValueError:
            logger.log(repr(spp))
        return datetime.datetime(year,month,day)
