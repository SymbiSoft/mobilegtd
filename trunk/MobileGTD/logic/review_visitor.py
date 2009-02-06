from model import action
from model import project
from model import datetime


class ReviewVisitor(object):
    def review(self,projects):
        for p in projects:
            for a in p.actions:
                a.update_status()
#            for a in p.actions_with_status(action.active):
#                a.status = action.done
            p.update_status()
            if p.last_modification_date() <= datetime.date.in_x_days(-5):
                p.status = project.inactive
