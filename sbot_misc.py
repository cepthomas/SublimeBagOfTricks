import subprocess
import webbrowser
import sublime
import sublime_plugin
import sbot_common


# print('Load sbot_misc')

# Misc stuff that doesn't warrant its own module.


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. '''
    sbot_common.trace('plugin_loaded sbot_misc')


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    ''' Clean up module global stuff. '''
    sbot_common.trace('plugin_unloaded sbot_misc')


#-----------------------------------------------------------------------------------
class SbotSplitViewCommand(sublime_plugin.WindowCommand):
    ''' Toggles between split file views.'''

    def run(self):
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


#-----------------------------------------------------------------------------------
class SbotOpenUrlCommand(sublime_plugin.WindowCommand):
    ''' Open a web page. Mainly for internal use. '''

    def run(self, url):
        webbrowser.open_new_tab(url)


#-----------------------------------------------------------------------------------
class SbotCmdLineCommand(sublime_plugin.WindowCommand):
    ''' Run a simple command in the project dir. '''

    def run(self):
        # Bottom input area.
        self.window.show_input_panel(self.window.extract_variables()['folder'] + '>', "", self.on_done, None, None)

    def on_done(self, text):
        try:
            print(self.window.extract_variables())
            sout = subprocess.check_output(text, cwd=self.window.extract_variables()['folder'], universal_newlines=True, shell=True)
        except Exception as e:
            sout = 'Error: {}'.format(e.args)
        sbot_common.create_new_view(self.window, sout)
