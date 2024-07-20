import os
# import platform
import subprocess
import shutil
import re
import logging
import sublime
import sublime_plugin
from . import sbot_common as sc

# Known script file types.
SCRIPT_TYPES = ['.py', '.lua', '.cmd', '.bat', '.sh']

SBOT_SETTINGS_FILE = "SublimeBagOfTricks.sublime-settings"

rex = re.compile(r'\[(.*)\]\(([^\)]*)\)')

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


#-----------------------------------------------------------------------------------
class SbotGeneralEvent(sublime_plugin.EventListener):
    ''' Listener for window events of global interest. '''

    def on_selection_modified(self, view):
        ''' Show the abs position in the status bar. '''
        caret = sc.get_single_caret(view)
        view.set_status("position", '???' if caret is None else f'Pos {caret}')


#-----------------------------------------------------------------------------------
class SbotSplitViewCommand(sublime_plugin.TextCommand):
    ''' Toggles between split file views. '''

    def run(self, edit):
        window = self.view.window()

        if len(window.layout()['rows']) > 2:
            # Remove split.
            window.run_command("focus_group", {"group": 1})
            window.run_command("close_file")
            window.run_command("set_layout", {"cols": [0.0, 1.0], "rows": [0.0, 1.0], "cells": [[0, 0, 1, 1]]})
        else:
            # Add split.
            caret = sc.get_single_caret(self.view)
            sel_row, _ = self.view.rowcol(caret)  # current sel
            window.run_command("set_layout", {"cols": [0.0, 1.0], "rows": [0.0, 0.5, 1.0], "cells": [[0, 0, 1, 1], [0, 1, 1, 2]]})
            window.run_command("focus_group", {"group": 0})
            window.run_command("clone_file")
            window.run_command("move_to_group", {"group": 1})
            self.view.run_command("goto_line", {"line": sel_row})


#-----------------------------------------------------------------------------------
class SbotOpenContextPathCommand(sublime_plugin.TextCommand):
    '''
    Borrowed from open_context_url.py. Note that that file is now 
    disabled and the function apparently implemented internally.
    '''

    def run(self, edit, event):
        path = self.find_path(event)
        sc.open_path(path)

    def is_visible(self, event):
        return self.find_path(event) is not None

    def find_path(self, event):
        # Get the text.
        pt = self.view.window_to_text((event["x"], event["y"]))
        line = self.view.line(pt) # Region
        text = self.view.substr(line)

        # Test all matches on the line against the one where the cursor is.
        it = rex.finditer(text)
        for match in it:
            if match.start() <= (pt - line.a) and match.end() >= (pt - line.a):
                path = match.group(2)
                if os.path.exists(path):
                    return path
        return None

    def description(self, event):
        # For menu.
        path = self.find_path(event)
        return "Open Path " + path

    def want_event(self):
        return True


#-----------------------------------------------------------------------------------
class SbotTreeCommand(sublime_plugin.WindowCommand):
    ''' Run tree command to a new view. '''

    def run(self, paths=None):
        dir, fn, path = sc.get_path_parts(self.window, paths)

        try:
            cmd = f'tree "{dir}" /a /f'
            cp = subprocess.run(cmd, universal_newlines=True, capture_output=True, shell=True, check=True)
            sc.create_new_view(self.window, cp.stdout)
        except Exception as e:
            sc.create_new_view(self.window, f'Well, that did not go well: {e}\n{cp.stderr}')

    def is_visible(self, paths=None):
        dir, fn, path = sc.get_path_parts(self.window, paths)
        return dir is not None


#-----------------------------------------------------------------------------------
class SbotRunCommand(sublime_plugin.WindowCommand):
    '''
    If the clicked file is a script, it is executed and the output presented in a new view.
    Supports context and sidebar menus.
    '''
    def run(self, paths=None):
        self.paths = paths
        self.args = None

        # Get user input for args - needs impl.
        get_input = False

        dir, fn, path = sc.get_path_parts(self.window, paths)
        if fn is not None:
            _, ext = os.path.splitext(fn)

            if get_input:
                self.window.show_input_panel(self.window.extract_variables()['folder'] + '>', "", self.on_done_input, None, None)
            else:
                self.execute()

    def on_done_input(self, text):
        self.args = text if len(text) > 0 else None
        self.execute()

    def execute(self):
        # Assemble and execute.
        dir, fn, path = sc.get_path_parts(self.window, self.paths)

        if fn is not None:
            _, ext = os.path.splitext(fn)

            try:
                cmd_list = []
                if ext == '.py':
                    cmd_list.append('python')
                    cmd_list.append(f'\"{path}\"')
                elif ext == '.lua':
                    cmd_list.append('lua')
                    cmd_list.append(f'\"{path}\"')
                elif ext in SCRIPT_TYPES:
                    cmd_list.append(f'\"{path}\"')
                else:
                    _logger.warning(f"Unsupported file type: {path}")
                    return

                if self.args:
                    cmd_list.append(self.args)

                cmd = ' '.join(cmd_list)

                cp = subprocess.run(cmd, cwd=dir, universal_newlines=True, capture_output=True, shell=True)  # check=True)
                output = cp.stdout
                errors = cp.stderr
                if len(errors) > 0:
                    output = output + '============ stderr =============\n' + errors
                sc.create_new_view(self.window, output)
            except:# Exception as e:
                logging.exception("Execute script failed")

    def is_visible(self, paths=None):
        vis = True
        dir, fn, path = sc.get_path_parts(self.window, paths)
        if fn is None:
            vis = False
        else:
            _, ext = os.path.splitext(fn)
            vis = ext in SCRIPT_TYPES
        return vis


