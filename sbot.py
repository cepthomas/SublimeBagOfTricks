import sys
import datetime
import sublime_plugin
import sbot_common

# print('Load sbot')

# The core and system stuff.


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. This fires only once for all instances of sublime. '''
    sbot_common.trace('===================== Starting {} ======================='.format(datetime.datetime.now()))
    sbot_common.trace('Using python', sys.version)


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    sbot_common.trace("plugin_unloaded()")


#-----------------------------------------------------------------------------------
class SbotEvent(sublime_plugin.EventListener):
    ''' Listener for window specific events of interest. '''

    def on_selection_modified(self, view):
        ''' Show the abs position in the status bar. '''
        pos = view.sel()[0].begin()
        view.set_status("position", 'Pos {}'.format(pos))
