import os
import sys
import time
import datetime
import sublime
import sublime_plugin

# print('Load sbot_common')

# Definitions.
SETTINGS_FN = 'SublimeBagOfTricks.sublime-settings'

# Debug.
_trace_fn = None


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. '''
    trace('plugin_loaded sbot_common')


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    ''' Clean up module global stuff. '''
    trace('plugin_unloaded sbot_common')


#-----------------------------------------------------------------------------------
def trace(*args, cat=''):
    ''' Debugging. '''
    global _trace_fn
    if _trace_fn is None:
        _trace_fn = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', 'temp', 'trace.txt')

    with open(_trace_fn, "a+") as f:
        f.write(s + '\n')

    # Check for file size limit.
    if os.path.getsize(_trace_fn) > 100000:
        os.replace(_trace_fn, _trace_fn.replace('trace.txt', 'trace_old.txt'))
        os.remove(_trace_fn)


#-----------------------------------------------------------------------------------
def error(info, exc):
    ''' Debugging. '''
    trace(info, str(exc), exc.args, cat='ERROR!!!')
    trace(sys.exc_info()[0], cat='ERROR!!!')
    sublime.error_message(info + '\n' + str(exc)) # TODO better eay?


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

    trace(" ".join(s))


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


#-----------------------------------------------------------------------------------
class SbotPerfCounter():
    ''' Container for perf counter. All times in msec. '''

    def __init__(self, cid):
        self.id = cid
        self.vals = []
        self.start_time = 0.0

    def start(self):
        self.start_time = time.perf_counter() * 1000.0

    def stop(self):
        if self.start_time != 0:
            self.vals.append(time.perf_counter() * 1000.0 - self.start_time)
            self.start_time = 0.0

    def dump(self):
        avg = sum(self.vals) / len(self.vals)
        s = self.id + ': '
        if len(self.vals) > 0:
            s += str(avg)
            s += ' ({})'.format(len(self.vals))
        else:
            s += 'No data'
        return s

    def clear(self):
        self.vals = []
