import sys
import datetime
import sublime_plugin
from sbot_common import *

# print('Load sbot')

# The core and system stuff.
# TODO Make into package and/or multiple plugins. https://packagecontrol.io/docs/submitting_a_package


#-----------------------------------------------------------------------------------
def plugin_loaded():
    '''
    Initialize module global stuff. This fires only once for all instances of sublime.
    There is one global context and all plugins share the same process.
    '''
    trace(TraceCat.INFO, f'===================== Starting {datetime.datetime.now()} =======================')
    trace(TraceCat.INFO, 'Using python', sys.version)


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    trace(TraceCat.INFO, "plugin_unloaded()")


#-----------------------------------------------------------------------------------
class SbotEvent(sublime_plugin.EventListener):
    ''' Listener for window specific events of interest. '''

    def on_selection_modified(self, view):
        ''' Show the abs position in the status bar. '''
        pos = view.sel()[0].begin()
        view.set_status("position", f'Pos {pos}')

    def on_load_project(window):
        trace(TraceCat.INFO, "on_load_project()")

