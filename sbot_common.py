import sys
import os
import platform
import subprocess
import pathlib
import collections
import traceback
import logging
import logging.handlers
import sublime

### Do not edit this file - it will be overwritten.

# Internal flag.
_temp_view_id = None

# The package logger.
_logger = None

# Data type.
HighlightInfo = collections.namedtuple('HighlightInfo', 'scope_name, region_name, type')


#-----------------------------------------------------------------------------------
def _notify_exception(exc_type, exc_value, exc_traceback):
    ''' Process unhandled exceptions and notify user. '''

    global _logger

    # TODO? sometimes gets this on shutdown: FileNotFoundError '...Log\plugin_host-3.8-on_exit.log'
    if issubclass(exc_type, FileNotFoundError):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    msg = f'Unhandled exception {exc_type.__name__}: {exc_value}'
    stb = traceback.format_tb(exc_traceback)
    stb.insert(0, msg)
    stb = '\n'.join(stb)
    _logger.error(stb)
    sublime.error_message(msg)

# Connect the last chance hook.
sys.excepthook = _notify_exception

#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Called once per plugin instance. Setup anything global. '''

    # Set up logging.
    _logger = logging.getLogger(__package__)
    log_fn = get_store_fn('sbot.log')

    # Main logger.
    file_handler = logging.handlers.RotatingFileHandler(log_fn, maxBytes=50000, backupCount=5) # should be user config
    file_handler.setFormatter(logging.Formatter('{asctime} {levelname:.3s}: {name} {message}', style='{'))
    _logger.addHandler(file_handler)

    # For user.
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(logging.Formatter(fmt='>>> {levelname:.3s} {name} {message}', style='{'))
    stream_handler.setLevel(logging.INFO)
    _logger.addHandler(stream_handler)


#-----------------------------------------------------------------------------------
def get_store_fn(fn):
    ''' General utility to get store simple file name. '''

    store_path = os.path.join(sublime.packages_path(), 'User', '.SbotStore')
    pathlib.Path(store_path).mkdir(parents=True, exist_ok=True)
    store_fn = os.path.join(store_path, fn)
    return store_fn


#-----------------------------------------------------------------------------------
def get_store_fn_for_project(project_fn, file_ext):
    ''' General utility to get store file name based on ST project name. '''

    store_fn = None
    if project_fn is not None:
        fn = os.path.basename(project_fn).replace('.sublime-project', file_ext)
        store_fn = get_store_fn(fn)
    return store_fn


#-----------------------------------------------------------------------------------
def get_single_caret(view):
    ''' Get current caret position for one only region. If multiples, return None. '''

    if len(view.sel()) == 0:
        raise RuntimeError('No data')
    elif len(view.sel()) == 1:  # single sel
        return view.sel()[0].b
    else:  # multi sel
        return None


#-----------------------------------------------------------------------------------
def get_sel_regions(view):
    ''' Function to get user selection or the whole view if no selection. '''

    regions = []
    if len(view.sel()[0]) > 0:  # user sel
        regions = view.sel()
    else:
        regions = [sublime.Region(0, view.size())]
    return regions


#-----------------------------------------------------------------------------------
def create_new_view(window, text, reuse=True):
    ''' Creates or reuse existing temp view with text. Returns the view.'''

    view = None
    global _temp_view_id

    # Locate the current temp view. This will silently fail if there isn't one.
    if reuse:
        for v in window.views():
            if v.id() == _temp_view_id:
                view = v
                break

    if view is None:
        # New instance.
        view = window.new_file()
        view.set_scratch(True)
        _temp_view_id = view.id()

    # Create/populate the view.
    view.run_command('select_all')
    view.run_command('cut')
    view.run_command('append', {'characters': text})  # insert has some odd behavior - indentation
    
    window.focus_view(view)

    return view


#-----------------------------------------------------------------------------------
def wait_load_file(window, fpath, line):
    ''' Open file asynchronously then position at line. Returns the new View or None if failed. '''

    global _logger
    vnew = None

    def _load(view):
        if vnew.is_loading():
            sublime.set_timeout(lambda: _load(vnew), 10)  # maybe not forever?
        else:
            vnew.run_command("goto_line", {"line": line})

    # Open the file in a new view.
    try:
        vnew = window.open_file(fpath)
        _load(vnew)
    except Exception as e:
        _logger.error(f'Failed to open {fpath}: {e}')
        vnew = None

    return vnew


#-----------------------------------------------------------------------------------
def get_highlight_info(which='all'):
    ''' Get list of builtin scope names and corresponding region names as list of HighlightInfo. '''

    hl_info = []
    if which == 'all' or which == 'user':
        for i in range(6):  # magical knowledge TODO1 fix these, maybe tuple too??
            hl_info.append(HighlightInfo(f'markup.user_hl{i + 1}', f'region_user_hl{i + 1}', 'user'))
    if which == 'all' or which == 'fixed':
        for i in range(3):  # magical knowledge
            hl_info.append(HighlightInfo(f'markup.fixed_hl{i + 1}', f'region_fixed_hl{i + 1}', 'fixed'))
    return hl_info


#-----------------------------------------------------------------------------------
def expand_vars(s: str):
    ''' Smarter version of builtin. Returns expanded string or None if bad var name. '''

    done = False
    count = 0
    while not done:
        if '$' in s:
            sexp = os.path.expandvars(s)
            if s == sexp:
                # Invalid var.
                s = None
                done = True
            else:
                # Go around again.
                s = sexp
        else:
            # Done expanding.
            done = True

        # limit iterations
        if not done:
            count += 1
            if count >= 3:
                done = True
                s = None
    return s


#-----------------------------------------------------------------------------------
def get_path_parts(window, paths):
    '''
    Slide and dice into useful parts. paths is a list of which only the first is considered.
    Returns (dir, fn, path) where:
    - path is fully expanded path or None if invalid.
    - fn is None for a directory.
    '''

    dir = None
    fn = None
    path = None

    view = window.active_view()

    if paths is not None and len(paths) > 0:  # came from sidebar
        # Get the first element of paths.
        path = paths[0]
    elif view is not None:  # came from view menu
        # Get the view file.
        path = view.file_name()
    else:  # maybe image preview - dig out file name
        path = window.extract_variables().get('file')

    if path is not None:
        exp_path = expand_vars(path)
        if os.path.isdir(exp_path):
            dir = exp_path
        else:
            dir, fn = os.path.split(exp_path)
        path = exp_path

    return (dir, fn, path)


#-----------------------------------------------------------------------------------
def open_path(path):
    ''' Acts as if you had clicked the path in the UI. Honors your file associations.'''

    if platform.system() == 'Darwin':
        subprocess.run(('open', path))
    elif platform.system() == 'Windows':
        os.startfile(path)
    else:  # linux variants
        subprocess.run(('xdg-open', path))

    return True
    

#-----------------------------------------------------------------------------------
def open_terminal(where):
    ''' Open a terminal in where. '''

    # This works for gnome. Maybe should support other desktop types?
    # Kde -> konsole
    # xfce4 -> xfce4-terminal
    # Cinnamon -> x-terminal-emulator
    # MATE -> mate-terminal --window
    # Unity -> gnome-terminal --profile=Default

    if platform.system() == 'Windows':
        cmd = f'wt -d "{where}"'  # W10+
    else:  # linux + mac(?)
        cmd = f'gnome-terminal --working-directory="{where}"'
    subprocess.run(cmd, shell=False, check=False)
