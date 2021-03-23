import os
import sys
import json
import sublime
import sublime_plugin
import sbot_common

# print('Load sbot_signet')


# Definitions.
SIGNET_REGION_NAME = 'signet'
SIGNET_ICON = 'Packages/Theme - Default/common/label.png'
SIGNET_FILE_EXT = '.sbot-sigs'
NEXT_SIG = 1
PREV_SIG = 2

# The current signet collections. Key is window id which corresponds to a project.
_sigs = {}

# Need to track these because ST window/view lifecycle is unreliable.
_views_inited = set()



#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. '''
    sbot_common.trace('plugin_loaded sbot_signet')


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    ''' Clean up module global stuff. '''
    sbot_common.trace('plugin_unloaded sbot_signet')


#-----------------------------------------------------------------------------------
class SignetEvent(sublime_plugin.ViewEventListener):
    ''' Listener for view specific events of interest. '''

    def on_activated(self):
        ''' When focus/tab received. This is the only reliable event - on_load() doesn't get called when showing previously opened files. '''
        view = self.view
        global _views_inited
        vid = view.id()
        winid = view.window().id()
        fn = view.file_name()

        sbot_common.trace('SignetEvent.on_activated', fn, vid, winid)

        # Lazy init.
        if fn is not None: # Sometimes this happens...
            # Is the persist file read yet?
            if winid not in _sigs:
                _open_sigs(winid, view.window().project_file_name())

            # Init the view, maybe.
            if vid not in _views_inited:
                _views_inited.add(vid)

                # Init the view with any persist values.
                rows = _get_persist_rows(view, False)
                if rows is not None:
                    # Update visual signets, brutally. This is the ST way.
                    regions = []
                    for r in rows:
                        pt = view.text_point(r-1, 0) # ST is 0-based
                        regions.append(sublime.Region(pt, pt))
                    settings = sublime.load_settings(sbot_common.SETTINGS_FN)
                    view.add_regions(SIGNET_REGION_NAME, regions, settings.get('signet_scope'), SIGNET_ICON)


    def on_load(self):
        ''' Called when file loaded. Doesn't work when starting up! Maybe ST4 improved? '''
        view = self.view
        sbot_common.trace('SignetEvent.on_load', view.file_name(), view.id(), view.window, view.window().project_file_name())
        # if view.file_name() is not None:


    def on_deactivated(self):
        ''' When focus/tab lost. Save to file. Crude, but on_close is not reliable so we take the conservative approach. '''
        view = self.view
        winid = view.window().id()
        sbot_common.trace('SignetEvent.on_deactivated', view.id(), winid)

        if winid in _sigs:
            _save_sigs(winid, view.window().project_file_name())


    def on_close(self):
        ''' Called when a view is closed (note, there may still be other views into the same buffer). '''
        view = self.view
        sbot_common.trace('SignetEvent.on_close', view.file_name(), view.id())


#-----------------------------------------------------------------------------------
class SbotToggleSignetCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        v = self.view
        
        # Get current row.
        sel_row, _ = v.rowcol(v.sel()[0].a)

        drows = _get_display_signet_rows(v)

        if sel_row != -1:
            # Is there one currently at the selected row?
            existing = sel_row in drows
            if existing:
                drows.remove(sel_row)
            else:
                drows.append(sel_row)

        # Update collection.
        crows = _get_persist_rows(v, True)
        crows.clear()
        for r in drows:
            crows.append(r + 1)

        # Update visual signets, brutally. This is the ST way.
        regions = []
        for r in drows:
            pt = v.text_point(r, 0) # 0-based
            regions.append(sublime.Region(pt, pt))

        settings = sublime.load_settings(sbot_common.SETTINGS_FN)
        v.add_regions(SIGNET_REGION_NAME, regions, settings.get('signet_scope'), SIGNET_ICON)


#-----------------------------------------------------------------------------------
class SbotNextSignetCommand(sublime_plugin.TextCommand):
    ''' Navigate to signet in whole collection. '''

    def run(self, edit):
        _go_to_signet(self.view, NEXT_SIG)


#-----------------------------------------------------------------------------------
class SbotPreviousSignetCommand(sublime_plugin.TextCommand):
    ''' Navigate to signet in whole collection. '''

    def run(self, edit):
        _go_to_signet(self.view, PREV_SIG)


#-----------------------------------------------------------------------------------
class SbotClearSignetsCommand(sublime_plugin.TextCommand):
    ''' Clear all signets. '''

    def run(self, edit):
        # Remove from collection.
        rows = _get_persist_rows(self.view, False)
        if rows is not None:
            rows.clear()

        # Clear visuals in open views.
        for vv in self.view.window().views():
            vv.erase_regions(SIGNET_REGION_NAME)


#-----------------------------------------------------------------------------------
def _save_sigs(winid, stp_fn):
    ''' General project saver. '''
    ok = True
    settings = sublime.load_settings(sbot_common.SETTINGS_FN)

    if settings.get('enable_persistence') and stp_fn is not None:
        stp_fn = stp_fn.replace('.sublime-project', SIGNET_FILE_EXT)
        
        try:
            # Remove invalid files and any empty values.
            if winid in _sigs:
                for fn, _ in _sigs[winid].items():
                    if not os.path.exists(fn):
                        del _sigs[winid][fn]
                    elif len(_sigs[winid][fn]) == 0:
                        del _sigs[winid][fn]

                # Now save.
                with open(stp_fn, 'w') as fp:
                    json.dump(_sigs[winid], fp, indent=4)

        except Exception as e:
            sbot_common.error('Save signets error1', e)
            ok = False

    return ok


