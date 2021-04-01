#import sys

TRANSIENT = 4
IGNORECASE = 2
LITERAL = 1


################# Added stuff ###################################################

def _etrace(*args):
    s = ' | '.join(map(str, args))
    print('EMUL', s)

# Current window.
_window = None # Window(909)

# Current views.
_views = []
_view_id = 100

# Settings.
_settings = None # Settings(1234)


################# Functions ###################################################

def version():
    return 'sublime_api.version()'

# def executable_path():
#     return sublime_api.executable_path()

def packages_path():
    return r'C:\Users\cepth\AppData\Roaming\Sublime Text 3\Packages'

# def installed_packages_path():
#     return sublime_api.installed_packages_path()

def status_message(msg):
    _etrace('status_message', msg)
    # sublime_api.status_message(msg)

def error_message(msg):
    _etrace('error_message', msg)
    # sublime_api.error_message(msg)

def message_dialog(msg):
    _etrace('message_dialog', msg)
    # sublime_api.message_dialog(msg)

def ok_cancel_dialog(msg, ok_title=""):
    _etrace('ok_cancel_dialog', msg)
    # return sublime_api.ok_cancel_dialog(msg, ok_title)

def run_command(cmd, args=None):
    _etrace('run_command', cmd, args)
    # sublime_api.run_command(cmd, args)

def set_clipboard(text):
    pass
    # return sublime_api.set_clipboard(text)

def load_settings(base_name):
    global _settings
    if _settings is None:
        _settings = Settings(1234)
    return _settings
    #settings_id = sublime_api.load_settings(base_name)
    #return Settings(settings_id)

def set_timeout(f, timeout_ms=0):
    """ Schedules a function to be called in the future. Sublime Text will block while the function is running """
    f()
    #sublime_api.set_timeout(f, timeout_ms)

def active_window():
    return _window
    # return Window(sublime_api.active_window())


################# View ###################################################

class View():
    def __init__(self, view_id):
        self.view_id = view_id
        self.buffer = ''
        self.selection = Selection(view_id)

    def __len__(self):
        return self.size()

    # def __eq__(self, other):
    #     pass
    #     # return isinstance(other, View) and other.view_id == self.view_id

    # def __bool__(self):
    #     pass
    #     # return self.view_id != 0

    def id(self):
        return self.view_id

    def window(self):
        return _window
        # window_id = sublime_api.view_window(self.view_id)
        # if window_id == 0:
        #     return None
        # else:
        #     return Window(window_id)

    def file_name(self):
        return 'test_file_name_{}'.format(self.view_id)
        # name = sublime_api.view_file_name(self.view_id)
        # if len(name) == 0:
        #     return None
        # else:
        #     return name

    def is_loading(self):
        return False
        # return sublime_api.view_is_loading(self.view_id)

    def close(self):
        return True
        # window_id = sublime_api.view_window(self.view_id)
        # return sublime_api.window_close_file(window_id, self.view_id)

    def set_scratch(self, scratch):
        pass
        # return sublime_api.view_set_scratch(self.view_id, scratch)

    def size(self):
        return len(self.buffer)
        # return sublime_api.view_size(self.view_id)

    def settings(self):
        return _settings
        # if not self.settings_object:
        #     self.settings_object = Settings(sublime_api.view_settings(self.view_id))
        # return self.settings_object

    def show_popup(self, content, flags=0, location=-1, max_width=320, max_height=240, on_navigate=None, on_hide=None):
        _etrace('View.show_popup')
        # sublime_api.view_show_popup(
        #     self.view_id, location, content, flags, max_width, max_height,
        #     on_navigate, on_hide)

    def substr(self, x):
        return 'TODO-T'
        # if isinstance(x, Region):
        #     return sublime_api.view_cached_substr(self.view_id, x.a, x.b)
        # else:
        #     s = sublime_api.view_cached_substr(self.view_id, x, x + 1)
        #     # S2 backwards compat
        #     if len(s) == 0:
        #         return "\x00"
        #     else:
        #         return s

    def insert(self, edit, pt, text):
        return True # TODO-T
        # if edit.edit_token == 0:
        #     raise ValueError("Edit objects may not be used after the TextCommand's run method has returned")
        # return sublime_api.view_insert(self.view_id, edit.edit_token, pt, text)

    def replace(self, edit, r, text):
        return True # TODO-T
        # if edit.edit_token == 0:
        #     raise ValueError("Edit objects may not be used after the TextCommand's run method has returned")
        # sublime_api.view_replace(self.view_id, edit.edit_token, r, text)

    def run_command(self, cmd, args=None):
        return True # TODO-T
        # sublime_api.view_run_command(self.view_id, cmd, args)
