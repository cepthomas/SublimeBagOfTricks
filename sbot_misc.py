import os
import sys
import time
import sublime
import sublime_plugin


# Misc commands and utilities.


#-----------------------------------------------------------------------------------
class SbotSplitViewCommand(sublime_plugin.WindowCommand):
    ''' Toggles between split file views.'''

    def run(self):
        w = self.window
        lo = w.layout()

        if(len(lo['rows']) > 2):
            # Remove split.
            w.run_command("focus_group", { "group": 1 } )
            w.run_command("close_file")
            w.run_command("set_layout", { "cols": [0.0, 1.0], "rows": [0.0, 1.0], "cells": [[0, 0, 1, 1]] } )
        else:
            # Add split.
            sel_row, _ = w.active_view().rowcol(w.active_view().sel()[0].a) # current sel
            w.run_command("set_layout", { "cols": [0.0, 1.0], "rows": [0.0, 0.5, 1.0], "cells": [[0, 0, 1, 1], [0, 1, 1, 2]] } )
            w.run_command("focus_group", { "group": 0 } )
            w.run_command("clone_file")
            w.run_command("move_to_group", { "group": 1 } )
            w.active_view().run_command("goto_line", {"line": sel_row})


#-----------------------------------------------------------------------------------
class SbotOpenSiteCommand(sublime_plugin.ApplicationCommand):
    ''' Open a web page. '''

    def run(self, url):
        webbrowser.open_new_tab(url)


#-----------------------------------------------------------------------------------
class SbotToggleDisplayCommand(sublime_plugin.TextCommand): #TODOC useful?
    ''' Toggles between two values. '''

    def run(self, edit, **kwargs):
        action = kwargs['action']
        v = self.view

        if action == 'white_space':
            pname, pval1, pval2 = "draw_white_space", "all", "selection"
        elif action == 'gutter':
            pname, pval1, pval2 = "gutter", False, True
        elif action == 'line_no':
            pname, pval1, pval2 = "line_numbers", False, True
        elif action == 'indent_guide':
            pname, pval1, pval2 = "draw_indent_guides", False, True
        elif action == 'eol':
            if not v.get_regions("eols"):
                eols = []
                p = 0
                while 1:
                    s = v.find('\n', p + 1)
                    if not s:
                        break
                    eols.append(s)
                    p = s.a

                if eols:
                    v.add_regions("eols", eols, "comment")
            else:
                v.erase_regions("eols")
        else:
            propertyValue = None

        if pname:
            propertyValue = pval1 if v.settings().get(pname, pval1) != pval1 else pval2
            v.settings().set(pname, propertyValue)


#-----------------------------------------------------------------------------------
def dump_view(preamble, view):
    ''' Helper util. '''

    s = []
    s.append('view')
    s.append(preamble)

    s.append('view_id:')
    s.append('None' if view is None else str(view.id()))

    if view is not None:
        w = view.window()
        fn = view.file_name()

        s.append('file_name:')
        s.append('None' if fn is None else os.path.split(fn)[1])

        s.append('project_file_name:')
        s.append('None' if w is None or w.project_file_name() is None else os.path.split(w.project_file_name())[1])

    logging.info(" ".join(s));
            

#-----------------------------------------------------------------------------------
def wait_load_file(view, line):
    ''' Open file asynchronously then position at line. '''
    
    if view.is_loading():
        sublime.set_timeout(lambda: wait_load_file(view, line), 100) # maybe not forever?
    else: # good to go
        view.run_command("goto_line", {"line": line})


#-----------------------------------------------------------------------------------
class SbotPerfCounter(object):
    ''' Container for perf counter. All times in msec. '''

    def __init__(self, id):
        self.id = id
        self.vals = []
        self.start_time = 0

    def start(self):
        self.start_time = time.perf_counter() * 1000.0

    def stop(self):
        if self.start_time != 0:
            self.vals.append(time.perf_counter() * 1000.0 - self.start_time)
            self.start_time = 0

    def dump(self):
        avg = sum(self.vals) / len(self.vals)
        s = self.id + ': '
        if len(self.vals) > 0:
            s += str(avg)
            s += ' ({})'.format(len(self.vals))
        else:
            s += 'No data'
        return s

    def clear(self):
        self.vals = []
