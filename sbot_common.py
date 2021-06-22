import os
import sys
import time
import datetime
import traceback
import enum
import sublime
import sublime_plugin

# print('Load sbot_common')


# Definitions.
SETTINGS_FN = 'SublimeBagOfTricks.sublime-settings'

# Debug.
class TraceCat(enum.Flag):
    ERROR_ERROR_ERROR = enum.auto()
    INFO = enum.auto()
    ACTV = enum.auto() # on_activated, on_deactivated
    LOAD = enum.auto() # on_load, on_close

_trace_cat = TraceCat.ERROR_ERROR_ERROR | TraceCat.INFO | TraceCat.LOAD
_trace_fn = None


#-----------------------------------------------------------------------------------
def trace(cat, *args):
    ''' Trace debugging. '''
    if cat & _trace_cat:
        global _trace_fn
        if _trace_fn is None:
            _trace_fn = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', 'temp', 'trace.txt')

        now = datetime.datetime.now().time()
        scat = str(cat).replace('TraceCat.', '')
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
    st = traceback.format_exc()#limit=None, chain=True)
    trace(TraceCat.ERROR_ERROR_ERROR, info, exc.args)
    trace(TraceCat.ERROR_ERROR_ERROR, st)
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
def write_to_console(text):
    ''' This is crude but works. Sublime also adds an extra eol when writing to the console. '''
    for b in text:
        if b == r'\n':
            sys.stdout.write('\n')
        elif b == r'\r':
            pass
        else:
            sys.stdout.write(chr(b))


#-----------------------------------------------------------------------------------
def dump_view(preamble, view):
    ''' Helper util. '''
    s = []
    s.append('view')
    s.append(preamble)

    s.append('view_id:')
    s.append('None' if view is None else str(view.id()))

    if view is not None:
        window = view.window()
        fn = view.file_name()

        s.append('file_name:')
        s.append('None' if fn is None else os.path.split(fn)[1])

        s.append('project_file_name:')
        s.append('None' if window is None or window.project_file_name() is None else os.path.split(window.project_file_name())[1])

    trace(TraceCat.INFO, " ".join(s))


#-----------------------------------------------------------------------------------
def wait_load_file(view, line):
    ''' Open file asynchronously then position at line. '''
    if view.is_loading():
        sublime.set_timeout(lambda: wait_load_file(view, line), 100) # maybe not forever?
    else: # good to go
        view.run_command("goto_line", {"line": line})


#-----------------------------------------------------------------------------------
def trim_all(s):
    ''' Remove lead/trail ws and empty lines.'''
    # lead/trail ws
    reo = re.compile('^[ \t]+|[\t ]+$', re.MULTILINE)
    s = reo.sub('', s)

    # empty lines
    reo = re.compile('^[ \t]*$\r?\n', re.MULTILINE)
    s = reo.sub('', s)

    return s


#-----------------------------------------------------------------------------------
def get_persistence_path(stp_fn, ext):
    ''' General file name maker. '''
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