# view.run_command('append', {'characters': text }) # insert has some odd behavior - indentation
# view.run_command("goto_line", {"line": line})
# view.run_command("expand_selection", {"to": "line"})
# view.run_command(menu_items[index]['command'], {'cmd': cmd})

    def sel(self):
        return self.selection

    def find(self, pattern, start_pt, flags=0):
        return True # TODO-T
        # return sublime_api.view_find(self.view_id, pattern, start_pt, flags)

    def find_all(self, pattern, flags=0, fmt=None, extractions=None):
        return True # TODO-T
        # if fmt is None:
        #     return sublime_api.view_find_all(self.view_id, pattern, flags)
        # else:
        #     results = sublime_api.view_find_all_with_contents(self.view_id, pattern, flags, fmt)
        #     ret = []
        #     for region, contents in results:
        #         ret.append(region)
        #         extractions.append(contents)
        #     return ret

    def scope_name(self, pt):
        return 'TODO-T'
        # return sublime_api.view_scope_name(self.view_id, pt)

    def style_for_scope(self, scope):
        return 'TODO-T'
        # return sublime_api.view_style_for_scope(self.view_id, scope)

    def split_by_newlines(self, r):
        return ['TODO-T']
        # return sublime_api.view_split_by_newlines(self.view_id, r)

    def word(self, x):
        return 'TODO-T'
        # if isinstance(x, Region):
        #     return sublime_api.view_word_from_region(self.view_id, x)
        # else:
        #     return sublime_api.view_word_from_point(self.view_id, x)

    def rowcol(self, tp):
        return (-1, -1)
        # return sublime_api.view_row_col(self.view_id, tp)

    def text_point(self, row, col):
        return False # TODO-T
        # return sublime_api.view_text_point(self.view_id, row, col)

    def add_regions(self, key, regions, scope="", icon="", flags=0):
        pass # TODO-T
        # if not isinstance(icon, "".__class__):
        #     raise ValueError("icon must be a string")
        # sublime_api.view_add_regions(self.view_id, key, regions, scope, icon, flags)

    def get_regions(self, key):
        pass # TODO-T
        # return sublime_api.view_get_regions(self.view_id, key)

    def erase_regions(self, key):
        pass # TODO-T
        # sublime_api.view_erase_regions(self.view_id, key)

    def set_status(self, key, value):
        _etrace('set_status', key, value)
        # sublime_api.view_set_status(self.view_id, key, value)


################# Window ###################################################

class Window():
    def __init__(self, view_id):
        self.window_id = view_id
        self.settings_object = None

    def id(self):
        return self.window_id

    def active_view(self):
        return _views[0]
        # view_id = sublime_api.window_active_view(self.window_id)
        # if view_id == 0:
        #     return None
        # else:
        #     return View(view_id)

    def show_input_panel(self, caption, initial_text, on_done, on_change, on_cancel):
        _etrace('Window.show_input_panel')
        # return View(sublime_api.window_show_input_panel(self.window_id, caption, initial_text, on_done, on_change, on_cancel))

    def show_quick_panel(self, items, on_select, flags=0, selected_index=-1, on_highlight=None):
        _etrace('Window.show_quick_panel')
        # No return

    def project_file_name(self):
        return 'test_sbot.sublime-project'
        # name = sublime_api.window_project_file_name(self.window_id)
        # if len(name) == 0:
        #     return None
        # else:
        #     return name

    def settings(self):
        """ Per-window settings, the contents are persisted in the session """
        return _settings
        # if not self.settings_object:
        #     self.settings_object = Settings(sublime_api.window_settings(self.window_id))
        # return self.settings_object

    def run_command(self, cmd, args=None):
        return True # TODO-T
        # sublime_api.window_run_command(self.window_id, cmd, args)
# window.run_command("focus_group", { "group": 1 } )
# window.run_command("close_file")
# window.run_command("set_layout", { "cols": [0.0, 1.0], "rows": [0.0, 1.0], "cells": [[0, 0, 1, 1]] } )
# window.run_command("clone_file")
# window.run_command("move_to_group", { "group": 1 } )

    def new_file(self, flags=0, syntax=""):
        """ flags must be either 0 or TRANSIENT """
        return None # TODO-T
        # return View(sublime_api.window_new_file(self.window_id, flags, syntax))

    def open_file(self, fname, flags=0, group=-1):
        """
        valid bits for flags are:
        ENCODED_POSITION: fname name may have :row:col or :row suffix
        TRASIENT: don't add the file to the list of open buffers
        FORCE_GROUP: don't select the file if it's opened in a different group
        """
        return None # TODO-T
        # return View(sublime_api.window_open_file(self.window_id, fname, flags, group))

    def find_open_file(self, fname):
        return None # TODO-T
        # view_id = sublime_api.window_find_open_file(self.window_id, fname)
        # if view_id == 0:
        #     return None
        # else:
        #     return View(view_id)

    def focus_view(self, view):
        pass
        # if view:
        #     sublime_api.window_focus_view(self.window_id, view.view_id)

    def get_view_index(self, view):
        return (-1, -1)  # TODO-T #group, and index
        # if view:
        #     return sublime_api.window_get_view_index(self.window_id, view.view_id)
        # else:
        #     return (-1, -1)

    def views(self):
        return None # TODO-T
        # view_ids = sublime_api.window_views(self.window_id)
        # return [View(x) for x in view_ids]

    def layout(self):
        return None # TODO-T
        # return sublime_api.window_get_layout(self.window_id)

    def project_data(self):
        return None # TODO-T
        # return sublime_api.window_get_project_data(self.window_id)

    def set_project_data(self, v):
        pass # TODO-T
        # sublime_api.window_set_project_data(self.window_id, v)


