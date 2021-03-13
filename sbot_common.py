import os
import time
import sublime
import sublime_plugin

print('Load sbot_common')

# Definitions.
SETTINGS_FN = 'SublimeBagOfTricks.sublime-settings'

# The settings.
_settings = None

# Debug.
_trace_fn = None


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. '''
    trace('plugin_loaded sbot_common')
    # global _settings
    # _settings = sublime.load_settings(SETTINGS_FN) #TODO2 doesn't reload on change.

    # print('^^^101', _settings.get("html_font_face"), id(_settings))



#-----------------------------------------------------------------------------------
def plugin_unloaded():
    ''' Clean up module global stuff. '''
    trace('plugin_unloaded sbot_common')


#-----------------------------------------------------------------------------------
def ensure_init():
    ''' Call these before accessing global stuff. TODO2 Ugly kludge - fix. '''
    global _settings
    global _trace_fn

    if _settings == None:
        _settings = sublime.load_settings(SETTINGS_FN) #TODO2 doesn't reload on change.
        _trace_fn = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', 'temp', 'trace.txt')


#-----------------------------------------------------------------------------------
def trace(*args, cat=None):
    ''' Debugging. '''
    global _trace_fn
    ensure_init()

    if cat == None:
        s = ' | '.join(map(str, args))
    else:
        s = cat + ' ' + ' | '.join(map(str, args))

#    print(s)
    # and/or TODO1 print | file | off , max_size, w/a? Also shouldn't have to do fn every time...
    with open(_trace_fn, "a+") as f:
        f.write(s + '\n')    

    # print('^^^102', _settings.get("html_font_face"), id(_settings))

#-----------------------------------------------------------------------------------
def error(*args):
    ''' Debugging. '''
    trace(*args, cat='ERR')
    # sublime.error_message(' '.join(map(str, args)))
    print(*args)


#-----------------------------------------------------------------------------------
def get_sel_regions(v):
    ''' Generic function to get selections or optionally the whole view.'''
    ensure_init()

    regions = []    
    if len(v.sel()[0]) > 0: # user sel
        regions = v.sel()
    elif _settings.get('sel_all'):
        regions = [sublime.Region(0, v.size())]
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
            sys.stdout.write(chr(b));


#-----------------------------------------------------------------------------------
def dump_view(preamble, view):
    ''' Helper util. '''
    s = []
    s.append('view')
    s.append(preamble)

    s.append('view_id:')
    s.append('None' if view is None else str(view.id()))

    if view is not None:
        w = view.window()
        fn = view.file_name()

        s.append('file_name:')
        s.append('None' if fn is None else os.path.split(fn)[1])

        s.append('project_file_name:')
        s.append('None' if w is None or w.project_file_name() is None else os.path.split(w.project_file_name())[1])

    trace(" ".join(s));
            

#-----------------------------------------------------------------------------------
def wait_load_file(view, line):
    ''' Open file asynchronously then position at line. '''
    if view.is_loading():
        sublime.set_timeout(lambda: wait_load_file(view, line), 100) # maybe not forever?
    else: # good to go
        view.run_command("goto_line", {"line": line})


#-----------------------------------------------------------------------------------
class SbotPerfCounter(object):
    ''' Container for perf counter. All times in msec. '''

    def __init__(self, id):
        self.id = id
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