#-----------------------------------------------------------------------------------
class SbotOpenCommand(sublime_plugin.WindowCommand): 
    '''
    Acts as if you had clicked the file in the UI, honors your file associations.
    Supports context and sidebar menus.
    '''
    def run(self, paths=None):
        dir, fn, path = sc.get_path_parts(self.window, paths)
        if fn is not None:
            sc.open_path(path)

    def is_visible(self, paths=None):
        dir, fn, path = sc.get_path_parts(self.window, paths)
        return fn is not None


#-----------------------------------------------------------------------------------
class SbotTerminalCommand(sublime_plugin.WindowCommand):
    '''
    Open term in this directory.
    Supports context and sidebar menus.
    '''
    def run(self, paths=None):
        dir, fn, path = sc.get_path_parts(self.window, paths)
        if dir is not None:
            sc.open_terminal(dir)

    def is_visible(self, paths=None):
        dir, fn, path = sc.get_path_parts(self.window, paths)
        return dir is not None


#-----------------------------------------------------------------------------------
class SbotCopyNameCommand(sublime_plugin.WindowCommand):
    '''
    Get file or directory name to clipboard.
    Supports context and sidebar menus.
    '''
    def run(self, paths=None):
        dir, fn, path = sc.get_path_parts(self.window, paths)
        if path is not None:
            sublime.set_clipboard(os.path.split(path)[-1])

    def is_visible(self, paths=None):
        dir, fn, path = sc.get_path_parts(self.window, paths)
        return path is not None


#-----------------------------------------------------------------------------------
class SbotCopyPathCommand(sublime_plugin.WindowCommand):
    '''
    Get file or directory path to clipboard.
    Supports context and sidebar menus.
    '''
    def run(self, paths=None):
        dir, fn, path = sc.get_path_parts(self.window, paths)
        if path is not None:
            sublime.set_clipboard(path)

    def is_visible(self, paths=None):
        dir, fn, path = sc.get_path_parts(self.window, paths)
        return path is not None


#-----------------------------------------------------------------------------------
class SbotCopyFileCommand(sublime_plugin.WindowCommand):
    '''
    Copy selected file to the same dir.
    Supports context and sidebar menus.
    '''
    def run(self, paths=None):
        dir, fn, path = sc.get_path_parts(self.window, paths)
        if fn is not None:
            # Find a valid file name.
            ok = False
            root, ext = os.path.splitext(path)
            for i in range(1, 9):
                newfn = f'{root}_{i}{ext}'
                if not os.path.isfile(newfn):
                    shutil.copyfile(path, newfn)
                    ok = True
                    break

            if not ok:
                sublime.status_message("Couldn't copy file")

    def is_visible(self, paths=None):
        dir, fn, path = sc.get_path_parts(self.window, paths)
        return fn is not None


#-----------------------------------------------------------------------------------
class SbotDeleteFileCommand(sublime_plugin.WindowCommand):
    '''
    Delete the file in the current view.
    Supports context and tab menus.
    '''
    def run(self):  # , paths=None):
        dir, fn, path = sc.get_path_parts(self.window, None)
        if fn is not None:
            self.window.run_command("delete_file", {"files": [path], "prompt": False})

    def is_visible(self):  #, paths=None):
        dir, fn, path = sc.get_path_parts(self.window, None)
        return fn is not None


#-----------------------------------------------------------------------------------
class SbotTrimCommand(sublime_plugin.TextCommand):
    '''sbot_trim how=leading|trailing|both'''

    def run(self, edit, how):
        if how == 'leading':
            reo = re.compile('^[ \t]+', re.MULTILINE)
            sub = ''
        elif how == 'trailing':
            reo = re.compile('[\t ]+$', re.MULTILINE)
            sub = ''
        else:  # both
            reo = re.compile('^[ \t]+|[\t ]+$', re.MULTILINE)
            sub = ''
        _do_sub(self.view, edit, reo, sub)