################# Region ###################################################

class Region():
    def __init__(self, a, b=None, xpos=-1):
        if b is None:
            b = a
        self.a = a
        self.b = b
        self.xpos = xpos

    # def __str__(self):
    #     return "(" + str(self.a) + ", " + str(self.b) + ")"

    # def __repr__(self):
    #     return "(" + str(self.a) + ", " + str(self.b) + ")"

    def __len__(self):
        return self.size()

    # def __eq__(self, rhs):
    #     return isinstance(rhs, Region) and self.a == rhs.a and self.b == rhs.b

    # def __lt__(self, rhs):
    #     lhs_begin = self.begin()
    #     rhs_begin = rhs.begin()

    #     if lhs_begin == rhs_begin:
    #         return self.end() < rhs.end()
    #     else:
    #         return lhs_begin < rhs_begin

    def empty(self):
        return self.a == self.b

    def begin(self):
        if self.a < self.b:
            return self.a
        else:
            return self.b

    def end(self):
        if self.a < self.b:
            return self.b
        else:
            return self.a

    def size(self):
        return abs(self.a - self.b)

    def contains(self, x):
        if isinstance(x, Region):
            return self.contains(x.a) and self.contains(x.b)
        else:
            return x >= self.begin() and x <= self.end()

    # def cover(self, rhs):
    #     a = min(self.begin(), rhs.begin())
    #     b = max(self.end(), rhs.end())
    #     if self.a < self.b:
    #         return Region(a, b)
    #     else:
    #         return Region(b, a)

    # def intersection(self, rhs):
    #     if self.end() <= rhs.begin():
    #         return Region(0)
    #     if self.begin() >= rhs.end():
    #         return Region(0)
    #     return Region(max(self.begin(), rhs.begin()), min(self.end(), rhs.end()))

    # def intersects(self, rhs):
    #     lb = self.begin()
    #     le = self.end()
    #     rb = rhs.begin()
    #     re = rhs.end()

    #     return (
    #         (lb == rb and le == re) or
    #         (rb > lb and rb < le) or (re > lb and re < le) or
    #         (lb > rb and lb < re) or (le > rb and le < re))


################# Selection ###################################################

class Selection():
    def __init__(self, view_id):
        self.view_id = view_id
        self.regions = []

    def __len__(self):
        return len(self.regions)
        #return sublime_api.view_selection_size(self.view_id)

    def __getitem__(self, index):
        if len(self.regions) > 0:
            return self.regions[index]
        else:
            raise IndexError()
        return None
        #r = sublime_api.view_selection_get(self.view_id, index)
        #if r.a == -1:
        #    raise IndexError()
        #return r

    # def __delitem__(self, index):
    #     if len(self.regions) > 0 and len(self.regions) < index:
    #         self.regions.remove(index)
    #     #sublime_api.view_selection_erase(self.view_id, index)

    #def __eq__(self, rhs):
    #    return rhs is not None and list(self) == list(rhs)

    #def __lt__(self, rhs):
    #    return rhs is not None and list(self) < list(rhs)

    #def __bool__(self):
    #    return self.view_id != 0

    # def is_valid(self):
    #     return self.view_id != 0
    #     # return sublime_api.view_buffer_id(self.view_id) != 0

    def clear(self):
        self.regions.clear()
        # sublime_api.view_selection_clear(self.view_id)

    def add(self, x):
        if isinstance(x, Region):
            self.regions.append(Region(x.a, x.b, x.xpos))
        else:
            self.regions.append(Region(x, x, x))
        # if isinstance(x, Region):
        #     sublime_api.view_selection_add_region(self.view_id, x.a, x.b, x.xpos)
        # else:
        #     sublime_api.view_selection_add_point(self.view_id, x)

    # def add_all(self, regions):
    #     pass
    #     # for r in regions:
    #     #     self.add(r)

    # def subtract(self, region):
    #     pass
    #     # sublime_api.view_selection_subtract_region(self.view_id, region.a, region.b)

    def contains(self, region):
        for r in self.regions:
            if r.contains(region):
                return True
        return False
        # return sublime_api.view_selection_contains(self.view_id, region.a, region.b)


################# Settings ###################################################

class Settings():
    def __init__(self, view_id):
        self.settings_id = view_id
        self.settings_storage = {}

    def get(self, key, default=None):
        return self.settings_storage.get(key, default)
        #if default is not None:
        #    return sublime_api.settings_get_default(self.settings_id, key, default)
        #else:
        #    return sublime_api.settings_get(self.settings_id, key)

    def has(self, key):
        return key in self.settings_storage
        # return sublime_api.settings_has(self.settings_id, key)

    def set(self, key, value):
        self.settings_storage[key] = value
        # sublime_api.settings_set(self.settings_id, key, value)
