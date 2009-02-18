from model import action
from model import project
from model import datetime


def update_status(e):
    old_status = e.status
    new_status = e.status.update(e)
    if new_status != old_status:
        e.status = new_status 


class ReviewVisitor(object):
    def review(self,projects):
        for p in projects:
            for a in p.actions:
                update_status(a)
#            for a in p.actions_with_status(action.active):
#                a.status = action.done
            update_status(p)
            if p.last_modification_date() <= datetime.date.in_x_days(-5):
                p.status = project.inactive

reviewer = ReviewVisitor()