#-----------------------------------------------------------------------------------
class SbotRemoveEmptyLinesCommand(sublime_plugin.TextCommand):
    '''sbot_remove_empty_lines  how=remove_all|normalize'''

    def run(self, edit, how):
        if how == 'normalize':
            reo = re.compile(r'(?:\s*)(\r?\n)(?:\s*)(?:\r?\n+)', re.MULTILINE)
            sub = r'\1\1'
        else:  # remove_all
            reo = re.compile('^[ \t]*$\r?\n', re.MULTILINE)
            sub = ''
        _do_sub(self.view, edit, reo, sub)


#-----------------------------------------------------------------------------------
class SbotRemoveWsCommand(sublime_plugin.TextCommand):
    '''sbot_remove_ws  how=remove_all|keep_eol|normalize'''

    def run(self, edit, how):
        if how == 'normalize':
            # Note: doesn't trim trailing.
            reo = re.compile('([ ])[ ]+')
            sub = r'\1'
        elif how == 'keep_eol':
            reo = re.compile(r'[ \t\v\f]')
            sub = ''
        else:  # remove_all
            reo = re.compile(r'[ \t\r\n\v\f]')
            sub = ''
        _do_sub(self.view, edit, reo, sub)


#-----------------------------------------------------------------------------------
class SbotInsertLineIndexesCommand(sublime_plugin.TextCommand):
    ''' Insert sequential numbers in first column. Default is to start at 1. '''

    def run(self, edit):
        # Iterate lines.
        line_count = self.view.rowcol(self.view.size())[0]
        width = len(str(line_count))
        offset = 0

        settings = sublime.load_settings(SBOT_SETTINGS_FILE)
        for region in sc.get_sel_regions(self.view, settings):
            line_num = 1
            offset = 0
            for line_region in self.view.split_by_newlines(region):
                s = f'{line_num:0{width}} '
                self.view.insert(edit, line_region.a + offset, s)
                line_num += 1
                # Adjust for inserts.
                offset += width + 1


#-----------------------------------------------------------------------------------
def _do_sub(view, edit, reo, sub):
    # Generic substitution function.
    settings = sublime.load_settings(SBOT_SETTINGS_FILE)
    for region in sc.get_sel_regions(view, settings):
        orig = view.substr(region)
        new = reo.sub(sub, orig)
        view.replace(edit, region, new)


#-----------------------------------------------------------------------------------
class SbotAllScopesCommand(sublime_plugin.TextCommand):
    ''' Show style info for common scopes. '''

    def run(self, edit):
        settings = sublime.load_settings(SBOT_SETTINGS_FILE)
        scopes = settings.get('scopes_to_show')
        _render_scopes(scopes, self.view)


#-----------------------------------------------------------------------------------
class SbotScopeInfoCommand(sublime_plugin.TextCommand):
    ''' Like builtin ShowScopeNameCommand but with coloring added. '''

    def run(self, edit):
        caret = sc.get_single_caret(self.view)
        if caret is not None:
            scope = self.view.scope_name(caret).rstrip()
            scopes = scope.split()
            _render_scopes(scopes, self.view)


#-----------------------------------------------------------------------------------
def _copy_scopes(view, scopes):
    ''' Copy to clipboard. '''

    sublime.set_clipboard(scopes)
    view.hide_popup()
    sublime.status_message('Scope names copied to clipboard')


#-----------------------------------------------------------------------------------
def _render_scopes(scopes, view):
    ''' Make popup for list of scopes. '''

    style_text = []
    content = []

    for scope in scopes:
        style = view.style_for_scope(scope)
        props = f'{{ color:{style["foreground"]}; '
        props2 = f'fg:{style["foreground"]} '
        if 'background' in style:
            props += f'background-color:{style["background"]}; '
            props2 += f'bg:{style["background"]} '
        if style['bold']:
            props += 'font-weight:bold; '
            props2 += 'bold '
        if style['italic']:
            props += 'font-style:italic; '
            props2 += 'italic '
        props += '}'

        i = len(style_text)
        style_text.append(f'.st{i} {props}')
        content.append(f'<p><span class=st{i}>{scope}  {props2}</span></p>')

    # Do popup
    st = '\n'.join(style_text)
    ct = '\n'.join(content)

    html = f'''
<body>
<style> p {{ margin: 0em; }} {st} </style>
{ct}
</body>
<a href="_copy_scopes">Copy</a>
'''

    to_show = '\n'.join(scopes)
    # to_show = html
    view.show_popup(html, max_width=512, max_height=600, on_navigate=lambda x: _copy_scopes(view, to_show))
