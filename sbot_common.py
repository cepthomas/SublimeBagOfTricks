import os
import sys
import time
import datetime
import traceback
import enum
import pathlib
import sublime
import sublime_plugin

print('Python: load sbot_common')


# Definitions.
SETTINGS_FN = 'SublimeBagOfTricks.sublime-settings'
HIGHLIGHT_REGION_NAME = 'highlight_%s'


# Debug/trace stuff.
class TraceCat(enum.Flag):
    ERROR = enum.auto()
    INFO  = enum.auto()
    LOOK  = enum.auto() # make it stand out in file
    ACTV  = enum.auto() # on_activated, on_deactivated
    LOAD  = enum.auto() # on_load, on_close
    STDO  = enum.auto() # stdio/stderr


# Stuff to hang on to.
_temp_path = None
_store_path = None
_trace_fn = None
_trace_cat = TraceCat.ERROR | TraceCat.LOOK | TraceCat.INFO | TraceCat.STDO # | TraceCat.LOAD | TraceCat.ACTV


#-----------------------------------------------------------------------------------
def trace(cat, *args):
    ''' Trace for debugging. '''

    global _trace_fn, _temp_path, _store_path

    if _trace_fn is None:
        # First time = initialize. Make sure paths exist.
        _temp_path = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', 'temp')
        pathlib.Path(_temp_path).mkdir(parents=True, exist_ok=True)
        _store_path = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', 'store')
        pathlib.Path(_store_path).mkdir(parents=True, exist_ok=True)
        # The trace file.
        _trace_fn = os.path.join(_temp_path, 'trace.txt')

    if cat in _trace_cat:
        now = datetime.datetime.now().time()

        scat = str(cat).replace('TraceCat.', '')
        if cat == TraceCat.ERROR:
            scat = '!!!!!!!! ERROR !!!!!!!!!!!!'
        elif cat == TraceCat.LOOK:
            scat = '>>>>>>>>> LOOK >>>>>>>>>>>>'

        content = ' | '.join(map(str, args))
        s = f'{now} {scat} {content}'

        with open(_trace_fn, "a+") as f:
            f.write(s + '\n')

        # Check for file size limit.
        if os.path.getsize(_trace_fn) > 100000:
            try:
                os.replace(_trace_fn, _trace_fn.replace('trace.txt', 'trace_old.txt'))
                os.remove(_trace_fn)
            except Exception as e:
                pass


#-----------------------------------------------------------------------------------
def plugin_exception(exc):
    '''
    Handling of runtime exceptions generated in ST callbacks.
    This gives us a chance to do something before they are swallowed and dumped to the console.
    '''
    st = traceback.format_exc()
    # trace(TraceCat.ERROR, st)
    sublime.error_message(f'Runtime error\n{st}')


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
            ppath = os.path.join(_store_path, stp_fn)

    return ppath


#-----------------------------------------------------------------------------------
def get_temp_path():
    ''' Accessor. '''
    return _temp_path
