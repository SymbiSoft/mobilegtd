from config.config import *
from model.projects import Projects

import appuifw
import thread
from log.logging import logger
from e32 import Ao_lock, in_emulator
from key_codes import *
import key_codes


def show_config(cfg):        
    fields = []
    for k, v in cfg.items():
        v = cfg.format_value(v)
        if isinstance(v, int) or isinstance(v, long):
            tname = 'number'
            v = int(v)
        elif isinstance(v, list) or isinstance(v, tuple):
            for item in v[0]:
                if not isinstance(item, unicode):
                    raise Exception("list can contain only unicode objects, "\
                                    "object %r is not supported" % item)
            
            tname = 'combo'
        elif isinstance(v, unicode):
            tname = 'text'
        else:
            raise Exception("%s has non-supported value" % k)

        fields.append((unicode(k), tname, v))


    form = appuifw.Form(fields=fields, flags=appuifw.FFormEditModeOnly | \
                        appuifw.FFormDoubleSpaced)

    saved = [False]
    def save_hook(param):
        saved[0] = True
    form.save_hook = save_hook
    
    form.execute()

    # return true if user saved, false otherwise
    if not saved[0]:
        return False
    
    for label, tname, value in form:
        if tname == 'combo':
            value = (value[0], int(value[1]))

        cfg[str(label)] = cfg.parse_value(value)

    return True


def no_action():
    pass

def applicable_functions(obj,allowed_function_names):
    function_names = [function_name for function_name in dir(obj) if function_name in allowed_function_names]
    return [eval('obj.%s'%function_name) for function_name in function_names]

def get_key(key_name):
    if key_name == '':
        key = None
    else:
        key=eval('EKey%s'%key_name)
    return key

def all_key_names():
    return filter(lambda entry:entry[0:4]=='EKey',dir(key_codes))
def all_key_values():
    key_values=[
                EKey0,
                EKey1,
                EKey2,
                EKey3,
                EKey4,
                EKey5,
                EKey6,
                EKey7,
                EKey8,
                EKey9,
                EKeyStar,
                EKeyHash,
                ]
    return key_values


def save_gui(object):
    object.old_gui = appuifw.app.body
    object.old_menu = appuifw.app.menu
    object.old_exit_key_handler = appuifw.app.exit_key_handler
    object.old_title=appuifw.app.title
    object.lock = Ao_lock()

def restore_gui(object):
    appuifw.app.body = object.old_gui
    appuifw.app.menu = object.old_menu
    appuifw.app.exit_key_handler = object.old_exit_key_handler
    appuifw.app.title = object.old_title


class ListView(object):
    def __init__(self,title):
        self.title = title
        self.view = appuifw.Listbox(self.items(),self.change_entry)
    
    def change_entry(self):
        pass
    
    def run(self):
        self.adjustment = None
        appuifw.app.screen=COMMON_CONFIG['screen'].encode('utf-8')
        save_gui(self)
        appuifw.app.title=self.title
        appuifw.app.body=self.view
        appuifw.app.exit_key_handler=self.exit
        try:
            self.lock.wait()
            while not self.exit_flag:
                self.refresh()
                self.lock.wait()
        except:
            pass
        restore_gui(self)
    def exit(self):
        self.exit_flag = True
        self.lock.signal()

    def update(self,subject=None):
        #logger.log(u'Updated %s'%repr(self))
        if self.lock:
            self.lock.signal()
        #pass

    def index_changed(self,adjustment=None):
        if adjustment:
            index = self.selected_index() + adjustment
        else:
            index = self.selected_index()
        if index < 0:
            index = len(self.widgets) - 1
        if index >= len(self.widgets):
            index = 0
        self.set_bindings_for_selection(index)

    def refresh(self):
        appuifw.app.menu=self.get_menu_entries()

    def set_index(self,index):
        if index > len(self.widgets):
            index = len(self.widgets)
        if index < 0:
            index = 0
        self.view.set_list(self.items(),index)

    def selected_index(self):
        return self.view.current()


