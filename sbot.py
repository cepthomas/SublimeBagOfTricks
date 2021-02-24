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
import sbot_misc
import sbot_render
import sbot_highlight
import sbot_sidebar
import sbot_signet
import sbot_extra

# All the core and system stuff.


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. '''

    sbot_common.initialize()
    sbot_common.settings = sublime.load_settings('SublimeBagOfTricks.sublime-settings')
    # print(sys.path)
    print(sys.version)

    # Init logging. TODO2 Add mode=a|w, level, filename, 
    if sbot_common.settings.get('enable_log', False):
        logfn = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', '_log.txt')
        print('Logfile:', logfn)
        logformat = "%(asctime)s %(levelname)8s <%(name)s> %(message)s"
        logging.basicConfig(filename=logfn, filemode='w', format=logformat, level=logging.INFO) # filemode a/w
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

        # dump_view('ViewEventListener.on_activated', self.view)
        sbot_project.load_project_maybe(self.view)

    def on_deactivated(self):
        ''' When focus/tab lost. Save to file. Crude, but on_close is not reliable so we take the conservative approach. (ST4 has on_pre_save_project()) '''

        # dump_view('EventListener.on_deactivated', self.view)
        sproj = sbot_project.get_project(self.view)
        if sproj is not None:
            # Save the project file internal to persisted.
            sproj.save()

    def on_selection_modified(self):
        ''' Show the abs position in the status bar for debugging. '''
        
        pos = self.view.sel()[0].begin()
        self.view.set_status("position", 'Pos {}'.format(pos))


#-----------------------------------------------------------------------------------
class SbotTestCommand(sublime_plugin.TextCommand):
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


        # if action == 'white_space':
        #     pname, pval1, pval2 = "draw_white_space", "all", "selection"
        # elif action == 'gutter':
        #     pname, pval1, pval2 = "gutter", False, True
        # elif action == 'line_no':
        #     pname, pval1, pval2 = "line_numbers", False, True
        # elif action == 'indent_guide':
        #     pname, pval1, pval2 = "draw_indent_guides", False, True
        # if pname:
        #     propertyValue = pval1 if v.settings().get(pname, pval1) != pval1 else pval2
        #     v.settings().set(pname, propertyValue)


        # class SbotShowEolCommand(sublime_plugin.TextCommand): #TODO1 useful?
        if not v.get_regions("eols"):
            eols = []
            ind = 0
            while 1:
                freg = v.find('[\n\r]', ind)
                if freg is not None and not freg.empty(): # second condition is not documented!!
                    eols.append(freg)
                    ind = freg.end() + 1
                else:
                    break
            if eols:
                # "highlight_scopes": [ "string", "constant.language", "comment", "markup.list", "variable", "invalid" ],
                v.add_regions("eols", eols, "invalid")
        else:
            v.erase_regions("eols")


#-----------------------------------------------------------------------------------
if __name__ == '__main__':
    print("Hello from __main__")
