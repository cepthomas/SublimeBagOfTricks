import os
import sys
import sublime
import sublime_plugin
import sbot_common
import sbot_project


# Defs
SIGNET_REGION_NAME = 'signet'
# SIGNET_ICON = 'bookmark'
SIGNET_ICON = 'Packages/Theme - Default/common/label.png'
NEXT_SIG = 1
PREV_SIG = 2


#-----------------------------------------------------------------------------------
class SbotToggleSignetCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        v = self.view
        # Get current row.
        sel_row, _ = v.rowcol(v.sel()[0].a)
        _toggle_signet(v, _get_signet_rows(v), sel_row)


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

    def run(self, edit):
        # Clear internal.
        sproj = sbot_project.get_project(self.view)
        if sproj is not None:
            sproj.signets.clear()

        # Clear visuals in open views.
        for vv in self.view.window().views():
            vv.erase_regions(SIGNET_REGION_NAME)


#-----------------------------------------------------------------------------------
def init_signets(view, rows):
    # Update visual signets, brutally. This is the ST way.
    regions = []
    for r in rows:
        pt = view.text_point(r, 0) # 0-based
        regions.append(sublime.Region(pt, pt))
    view.add_regions(SIGNET_REGION_NAME, regions, sbot_common.settings.get('signet_scope', 'comment'), SIGNET_ICON)


#-----------------------------------------------------------------------------------
def _go_to_signet(view, dir):
    ''' Navigate to signet in whole collection. dir is NEXT_SIG or PREV_SIG. '''

    v = view
    w = view.window()
    signet_nav_files = sbot_common.settings.get('signet_nav_files', True)

    signet_nav_files
    done = False
    sel_row, _ = v.rowcol(v.sel()[0].a) # current sel
    incr = +1 if dir == NEXT_SIG else -1
    array_end = 0 if dir == NEXT_SIG else -1

    # 1) NEXT_SIG: If there's another bookmark below >>> goto it
    # 1) PREV_SIG: If there's another bookmark above >>> goto it
    if not done:
        sig_rows = _get_signet_rows(v)
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
            sig_rows = _get_signet_rows(vv)
            if(len(sig_rows) > 0):
                w.focus_view(vv)
                vv.run_command("goto_line", {"line": sig_rows[array_end] + 1})
                done = True
            else:
                view_index += incr

    # 3) NEXT_SIG: Else if there is a signet file in the project that is not open >>> open it, focus tab, goto first signet
    # 3) PREV_SIG: Else if there is a signet file in the project that is not open >>> open it, focus tab, goto last signet
    if not done:
        sig_files = []
        sproj = sbot_project.get_project(v)
        if sproj is not None:
            for sig_fn, sig_rows in sproj.signets.items():
                if w.find_open_file(sig_fn) is None and os.path.exists(sig_fn) and len(sig_rows) > 0:
                    vv = w.open_file(sig_fn)
                    sublime.set_timeout(lambda: wait_load_file(vv, sig_rows[array_end]), 10) # already 1-based in file
                    w.focus_view(vv)
                    done = True
                    break

    # 4) NEXT_SIG: Else >>> find first tab/file with signets, focus tab, goto first signet
    # 4) PREV_SIG: Else >>> find last tab/file with signets, focus tab, goto last signet
    if not done:
        view_index = 0 if dir == NEXT_SIG else len(w.views()) - 1
        while not done and ((dir == NEXT_SIG and view_index < len(w.views()) or (dir == PREV_SIG and view_index >= 0))):
            vv = w.views()[view_index]
            sig_rows = _get_signet_rows(vv)
            if(len(sig_rows) > 0):
                w.focus_view(vv)
                vv.run_command("goto_line", {"line": sig_rows[array_end] + 1})
                done = True
            else:
                view_index += incr


#-----------------------------------------------------------------------------------
def _get_signet_rows(view):
    ''' Get all the signet row numbers in the view. Returns a sorted list. '''
    
    sig_rows = []
    for reg in view.get_regions(SIGNET_REGION_NAME):
        row, _ = view.rowcol(reg.a)
        sig_rows.append(row)
    sig_rows.sort()
    return sig_rows


#-----------------------------------------------------------------------------------
def _toggle_signet(view, rows, sel_row=-1):
    if sel_row != -1:
        # Is there one currently at the selected row?
        existing = sel_row in rows
        if existing:
            rows.remove(sel_row)
        else:
            rows.append(sel_row)

    # Update internal.
    sproj = sbot_project.get_project(view)
    if sproj is not None:
        if len(rows) > 0:
            sproj.signets[view.file_name()] = rows
        elif view.file_name() in sproj.signets:
            del sproj.signets[view.file_name()]

    # Update visual signets, brutally. This is the ST way.
    regions = []
    for r in rows:
        pt = view.text_point(r, 0) # 0-based
        regions.append(sublime.Region(pt, pt))
    view.add_regions(SIGNET_REGION_NAME, regions, sbot_common.settings.get('signet_scope', 'comment'), SIGNET_ICON)