class WidgetBasedListView(ListView):
    def __init__(self,title):
        self.widgets = self.generate_widgets()
        super(WidgetBasedListView,self).__init__(title)
        self.exit_flag = False

    def run(self):
        self.refresh()
        self.set_bindings_for_selection(0)
        ListView.run(self)

    def notify(self,object,attribute,new=None,old=None):
        self.refresh()
    def refresh(self):
        self.widgets = self.generate_widgets()
        self.redisplay_widgets()
        super(WidgetBasedListView,self).refresh()
    def redisplay_widgets(self):
        self.set_index(self.selected_index())
    def items(self):
        return self.all_widget_texts()
    def all_widget_texts(self):
        return [entry.list_repr() for entry in self.widgets]

    

    def current_widget(self):
        return self.widgets[self.selected_index()]
        

class KeyBindingView(object):
    
    def __init__(self,binding_map):
        self.binding_map = binding_map

    def get_menu_entries(self):
        menu_entries=[]
        for key,key_name,description,function in self.key_and_menu_bindings(self.selected_index()):
            if description != '':
                if key:
                    if key_name == 'Backspace': key_name='C'
                    description='[%s] '%key_name +description
                else:
                    description='    '+description
                menu_entries.append((description,function)) 
        menu_entries.append((u'Exit', self.exit))
        return menu_entries       
    def set_bindings_for_selection(self,selected_index):
        self.remove_all_key_bindings()
        
        for key,key_name,description,function in self.key_and_menu_bindings(selected_index):
            if key:
                self.view.bind(key,function)
        self.view.bind(EKeyUpArrow,lambda: self.index_changed(-1))
        self.view.bind(EKeyDownArrow,lambda: self.index_changed(1))
        
    def remove_all_key_bindings(self):
        for key in all_key_values():
            self.view.bind(key,no_action)

class SearchableListView(WidgetBasedListView):
    def __init__(self,title,entry_filters):
        self.current_entry_filter_index = 0
        self.entry_filters = entry_filters
        self.filtered_list = self.entry_filters[0]
        self.lock = None
        super(SearchableListView,self).__init__(title)


    def search_item(self):
        selected_item = appuifw.selection_list(self.all_widget_texts(),search_field=1)
        if selected_item == None or selected_item == -1:
            selected_item = self.selected_index()
        self.view.set_list(self.items(),selected_item)
        self.set_bindings_for_selection(selected_item)
    def switch_entry_filter(self):
        self.current_entry_filter_index += 1
        self.filtered_list = self.entry_filters[self.current_entry_filter_index % len(self.entry_filters)]
        self.refresh()


class EditableListView(SearchableListView,KeyBindingView):
    def __init__(self,title,entry_filters,binding_map):
        KeyBindingView.__init__(self,binding_map)
        super(EditableListView, self).__init__(title,entry_filters)

    def key_and_menu_bindings(self,selected_index):
        key_and_menu_bindings=[]
        for function in applicable_functions(self.widgets[selected_index],self.binding_map)+\
            applicable_functions(self,self.binding_map):
            execute_and_update_function = self.execute_and_update(function)
            (key,description) = self.binding_map[function.__name__]
            key_and_menu_bindings.append((get_key(key),key,description,execute_and_update_function))
        return key_and_menu_bindings

    def change_entry(self):
        self.current_widget().change()
        self.refresh()
    def execute_and_update(self,function):
        return lambda: (function(),self.refresh(),self.index_changed())

    def notify(self,item,attribute,new=None,old=None):
        self.refresh()

#class DisplayableFunction:
#    def __init__(self,display_name,function):
#        self.display_name = display_name
#        self.function = function
#    def list_repr(self):
#        return self.display_name
#    def execute(self):
#        function()

# Public API
__all__= ('EditableListView','show_config')
