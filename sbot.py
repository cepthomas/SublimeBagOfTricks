import os
import sys
import json
import logging
import time
import traceback
import threading
import sublime
import sublime_plugin
import sbot_common
import sbot_project
import sbot_misc_commands
import sbot_render
import sbot_highlight
import sbot_sidebar
import sbot_signet
import sbot_extra


# All the core and system stuff.


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. '''

    print('Hello! I am python', sys.version)
    sbot_common.initialize()

    # Init logging. TODO Add filemode=a|w, level, filename, 
    if sbot_common.settings.get('enable_log', False):
        logfn = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', 'temp', 'sbot_log.txt')
        print('Logfile:', logfn)
        logformat = "%(asctime)s %(levelname)8s <%(name)s> %(message)s"
        logging.basicConfig(filename=logfn, filemode='w', format=logformat, level=logging.INFO)
        logging.info("=============================== log start ===============================");


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    logging.info("plugin_unloaded()")

    # just in case...
    sbot_project.save_all()


#-----------------------------------------------------------------------------------
class ViewEvent(sublime_plugin.ViewEventListener):
    ''' Listener for events of interest. '''

    def on_activated(self):
        ''' When focus/tab received. '''

        # sbot_common.dump_view('ViewEventListener.on_activated', self.view)
        sbot_project.load_project_maybe(self.view)

    def on_deactivated(self):
        ''' When focus/tab lost. Save to file. Crude, but on_close is not reliable so we take the conservative approach. TODO-ST4 has on_pre_save_project()) '''

        # sbot_common.dump_view('EventListener.on_deactivated', self.view)
        sproj = sbot_project.get_project(self.view)
        if sproj is not None:
            # Save the project file internal to persisted.
            sproj.save()

    def on_selection_modified(self):
        ''' Show the abs position in the status bar for debugging. '''
        
        pos = self.view.sel()[0].begin()
        self.view.set_status("position", 'Pos {}'.format(pos))


#-----------------------------------------------------------------------------------
if __name__ == '__main__':
    print("Hello from __main__")
