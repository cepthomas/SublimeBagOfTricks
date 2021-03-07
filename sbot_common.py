import os
import time
import sublime
import sublime_plugin


#-----------------------------------------------------------------------------------
def initialize():
    ''' Vars shared across project.'''
    global settings
    settings = sublime.load_settings('SublimeBagOfTricks.sublime-settings')


#-----------------------------------------------------------------------------------
def get_sel_regions(v):
    ''' Generic function to get selections or optionally the whole view.'''

    regions = []    
    if len(v.sel()[0]) > 0: # user sel
        regions = v.sel()
    elif settings.get('sel_all', True):
        regions = [sublime.Region(0, v.size())]
    return regions


#-----------------------------------------------------------------------------------
def create_new_view(window, text):
    ''' Creates a temp view with text. Returns the view.'''

    vnew = window.new_file()
    vnew.set_scratch(True)
    vnew.run_command('insert', {'characters': text })
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


#-----------------------------------------------------------------------------------
def trace(*objects):
    # 'Hey {name}, there is a 0x{errno:x} error!'.format(name=name, errno=errno)
    # f-string   f'Five plus ten is {a + b} and not {2 * (a + b)}.'

    # print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False)
    print(*objects, sep=', ')
    # or append to file TODO
    # logfn = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', 'temp', 'sbot_log.txt')
    # print('Logfile:', logfn)
    # logformat = "%(asctime)s %(levelname)8s <%(name)s> %(message)s"
    # logging.basicConfig(filename=logfn, filemode='w', format=logformat, level=logging.INFO)
    # logging.info("=============================== log start ===============================");

    # pass