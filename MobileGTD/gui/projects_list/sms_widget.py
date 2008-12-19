from inbox import EInbox,Inbox
INBOX = Inbox(EInbox)


class SMSWidget:
    def __init__(self,sms_id,projects):
        self.sms_id = sms_id
        self.projects = projects
    def content(self):
        return INBOX.content(self.sms_id)
    def change(self):
        self.view_sms()
    def create_project(self):
        infos = []
        lines = sms_regexp.split(self.content())
        
        info_lines = []
        for index in range(len(lines)):
            if len(lines[index]) < 2 and index>0:
                previous = info_lines.pop()
                info_lines.append(previous+lines[index])
            else:
                info_lines.append(lines[index])
        for line in info_lines:
            infos.append(line)
        project = NewProjectWidget(self.projects).change(u'Project for SMS from %s'%self.sender(),infos)
    def remove(self):
        INBOX.delete(self.sms_id)
    def sender(self):
        return INBOX.address(self.sms_id)
    def list_repr(self):
        return u'SMS from %s'%self.sender()
    def name_and_details(self):
        return (self.list_repr(), self.content())

    def view_sms(self):
        save_gui(self)
        t = appuifw.Text()
        t.add(self.list_repr())
        t.add(u':\n')
        t.add(self.content())
        appuifw.app.menu=[(u'Create Project', self.create_project),
        (u'Exit', self.exit_sms_view)]

        appuifw.app.title=self.list_repr()
        appuifw.app.body=t
        appuifw.app.exit_key_handler=self.exit_sms_view
        lock = Ao_lock()
    def exit_sms_view(self):
        self.lock.signal()
        restore_gui(self)
