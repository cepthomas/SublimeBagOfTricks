import os
import sys
import json
import time
import traceback
import threading
import sublime
import sublime_plugin
import sbot_common

# print('^^^^^ Load sbot')

# The core and system stuff.


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. This fires only once for all instances of sublime. '''
    sbot_common.trace('===================== Starting', sys.version)


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    sbot_common.trace("plugin_unloaded()")
    # just in case... TODO I think it's too late for this.
    # sbot_project.save_all()


#-----------------------------------------------------------------------------------
class SbotEvent(sublime_plugin.EventListener):
    ''' Listener for events of interest. '''

    def on_selection_modified(self, view):
        ''' Show the abs position in the status bar for debugging. '''
        pos = view.sel()[0].begin()
        view.set_status("position", 'Pos {}'.format(pos))


#-----------------------------------------------------------------------------------
if __name__ == '__main__':
    sbot_common.trace("Hello from __main__")
