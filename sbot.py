import sys
import datetime
import io
import webbrowser
import sublime
import sublime_plugin
from sbot_common import *

# print('Python: load sbot')


# The core and system stuff.


#-----------------------------------------------------------------------------------
def plugin_loaded():
    trace(TraceCat.INFO, f'===================== Starting {datetime.datetime.now()} =======================')
    trace(TraceCat.INFO, 'Using python', sys.version)


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    trace(TraceCat.INFO, "plugin_unloaded()")


#-----------------------------------------------------------------------------------
class SbotAboutCommand(sublime_plugin.WindowCommand):
    ''' Open a web page. '''

    def run(self, url):
        webbrowser.open_new_tab("https://github.com/cepthomas/SublimeBagOfTricks/blob/master/README.md")


#-----------------------------------------------------------------------------------
class SbotEvent(sublime_plugin.EventListener):
    ''' Listener for window specific events of interest. '''

    def on_selection_modified(self, view):
        ''' Show the abs position in the status bar. '''
        pos = view.sel()[0].begin()
        view.set_status("position", f'Pos {pos}')

    def on_load_project(self, window):
        ''' Doesn't fire on startup (last) project load. '''
        trace(TraceCat.INFO, "on_load_project()", window.project_file_name())

    def on_exit(self):
        ''' Called once after the API has shut down, immediately before the plugin_host process exits. '''
        trace(TraceCat.INFO, "on_exit()")

    def on_pre_close_window(self, window):
        ''' Seems to work. '''
        trace(TraceCat.INFO, "on_pre_close_window()", window.project_file_name())
