import os
import subprocess
import webbrowser
import shutil
import sublime
import sublime_plugin
from sbot_common import *


# print('Python: load sbot_sidebar')


#-----------------------------------------------------------------------------------
def get_dir(paths):
    path = paths[0] if os.path.isdir(paths[0]) else os.path.split(paths[0])[0]
    return path


#-----------------------------------------------------------------------------------
class SbotSidebarCopyNameCommand(sublime_plugin.WindowCommand):
    ''' Get file name to clipboard. '''

    def run(self, paths):
        try:
            names = (os.path.split(path)[1] for path in paths)
            sublime.set_clipboard('\n'.join(names))
        except Exception as e:
            plugin_exception(e)


#-----------------------------------------------------------------------------------
class SbotSidebarCopyPathCommand(sublime_plugin.WindowCommand):
    ''' Get file path to clipboard. '''

    def run(self, paths):
        try:
            sublime.set_clipboard('\n'.join(paths))
        except Exception as e:
            plugin_exception(e)


#-----------------------------------------------------------------------------------
class SbotSidebarCopyFileCommand(sublime_plugin.WindowCommand):
    ''' Copy selected file to the same dir. '''

    def run(self, paths):
        ok = False
        try:
            fn = paths[0]
            # Find a valid file name.
            root, ext = os.path.splitext(fn)
            for i in range(1, 9):
                newfn = f'{root}_{i}{ext}'
                if not os.path.isfile(newfn):
                    shutil.copyfile(fn, newfn)
                    ok = True
                    break
        except Exception as e:
            plugin_exception(e)

        if not ok:
            sublime.status_message("Couldn't copy file")    

    def is_visible(self, paths):
        vis = len(paths) > 0 and os.path.isfile(paths[0])
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarTerminalCommand(sublime_plugin.WindowCommand):
    ''' Open term here. '''

    def run(self, paths):
        try:
            if len(paths) > 0:
                path = get_dir(paths)
                cmd = f'wt -d "{path}"'
                subprocess.run(cmd, shell=True)
        except Exception as e:
            plugin_exception(e)


    def is_visible(self, paths):
        vis = os.name == 'nt'
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarOpenFolderCommand(sublime_plugin.WindowCommand):
    ''' Open current folder. '''

    def run(self, paths):
        try:
            if len(paths) > 0:
                path = get_dir(paths)
                cmd = f'explorer "{path}"'
                subprocess.run(cmd, shell=True)
        except Exception as e:
            plugin_exception(e)


    def is_visible(self, paths):
        vis = os.name == 'nt' and len(paths) > 0
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarTreeCommand(sublime_plugin.WindowCommand):
    ''' Run tree command to clipboard. '''

    def run(self, paths):
        try:
            if len(paths) > 0:
                path = get_dir(paths)
                cmd = f'tree "{path}" /a /f'
                cp = subprocess.run(cmd, universal_newlines=True, capture_output=True, shell=True)
                create_new_view(self.window, cp.stdout)
        except Exception as e:
            plugin_exception(e)


    def is_visible(self, paths):
        vis = os.name == 'nt' and len(paths) > 0
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarExecCommand(sublime_plugin.WindowCommand):
    ''' Simple executioner for exes/cmds without args. '''

    def run(self, paths):
        try:
            if len(paths) > 0:
                path = get_dir(paths)
                cmd = ['python', paths[0]] if paths[0].endswith('.py') else [paths[0]]
                cp = subprocess.run(cmd, universal_newlines=True, capture_output=True, shell=True, cwd=path)
                create_new_view(self.window, cp.stdout)
        except Exception as e:
            plugin_exception(e)


    def is_visible(self, paths):
        vis = len(paths) > 0 and os.path.splitext(paths[0])[1] in ['.exe', '.cmd', '.bat', '.py', '.sh']
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarExcludeCommand(sublime_plugin.WindowCommand):
    ''' Remove from project. Supplements builtin remove_folder. '''

    def run(self, paths):
        try:
            if len(paths) > 0:
                pdata = self.window.project_data()

                exclude = paths[0]
                path = get_dir(paths)
                fn = self.window.project_file_name()

                # Locate the folder.
                found = False
                for folder in pdata["folders"]:
                    fpath = folder["path"]
                    apath = os.path.split(fn)[0] if(fpath == '.') else os.path.abspath(fpath)

                    if path.startswith(apath):
                        # Make a relative ref.
                        rpath = os.path.relpath(exclude, apath)
                        patfold = "folder_exclude_patterns" if os.path.isdir(exclude) else "file_exclude_patterns" # TODO this doesn't work for subdirs - ST thing - needs combo include/exclude

                        try:
                            folder[patfold].append(rpath)
                        except:
                            folder[patfold] = [rpath]
                        found = True
                        break

                # Finish up.
                if found:
                    self.window.set_project_data(pdata)
                else:
                    trace(TraceCat.ERROR, 'not found:', paths[0]) # Fails if folder moved.
        except Exception as e:
            plugin_exception(e)

    def is_visible(self, paths):
        vis = True
        try:
            # Disallow project folders - should use builtin remove_folder.
            if len(paths) > 0:
                if os.path.isdir(paths[0]):
                    pdata = self.window.project_data()
                    path = paths[0]
                    fn = self.window.project_file_name()

                    for folder in pdata["folders"]:
                        fpath = folder["path"]
                        apath = os.path.split(fn)[0] if fpath == '.' else os.path.abspath(fpath)
                        if path == apath:
                            vis = False
                            break
                # else: Just a file is ok.
            else:
                vis = False
        except Exception as e:
            plugin_exception(e)

        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarOpenBrowserCommand(sublime_plugin.WindowCommand):
    ''' Simple exec for html files. '''

    def run(self, paths):
        webbrowser.open_new_tab(paths[0])

    def is_visible(self, paths):
        vis = len(paths) > 0 and os.path.splitext(paths[0])[1] in ['.html', '.svg']
        return vis
