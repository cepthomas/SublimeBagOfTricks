import subprocess
import sublime
import sublime_plugin
from sbot_common import *


# print('Python: load sbot_misc')

# Misc commands that don't currently warrant their own module.


#-----------------------------------------------------------------------------------
class SbotSplitViewCommand(sublime_plugin.WindowCommand):
    ''' Toggles between split file views.'''

    def run(self):
        try:
            window = self.window

            if len(window.layout()['rows']) > 2:
                # Remove split.
                window.run_command("focus_group", { "group": 1 } )
                window.run_command("close_file")
                window.run_command("set_layout", { "cols": [0.0, 1.0], "rows": [0.0, 1.0], "cells": [[0, 0, 1, 1]] } )
            else:
                # Add split.
                sel_row, _ = window.active_view().rowcol(window.active_view().sel()[0].a) # current sel
                window.run_command("set_layout", { "cols": [0.0, 1.0], "rows": [0.0, 0.5, 1.0], "cells": [[0, 0, 1, 1], [0, 1, 1, 2]] } )
                window.run_command("focus_group", { "group": 0 } )
                window.run_command("clone_file")
                window.run_command("move_to_group", { "group": 1 } )
                window.active_view().run_command("goto_line", {"line": sel_row})
        except Exception as e:
            plugin_exception(e)


#-----------------------------------------------------------------------------------
class SbotCmdLineCommand(sublime_plugin.WindowCommand):
    ''' Run a simple command in the project dir. '''

    def run(self):
        try:
            # Bottom input area.
            self.window.show_input_panel(self.window.extract_variables()['folder'] + '>', "", self.on_done, None, None)
        except Exception as e:
            plugin_exception(e)

    def on_done(self, text):
        try:
            cp = subprocess.run(text, cwd=self.window.extract_variables()['folder'], universal_newlines=True, capture_output=True, shell=True)
            sout = cp.stdout
            create_new_view(self.window, sout)
        except Exception as e:
            plugin_exception(e)


#-----------------------------------------------------------------------------------
class SbotShowEolCommand(sublime_plugin.TextCommand):
    ''' Show line ends. '''

    def run(self, edit):
        try:
            if not self.view.get_regions("eols"):
                eols = []
                ind = 0
                while 1:
                    freg = self.view.find('[\n\r]', ind) # TODO this doesn't work as ST normalizes endings. See what hexviewer does?
                    if freg is not None and not freg.empty(): # second condition is not documented!!
                        eols.append(freg)
                        ind = freg.end() + 1
                    else:
                        break
                if eols:
                    settings = sublime.load_settings(SETTINGS_FN)
                    self.view.add_regions("eols", eols, settings.get('eol_scope'))
            else:
                self.view.erase_regions("eols")
        except Exception as e:
            plugin_exception(e)
    

#-----------------------------------------------------------------------------------
class SbotTestPhantomsCommand(sublime_plugin.TextCommand):
    # def __init__(self, view):
    #     self.phantom_set = sublime.PhantomSet(self.view, "my_key")

    def __init__(self, view):
        print("Construct SbotTestPhantomsCommand")
        super(SbotTestPhantomsCommand, self).__init__(view)
        self.view = view
        self.phantom_set = sublime.PhantomSet(self.view, "my_key")
        self.count = 0

    def run(self, edit):
        image = f"C:\\Users\\cepth\\AppData\\Roaming\\Sublime Text\\Packages\\SublimeBagOfTricks\\test\\files\\mark64.bmp"
        img_html = '<img src="file://' + image + '" width="16" height="16">'

        # Old way works:
        # self.view.erase_phantoms("test")
        # self.view.erase_phantoms ("test")
        # for sel in self.view.sel():
        #     self.view.add_phantom ("test", sel, img_html, sublime.LAYOUT_BLOCK)

        # Clean first. Note - phantoms need to be managed externally rather than instantiate each time cmd is loaded.
        phantoms = []
        self.phantom_set.update(phantoms)

        html = f'<div>|image LAYOUT_INLINE at 200:210|{img_html}|</div>'
        region = sublime.Region(200, 210)
        phantom = sublime.Phantom(region, html, sublime.LAYOUT_INLINE)
        phantoms.append(phantom)

        html = f'<div>|image LAYOUT_BELOW at 400:410|{img_html}|</div>'
        region = sublime.Region(400, 410)
        phantom = sublime.Phantom(region, html, sublime.LAYOUT_BELOW)
        phantoms.append(phantom)

        html = f'<div>|image LAYOUT_BLOCK at 600:610|{img_html}|</div>'
        region = sublime.Region(600, 610)
        phantom = sublime.Phantom(region, html, sublime.LAYOUT_BLOCK)
        phantoms.append(phantom)

        href = "https://www.sublimetext.com/docs/api_reference.html"
        href = "abcdef12345"

        html = f'<div><a href="{href}">|href LAYOUT_BLOCK at 800:810|</a></div>'
        region = sublime.Region(800, 810)
        phantom = sublime.Phantom(region, html, sublime.LAYOUT_BLOCK, self.nav)
        phantoms.append(phantom)

        self.phantom_set.update(phantoms)

        # sublime.LAYOUT_INLINE: Display in between the region and the point following.
        # sublime.LAYOUT_BELOW: Display in space below the current line, left-aligned with the region.
        # sublime.LAYOUT_BLOCK: Display in space below the current line, left-aligned with the beginning of the line.

    def nav(self, href):
        # on_navigate is an optional callback that should accept a single string parameter, 
        # that is the href attribute of the link clicked.
        print(f"href:{href}")

