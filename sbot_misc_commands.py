import os
import sys
import time
import webbrowser
import sublime
import sublime_plugin
import sbot_common


# print('^^^^^ Load sbot_misc_commands')

# Misc commands.

# The settings.
_settings = {}


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. '''
    sbot_common.trace('plugin_loaded sbot_misc_commands')
    global _settings
    _settings = sublime.load_settings(sbot_common.SETTINGS_FN)


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    ''' Clean up module global stuff. '''
    sbot_common.trace('plugin_unloaded sbot_misc_commands')


#-----------------------------------------------------------------------------------
class SbotSplitViewCommand(sublime_plugin.WindowCommand):
    ''' Toggles between split file views.'''

    def run(self):
        w = self.window

        if(len(w.layout()['rows']) > 2):
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
class SbotOpenUrlCommand(sublime_plugin.WindowCommand):
    ''' Open a web page. '''

    def run(self, url):
        webbrowser.open_new_tab(url)


#-----------------------------------------------------------------------------------
class SbotShowEolCommand(sublime_plugin.TextCommand):
    ''' Show line ends. '''

    def run(self, edit, all=False):
        v = self.view
        w = v.window()

        if not v.get_regions("eols"):
            eols = []
            ind = 0
            while 1:
                freg = v.find('[\n\r]', ind)
                if freg is not None and not freg.empty(): # second condition is not documented!!
                    eols.append(freg)
                    ind = freg.end() + 1
                else:
                    break
            if eols:
                v.add_regions("eols", eols, _settings.get('eol_scope', "comment"))
        else:
            v.erase_regions("eols")


#-----------------------------------------------------------------------------------
class SbotInsertLineIndexesCommand(sublime_plugin.TextCommand):
    ''' Insert sequential numbers in first column. Default is to start at 1. '''

    def run(self, edit, all=False):
        v = self.view

        # Iterate lines.
        line_count = v.rowcol(v.size())[0]
        width = len(str(line_count))
        offset = 0

        for region in sbot_common.get_sel_regions(v):
            line_num = 1
            offset = 0
            for line_region in v.split_by_newlines(region):
                s = "{:0{size}} ".format(line_num, size=width)
                v.insert(edit, line_region.a + offset, s)
                line_num += 1
                # Adjust for inserts.
                offset += width+1


#-----------------------------------------------------------------------------------
class SbotShowEolCommand(sublime_plugin.TextCommand):
    ''' Show line ends. '''

    def run(self, edit, all=False):
        v = self.view
        w = v.window()

        if not v.get_regions("eols"):
            eols = []
            ind = 0
            while 1:
                freg = v.find('[\n\r]', ind)
                if freg is not None and not freg.empty(): # second condition is not documented!!
                    eols.append(freg)
                    ind = freg.end() + 1
                else:
                    break
            if eols:
                # "highlight_scopes": [ "string", "constant.language", "comment", "markup.list", "variable", "invalid" ],
                v.add_regions("eols", eols, _settings.get('eol_scope', "comment"))
        else:
            v.erase_regions("eols")
