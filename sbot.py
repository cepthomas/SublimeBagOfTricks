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


# sbot_projects = {} # k:window_id v:{fn, highlights, signets,... }

# self.signets = {} # k:filename v:[rows]
# self.highlights = {} # k:filename v:[tokens] where: tokens={"token": "abc", "whole_word": true, "scope": "comment"}

# _signets = {} # k:filename v:[rows]
# _highlights = {}


# sbot-project file:
# {
#     "highlights": {
#         "file5.o": {
#             "token2": {
#                 "scope": "scope_yyy", 
#                 "whole_word": false
#             }, 
#             "token3": {
#                 "scope": "scope_zzz", 
#                 "whole_word": true
#             }, 
#             "token1": {
#                 "scope": "scope_xxx", 
#                 "whole_word": true
#             }
#         }, 
#         "file4.xml": {
#             "token2": {
#                 "scope": "scope_yyy", 
#                 "whole_word": false
#             }, 
#             "token3": {
#                 "scope": "scope_zzz", 
#                 "whole_word": true
#             }, 
#             "token1": {
#                 "scope": "scope_xxx", 
#                 "whole_word": true
#             }
#         }
#     }, 
#     "signets": {
#         "file1.c": [
#             1, 
#             2, 
#             3
#         ], 
#         "file3.json": [
#             111, 
#             112, 
#             113
#         ], 
#         "file2.h": [
#             11, 
#             12, 
#             13
#         ]
#     }
# }


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. This fires only once for all instances of sublime. '''

    print('Hello! I am python', sys.version)

    sbot_common.initialize()



    # sigs = {}
    # sigs['file1.c'] = [1, 2, 3]
    # sigs['file2.h'] = [11, 12, 13]
    # sigs['file3.json'] = [111, 112, 113]

    # hls = {}
    # hls['file4.xml'] = {}
    # x = hls['file4.xml']
    # x['token1'] = {"whole_word": True, "scope": "scope_xxx"}
    # x['token2'] = {"whole_word": False, "scope": "scope_yyy"}
    # x['token3'] = {"whole_word": True, "scope": "scope_zzz"}

    # hls['file5.o'] = {}
    # x = hls['file5.o']
    # x['token1'] = {"whole_word": True, "scope": "scope_xxx"}
    # x['token2'] = {"whole_word": False, "scope": "scope_yyy"}
    # x['token3'] = {"whole_word": True, "scope": "scope_zzz"}

    # sbot_proj = {}
    # sbot_proj['highlights'] = hls
    # sbot_proj['signets'] = sigs

    # with open(r'C:\Users\cepth\AppData\Roaming\Sublime Text 3\Packages\SublimeBagOfTricks\junk.txt', 'w') as fp:
    #     json.dump(sbot_proj, fp, indent=4)




    # Init logging. TODO Add filemode=a|w, level, filename, TODO put log in User area, along with sbot-project
    if sbot_common.settings.get('enable_log', False):
        logfn = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', 'temp', 'sbot_log.txt')
        print('Logfile:', logfn)
        logformat = "%(asctime)s %(levelname)8s <%(name)s> %(message)s"
        logging.basicConfig(filename=logfn, filemode='w', format=logformat, level=logging.INFO)
        logging.info("=============================== log start ===============================");

    print('^^^ plugin_loaded', sublime.active_window().id())


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    logging.info("plugin_unloaded()")

    # just in case...
    sbot_project.save_all()




#-----------------------------------------------------------------------------------
class Event(sublime_plugin.EventListener):
    ''' Listener for events of interest. '''

    def on_pre_close(self, view):
        ''' Called when a view is about to be closed. The view will still be in the window at this point. '''

        print('^^^ on_pre_close', view.file_name(), view.id(), view.window().id())

        # if view.file_name() is not None:


    def on_new(self, view):
        ''' Called when a new file is created.'''
        print('^^^ on_new', view.file_name(), view.id(), view.window().id())

    def on_load(self, view):
        '''  Called when the file is finished loading.'''
        print('^^^ on_load', view.file_name(), view.id(), view.window().id())


    def on_activated(self, view):
        ''' When focus/tab received. '''
        print('^^^ on_activated',view.file_name(), view.id(),view.window().id())
        # sbot_common.dump_view('ViewEventListener.on_activated',view)
        sbot_project.load_project_maybe(view)
        # # Open the st project.
        # self.fn = project_fn.replace('.sublime-project', SBOT_PROJECT_EXT)
        # # Need to track this because ST window/view lifecycle is unreliable.
        # self.views_inited = set()


    def on_deactivated(self, view):
        ''' When focus/tab lost. Save to file. Crude, but on_close is not reliable so we take the conservative approach. TODO-ST4 has on_pre_save_project()) '''
        print('^^^ on_deactivated',view.id(),view.window().id())
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

#         print('^^^ on_activated', self.view.file_name() , self.view.id(), self.view.window().id())


#         # sbot_common.dump_view('ViewEventListener.on_activated', self.view)
#         sbot_project.load_project_maybe(self.view)

#     def on_deactivated(self):
#         ''' When focus/tab lost. Save to file. Crude, but on_close is not reliable so we take the conservative approach. TODO-ST4 has on_pre_save_project()) '''
#         print('^^^ on_deactivated', self.view.id(), self.view.window().id())

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
    print("Hello from __main__")
