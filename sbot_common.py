import os
import sys
import time
import datetime
import traceback
import enum
import sublime
import sublime_plugin

print('Python load sbot_common')


# Definitions.
SETTINGS_FN = 'SublimeBagOfTricks.sublime-settings'
HIGHLIGHT_REGION_NAME = 'highlight_%s'


#-----------------------------------------------------------------------------------
# Debug/trace stuff.
class TraceCat(enum.Flag):
    ERROR = enum.auto()
    LOOK  = enum.auto() # stand out in file
    INFO  = enum.auto()
    ACTV  = enum.auto() # on_activated, on_deactivated
    LOAD  = enum.auto() # on_load, on_close
    STIO  = enum.auto() # stdio/stderr

_trace_cat = TraceCat.ERROR | TraceCat.LOOK | TraceCat.INFO | TraceCat.LOAD | TraceCat.STIO
_trace_fn = None


#-----------------------------------------------------------------------------------
def trace(cat, *args):
    ''' Trace debugging. '''
    if cat & _trace_cat:
        global _trace_fn
        if _trace_fn is None:
            _trace_fn = os.path.join(get_temp_path(), 'trace.txt')

        now = datetime.datetime.now().time()

        scat = str(cat).replace('TraceCat.', '')
        if cat == TraceCat.ERROR:
            scat = '!!!!!!!!!!!!!!!!!!!! ERROR'
        elif cat == TraceCat.LOOK:
            scat = '>>>>>>>>>>>>>>>>>>>>'

        content = ' | '.join(map(str, args))
        s = f'{now} {scat} {content}'

        with open(_trace_fn, "a+") as f:
            f.write(s + '\n')

        # Check for file size limit.
        if os.path.getsize(_trace_fn) > 100000:
            os.replace(_trace_fn, _trace_fn.replace('trace.txt', 'trace_old.txt'))
            os.remove(_trace_fn)


#-----------------------------------------------------------------------------------
def unhandled_exception(info, exc):
    ''' Trace debugging. '''
    st = traceback.format_exc()
    trace(TraceCat.ERROR, info, exc.args)
    trace(TraceCat.ERROR, st)
    sublime.error_message(info + '\n' + st)


#-----------------------------------------------------------------------------------
def get_sel_regions(view):
    ''' Generic function to get selections or optionally the whole view.'''
    regions = []
    if len(view.sel()[0]) > 0: # user sel
        regions = view.sel()
    else:
        settings = sublime.load_settings(SETTINGS_FN)
        if settings.get('sel_all'):
            regions = [sublime.Region(0, view.size())]
    return regions


#-----------------------------------------------------------------------------------
def create_new_view(window, text):
    ''' Creates a temp view with text. Returns the view.'''
    vnew = window.new_file()
    vnew.set_scratch(True)
    vnew.run_command('append', {'characters': text }) # insert has some odd behavior - indentation
    return vnew


#-----------------------------------------------------------------------------------
def wait_load_file(view, line):
    ''' Open file asynchronously then position at line. '''
    if view.is_loading():
        sublime.set_timeout(lambda: wait_load_file(view, line), 100) # maybe not forever?
    else: # good to go
        view.run_command("goto_line", {"line": line})


#-----------------------------------------------------------------------------------
def get_persistence_path(stp_fn, ext):
    ''' General file name maker. Uses settings.persistence_path to determine path. '''
    ppath = None
    settings = sublime.load_settings(SETTINGS_FN)

    if stp_fn is not None:
        spp = settings.get('persistence_path')
        stp_fn = stp_fn.replace('.sublime-project', ext)
        if spp == 'local':
            ppath = stp_fn
        elif spp == 'store':
            stp_fn = os.path.basename(stp_fn)
            ppath = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', 'store', stp_fn)

    return ppath


#-----------------------------------------------------------------------------------
def get_temp_path():
    ''' General file name maker. '''
    tfn = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', 'temp')
    return tfn