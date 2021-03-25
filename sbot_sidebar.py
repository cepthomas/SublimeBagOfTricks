import os
import subprocess
import webbrowser
import sublime
import sublime_plugin
import sbot_common


# print('Load sbot_sidebar')


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. '''
    sbot_common.trace('plugin_loaded sbot_sidebar')


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    ''' Clean up module global stuff. '''
    sbot_common.trace('plugin_unloaded sbot_sidebar')


#-----------------------------------------------------------------------------------
class SbotSidebarCopyNameCommand(sublime_plugin.WindowCommand):
    ''' Get file name to clipboard. '''

    def run(self, paths):
        names = (os.path.split(path)[1] for path in paths)
        sublime.set_clipboard('\n'.join(names))


#-----------------------------------------------------------------------------------
class SbotSidebarCopyPathCommand(sublime_plugin.WindowCommand):
    ''' Get file path to clipboard. '''

    def run(self, paths):
        sublime.set_clipboard('\n'.join(paths))


#-----------------------------------------------------------------------------------
class SbotSidebarTerminalCommand(sublime_plugin.WindowCommand):
    ''' Open win term here. '''

    def run(self, paths):
        if len(paths) > 0:
            path = paths[0] if os.path.isdir(paths[0]) else os.path.split(paths[0])[0]
            cmd = 'wt -d "{}"'.format(path)
            subprocess.call(cmd, shell=True)


#-----------------------------------------------------------------------------------
class SbotSidebarFolderCommand(sublime_plugin.WindowCommand):
    ''' Open current folder. '''

    def run(self, paths):
        if len(paths) > 0:
            path = paths[0] if os.path.isdir(paths[0]) else os.path.split(paths[0])[0]
            cmd = 'explorer "{}"'.format(path)
            subprocess.call(cmd, shell=True)

    def is_visible(self, paths):
        vis = len(paths) > 0 and os.path.isdir(paths[0])
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarTreeCommand(sublime_plugin.WindowCommand):
    ''' Run tree command to clipboard. '''

    def run(self, paths):
        if len(paths) > 0:
            path = paths[0] if os.path.isdir(paths[0]) else os.path.split(paths[0])[0]
            cmd = 'tree "{}" /a /f | clip'.format(path)
            subprocess.call(cmd, shell=True)
            # subprocess.call(['tree', path, '/a', '/f', '|', 'clip'])#, shell=True)

    def is_visible(self, paths):
        vis = len(paths) > 0 and os.path.isdir(paths[0])
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarExecCommand(sublime_plugin.WindowCommand):
    ''' Simple executioner for exes/cmds without args. '''

    def run(self, paths):
        if len(paths) > 0:
            sout = subprocess.check_output([paths[0]], universal_newlines=True)
            sbot_common.create_new_view(self.window, sout)

    def is_visible(self, paths):
        vis = len(paths) > 0 and os.path.splitext(paths[0])[1] in ['.exe', '.cmd', '.bat']
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarExcludeCommand(sublime_plugin.WindowCommand):
    ''' Remove from project. '''

    def __init__(self, window):#TODO-T remove this
        self.fn = window.project_file_name()
        super(SbotSidebarExcludeCommand, self).__init__(window)

    def run(self, paths):
        if len(paths) > 0:
            pdata = self.window.project_data()

            exclude = paths[0]
            path = exclude if os.path.isdir(exclude) else os.path.split(exclude)[0]
            #fn = '' if os.path.isdir(exclude) else os.path.split(exclude)[1]

            # Locate the folder.
            found = False
            for folder in pdata["folders"]:
                fpath = folder["path"]
                apath = os.path.split(self.fn)[0] if(fpath == '.') else os.path.abspath(fpath)

                if path.startswith(apath):
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
                sbot_common.trace('not found:', paths[0])

    def is_visible(self, paths):
        # Disallow project folders - they should use builtin remove_folder.
        vis = True
        if len(paths) > 0:
            if os.path.isdir(paths[0]):
                pdata = self.window.project_data()
                path = paths[0]

                for folder in pdata["folders"]:
                    fpath = folder["path"]
                    apath = os.path.split(self.fn)[0] if fpath == '.' else os.path.abspath(fpath)
                    if path == apath:
                        vis = False
                        break
            # else: Just a file is ok.
        else:
            vis = False

        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarOpenBrowserCommand(sublime_plugin.WindowCommand):
    ''' Simple exec for html files. '''

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
