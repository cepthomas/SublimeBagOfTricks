import sys
import datetime
import io
import webbrowser
import sublime
import sublime_plugin
from sbot_common import *

print('Python load sbot')


# The core and system stuff.


#-----------------------------------------------------------------------------------
def plugin_loaded():
    '''
    Initialize module global stuff. This fires only once for all instances of sublime.
    There is one global context and all plugins share the same process.
    '''

    # Hook the default outputs.
    settings = sublime.load_settings(SETTINGS_FN)
    stdio_hook = settings.get('stdio_hook')
    if stdio_hook:
        print('This should appear in ST console only.')
        sys.stdout = StdHook(sys.stdout)
        sys.stderr = StdHook(sys.stderr)
        print('This should appear in trace log and ST console.')

    # Normal startup stuff.
    trace(TraceCat.INFO, f'===================== Starting {datetime.datetime.now()} =======================')
    trace(TraceCat.INFO, 'Using python', sys.version)


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    trace(TraceCat.INFO, "plugin_unloaded()")


#-----------------------------------------------------------------------------------
class SbotAboutCommand(sublime_plugin.WindowCommand):
    ''' Open a web page. Mainly for internal use. '''

    def run(self, url):
        webbrowser.open_new_tab("https://github.com/cepthomas/SublimeBagOfTricks/blob/master/README.md")


#-----------------------------------------------------------------------------------
class StdHook(io.TextIOBase):
    '''
    Experimental hook to capture ST's monopolization of the console.
    Also tried sys.excepthook but it seems ST captures unhandled exceptions.
    '''

    def __init__(self, std):
        self.buf = None
        self.std = std

    def flush(self):
        b = self.buf
        self.buf = None
        if b is not None and len(b):
            # TODO sniff/process things like exceptions
            trace(TraceCat.STDO, b.rstrip())
            # Echo to console.
            self.std.write(b)

    def write(self, s):
        if self.buf is None:
            self.buf = s
        else:
            self.buf += s
        if '\n' in s or '\r' in s:
            self.flush()


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
