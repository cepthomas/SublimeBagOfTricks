import os
import sys
import json
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


# sbot_projects = {} # k:window_id v:{fn, highlights, signets,... }

# self.signets = {} # k:filename v:[rows]
# self.highlights = {} # k:filename v:[tokens] where: tokens={"token": "abc", "whole_word": true, "scope": "comment"}

# _signets = {} # k:filename v:[rows]
# _highlights = {}



#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. This fires only once for all instances of sublime. '''

    sbot_common.trace('Hello! I am python', sys.version)

    sbot_common.initialize()

    sbot_common.trace('^^^ plugin_loaded', sublime.active_window().id())


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    sbot_common.trace("plugin_unloaded()")

    # just in case...
    sbot_project.save_all()




#-----------------------------------------------------------------------------------
class Event(sublime_plugin.EventListener):
    ''' Listener for events of interest. '''

    def on_pre_close(self, view):
        ''' Called when a view is about to be closed. The view will still be in the window at this point. '''
        sbot_common.trace('^^^ on_pre_close', view.file_name(), view.id(), view.window().id())
        # if view.file_name() is not None:


    def on_new(self, view):
        ''' Called when a new file is created.'''
        sbot_common.trace('^^^ on_new', view.file_name(), view.id(), view.window().id())


    def on_load(self, view):
        '''  Called when the file is finished loading.'''
        sbot_common.trace('^^^ on_load', view.file_name(), view.id(), view.window().id())


    def on_activated(self, view):
        ''' When focus/tab received. '''
        sbot_common.trace('^^^ on_activated',view.file_name(), view.id(),view.window().id())
        sbot_common.trace('$$$ on_activated', view.file_name(), view.id(), view.window().id())
        # sbot_common.dump_view('ViewEventListener.on_activated',view)
        sbot_project.load_project_maybe(view)
        # # Open the st project.
        # self.fn = project_fn.replace('.sublime-project', SBOT_PROJECT_EXT)
        # # Need to track this because ST window/view lifecycle is unreliable.
        # self.views_inited = set()


    def on_deactivated(self, view):
        ''' When focus/tab lost. Save to file. Crude, but on_close is not reliable so we take the conservative approach. TODO-ST4 has on_pre_save_project()) '''
        sbot_common.trace('^^^ on_deactivated',view.id(),view.window().id())
        # sbot_common.dump_view('EventListener.on_deactivated',view)
        sproj = sbot_project.get_project(view)
        if sproj is not None:
            # Save the project file internal to persisted.
            sproj.save()


    def on_selection_modified(self, view):
        ''' Show the abs position in the status bar for debugging. '''
        
        pos = view.sel()[0].begin()
        view.set_status("position", 'Pos {}'.format(pos))


# #-----------------------------------------------------------------------------------
# class ViewEvent(sublime_plugin.ViewEventListener):
#     ''' Listener for events of interest. '''

#     def on_activated(self):
#         ''' When focus/tab received. '''

#         sbot_common.trace('^^^ on_activated', self.view.file_name() , self.view.id(), self.view.window().id())


#         # sbot_common.dump_view('ViewEventListener.on_activated', self.view)
#         sbot_project.load_project_maybe(self.view)

#     def on_deactivated(self):
#         ''' When focus/tab lost. Save to file. Crude, but on_close is not reliable so we take the conservative approach. TODO-ST4 has on_pre_save_project()) '''
#         sbot_common.trace('^^^ on_deactivated', self.view.id(), self.view.window().id())

#         # sbot_common.dump_view('EventListener.on_deactivated', self.view)
#         sproj = sbot_project.get_project(self.view)
#         if sproj is not None:
#             # Save the project file internal to persisted.
#             sproj.save()

#     def on_selection_modified(self):
#         ''' Show the abs position in the status bar for debugging. '''
        
#         pos = self.view.sel()[0].begin()
#         self.view.set_status("position", 'Pos {}'.format(pos))


#-----------------------------------------------------------------------------------
if __name__ == '__main__':
    sbot_common.trace("Hello from __main__")