#-----------------------------------------------------------------------------------
def _open_sigs(winid, stp_fn):
    ''' General project opener. '''
    global _sigs

    ok = True
    settings = sublime.load_settings(sbot_common.SETTINGS_FN)

    if settings.get('enable_persistence') and stp_fn is not None:
        fn = stp_fn.replace('.sublime-project', SIGNET_FILE_EXT)

        try:
            with open(fn, 'r') as fp:
                values = json.load(fp)
                _sigs[winid] = values

        except FileNotFoundError as e:
            # Assumes new file.
            sublime.status_message('Creating new signets file')
            _sigs[winid] = { }

        except Exception as e:
            sbot_common.error('Save signets error2', e)
            ok = False

    return ok


#-----------------------------------------------------------------------------------
def _go_to_signet(view, dir):
    ''' Navigate to signet in whole collection. dir is NEXT_SIG or PREV_SIG. '''
    v = view
    w = view.window()

    settings = sublime.load_settings(sbot_common.SETTINGS_FN)

    signet_nav_files = settings.get('signet_nav_files')

    signet_nav_files
    done = False
    sel_row, _ = v.rowcol(v.sel()[0].a) # current sel
    incr = +1 if dir == NEXT_SIG else -1
    array_end = 0 if dir == NEXT_SIG else -1

    # 1) NEXT_SIG: If there's another bookmark below >>> goto it
    # 1) PREV_SIG: If there's another bookmark above >>> goto it
    if not done:
        sig_rows = _get_display_signet_rows(v)
        if dir == PREV_SIG:
            sig_rows.reverse()

        for sr in sig_rows:
            if (dir == NEXT_SIG and sr > sel_row) or (dir == PREV_SIG and sr < sel_row):
                w.active_view().run_command("goto_line", {"line": sr + 1})
                done = True
                break

        # At begin or end. Check for single file operation.
        if not done and not signet_nav_files and len(sig_rows) > 0:
            w.active_view().run_command("goto_line", {"line": sig_rows[0] + 1})
            done = True

    # 2) NEXT_SIG: Else if there's an open signet file to the right of this tab >>> focus tab, goto first signet
    # 2) PREV_SIG: Else if there's an open signet file to the left of this tab >>> focus tab, goto last signet
    if not done:
        view_index = w.get_view_index(v)[1] + incr
        while not done and ((dir == NEXT_SIG and view_index < len(w.views()) or (dir == PREV_SIG and view_index >= 0))):
            vv = w.views()[view_index]
            sig_rows = _get_display_signet_rows(vv)
            if(len(sig_rows) > 0):
                w.focus_view(vv)
                vv.run_command("goto_line", {"line": sig_rows[array_end] + 1})
                done = True
            else:
                view_index += incr

    # 3) NEXT_SIG: Else if there is a signet file in the project that is not open >>> open it, focus tab, goto first signet
    # 3) PREV_SIG: Else if there is a signet file in the project that is not open >>> open it, focus tab, goto last signet
    if not done:
        winid = w.id()

        for fn, rows in _sigs[winid].items():
            if w.find_open_file(fn) is None and os.path.exists(fn) and len(rows) > 0:
                vv = w.open_file(fn)
                sublime.set_timeout(lambda: sbot_common.wait_load_file(vv, rows[array_end]), 10) # already 1-based in file
                w.focus_view(vv)
                done = True
                break

    # 4) NEXT_SIG: Else >>> find first tab/file with signets, focus tab, goto first signet
    # 4) PREV_SIG: Else >>> find last tab/file with signets, focus tab, goto last signet
    if not done:
        view_index = 0 if dir == NEXT_SIG else len(w.views()) - 1
        while not done and ((dir == NEXT_SIG and view_index < len(w.views()) or (dir == PREV_SIG and view_index >= 0))):
            vv = w.views()[view_index]
            sig_rows = _get_display_signet_rows(vv)
            if(len(sig_rows) > 0):
                w.focus_view(vv)
                vv.run_command("goto_line", {"line": sig_rows[array_end] + 1})
                done = True
            else:
                view_index += incr


#-----------------------------------------------------------------------------------
def _get_display_signet_rows(view):
    ''' Get all the signet row numbers in the view. Returns a sorted list. '''
    sig_rows = []
    for reg in view.get_regions(SIGNET_REGION_NAME):
        row, _ = view.rowcol(reg.a)
        sig_rows.append(row)
    sig_rows.sort()
    return sig_rows


#-----------------------------------------------------------------------------------
def _get_persist_rows(view, init_empty):
    ''' General helper to get the data values from collection. If init_empty and there are none, add a default value. '''
    global _sigs

    vals = None # Default
    winid = view.window().id()
    fn = view.file_name()

    if winid in _sigs:
        if fn not in _sigs[winid]:
            if init_empty:
                # Add a new one.
                _sigs[winid][fn] = []
                vals = _sigs[winid][fn]
        else:
            vals = _sigs[winid][fn]

    return vals
