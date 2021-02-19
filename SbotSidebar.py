import os
import sys
import subprocess
import sublime
import sublime_plugin



#-----------------------------------------------------------------------------------
class SbotSidebarCopyNameCommand(sublime_plugin.WindowCommand):

    def run(self, paths):
        names = (os.path.split(path)[1] for path in paths)
        sublime.set_clipboard('\n'.join(names))


#-----------------------------------------------------------------------------------
class SbotSidebarCopyPathCommand(sublime_plugin.WindowCommand):

    def run(self, paths):
        sublime.set_clipboard('\n'.join(paths))


#-----------------------------------------------------------------------------------
class SbotSidebarTerminalCommand(sublime_plugin.WindowCommand):

    def run(self, paths):
        if len(paths) > 0:
            dir = paths[0] if os.path.isdir(paths[0]) else os.path.split(paths[0])[0]
            subprocess.call(['wt', '-d', dir])


#-----------------------------------------------------------------------------------
class SbotSidebarFolderCommand(sublime_plugin.WindowCommand):

    def run(self, paths):
        if len(paths) > 0:
            dir = paths[0] if os.path.isdir(paths[0]) else os.path.split(paths[0])[0]
            subprocess.call(['explorer', dir], shell=True)

    def is_visible(self, paths):
        vis = len(paths) > 0 and os.path.isdir(paths[0])
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarTreeCommand(sublime_plugin.WindowCommand):

    def run(self, paths):
        if len(paths) > 0:
            dir = paths[0] if os.path.isdir(paths[0]) else os.path.split(paths[0])[0]
            subprocess.call(['tree', dir, '/a', '/f', '|', 'clip'], shell=True)

    def is_visible(self, paths):
        vis = len(paths) > 0 and os.path.isdir(paths[0])
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarExecCommand(sublime_plugin.WindowCommand):

    def run(self, paths):
        if len(paths) > 0:
            # print(paths[0])
            subprocess.call([paths[0]], shell=True) #TODOC collect stdout/stderr, dump to console.

    def is_visible(self, paths):
        # print(os.path.splitext(paths[0]))
        vis = len(paths) > 0 and os.path.splitext(paths[0])[1] in ['.exe', '.cmd', '.bat']
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarExcludeCommand(sublime_plugin.WindowCommand):

    def __init__(self, window):
        self.fn = window.project_file_name()
        self.window = window

    def run(self, paths):
        if len(paths) > 0:
            pdata = self.window.project_data()

            exclude = paths[0]
            dir = exclude if os.path.isdir(exclude) else os.path.split(exclude)[0]
            fn = '' if os.path.isdir(exclude) else os.path.split(exclude)[1]

            # Locate the folder.
            found = False
            for folder in pdata["folders"]:
                fpath = folder["path"]
                apath = os.path.split(self.fn)[0] if(fpath == '.') else os.path.abspath(fpath)

                if dir.startswith(apath):
                    # Make a relative ref.
                    rpath = os.path.relpath(exclude, apath)
                    patfold = "folder_exclude_patterns" if os.path.isdir(exclude) else "file_exclude_patterns"

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
                logging.info('not found:' + paths[0])

    def is_visible(self, paths):
        # Disallow project folders - they should use builtin remove_folder.
        vis = True
        if len(paths) > 0:
            if os.path.isdir(paths[0]):
                pdata = self.window.project_data()
                dir = paths[0]

                for folder in pdata["folders"]:
                    fpath = folder["path"]
                    apath = os.path.split(self.fn)[0] if fpath == '.' else os.path.abspath(fpath)
                    if dir == apath:
                        vis = False
                        break
            # else: Just a file = ok.
        else:
            vis = False

        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarOpenBrowserCommand(sublime_plugin.WindowCommand):

    def run(self, paths):
        webbrowser.open_new_tab(paths[0])

    def is_visible(self, paths):
        vis = False

        if len(paths) > 0:
            if os.path.isfile(paths[0]):
                fn = os.path.split(paths[0])[1]
                if '.htm' in fn:
                    vis = True
        return vis
