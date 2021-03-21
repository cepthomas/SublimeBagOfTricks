

import sbot
import sbot_common

sbot.plugin_loaded()


sbot.plugin_unloaded()



#class sublime_plugin.ViewEventListener:
#    #self.view

#    def on_activated(self):
#        ''' When focus/tab received. This is the only reliable event - on_load() doesn't get called when showing previously opened files. '''

#    def on_load(self):
#        ''' Called when file loaded. Doesn't work when starting up! Maybe ST4 improved? '''

#    def on_deactivated(self):
#        ''' When focus/tab lost. Save to file. Crude, but on_close is not reliable so we take the conservative approach. '''

#    def on_close(self):
#        ''' Called when a view is closed (note, there may still be other views into the same buffer). '''


#class sublime_plugin.EventListener:
#    ''' Listener for window specific events of interest. '''

#    # def on_load(self, view):
#    # def on_activated(self, view):
#    # def on_deactivated(self, view):
#    # def on_close(self, view):

#    def on_selection_modified(self, view):
#        ''' Show the abs position in the status bar. '''
#        pos = view.sel()[0].begin()
#        view.set_status("position", 'Pos {}'.format(pos))


