import os
import sys
import json
import logging
import time
import traceback
import threading
import sublime
import sublime_plugin
import SbotCommon
import SbotProject
import SbotMisc
import SbotRender
import SbotHighlight
import SbotSidebar
import SbotSignet
import SbotExtra

# All the core and system stuff.

# TODOC Combined prefs editor.


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. '''
    SbotCommon.initialize()
    SbotCommon.settings = sublime.load_settings('SublimeBagOfTricks.sublime-settings')
    # print(sys.path)

    # Init logging.
    if SbotCommon.settings.get('enable_log', False):
        logfn = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', 'sbot_log.txt')
        print('Logfile:', logfn)
        logformat = "%(asctime)s %(levelname)8s <%(name)s> %(message)s"
        logging.basicConfig(filename=logfn, filemode='w', format=logformat, level=logging.INFO) # filemode a/w
        logging.info("=============================== log start ===============================");


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    logging.info("plugin_unloaded()")
    # TODOC just in case...
    # for id in list(sbot_projects):
    #     sbot_projects[id].save()


#-----------------------------------------------------------------------------------
class ViewEvent(sublime_plugin.ViewEventListener):
    ''' Listener for events of interest. '''

    def on_activated(self):
        ''' When focus/tab received. '''
        # dump_view('ViewEventListener.on_activated', self.view)
        SbotProject.load_project_maybe(self.view)

    def on_deactivated(self):
        ''' When focus/tab lost. Save to file. Also crude, but on_close is not reliable so we take the conservative approach. (ST4 has on_pre_save_project()) '''
        # dump_view('EventListener.on_deactivated', self.view)
        sproj = SbotProject.get_project(self.view)
        if sproj is not None:
            # Save the project file internal to persisted.
            sproj.save()

    def on_selection_modified(self):
        ''' Show the abs position in the status bar for debugging. '''
        pos = self.view.sel()[0].begin()
        self.view.set_status("position", 'Pos {}'.format(pos))


#-----------------------------------------------------------------------------------
class SbotTestTestTestCommand(sublime_plugin.TextCommand):
    ''' Just for hack testing. '''

    def run(self, edit, all=False):
        v = self.view
        w = self.view.window()
        
        # for sheet in w.sheets():
        #     print('sheet:', sheet)
        # for view in w.views(): # These are in order L -> R.
        #     print('active view:', w.get_view_index(view), view.file_name()) # (group, index)
        # get_project(v).dump() # These are not ordered like file.

        # # Phantom phun
        # image = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', 'test', 'mark1.bmp')
        # print(image)
        # html = '<body><p>Hello!</p><img src="file://' + image + '" width="90" height="145"></body>'
        # self.phantset = sublime.PhantomSet(v, "test")
        # phant = sublime.Phantom(v.sel()[0], html, sublime.LAYOUT_BLOCK)
        # phants = []
        # phants.append(phant)
        # self.phantset.update(phants)

        # global global_thing
        # print(global_thing)
        # global_thing['item' + str(len(global_thing) + 5)] = 1234
        # v.show_popup(str(global_thing))


#-----------------------------------------------------------------------------------
if __name__ == '__main__':
    print("Hello from __main__")

    # try:
    #     unittest.main()
    # except SystemExit as e:
    #     # print("ok")
    #     pass
    # except:
    #     print("Something else went wrong")    
