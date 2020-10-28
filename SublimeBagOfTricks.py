import os
import re
import textwrap
import math
import json
import webbrowser
import logging
from html import escape
import time
import traceback
import subprocess
import tempfile
import sublime
import sublime_plugin


# ====== Defs ========
HIGHLIGHT_REGION_NAME = 'highlight_%s'
MAX_HIGHLIGHTS = 6
SIGNET_REGION_NAME = 'signet'
# SIGNET_ICON = 'bookmark'
SIGNET_ICON = 'Packages/Theme - Default/common/label.png'
SBOT_PROJECT_EXT = '.sbot-project'
NEXT_SIG = 1
PREV_SIG = 2

# ====== Vars - global for all open Windows (not Views!) ====
settings = None
sbot_projects = {} # {k:window_id v:SbotProject}


# =========================================================================
# ====================== System stuff =====================================
# =========================================================================


#-----------------------------------------------------------------------------------
class ViewEvent(sublime_plugin.ViewEventListener):
    ''' Listener. '''

    def on_activated(self):
        ''' When focus/tab received. '''
        # _dump_view('ViewEventListener.on_activated', self.view)
        _load_project_maybe(self.view)

    def on_deactivated(self):
        ''' When focus/tab lost. Save to file. Also crude, but on_close is not reliable so we take the conservative approach. (ST4 has on_pre_save_project()) '''
        # _dump_view('EventListener.on_deactivated', self.view)
        sproj = _get_project(self.view)
        if sproj is not None:
            # Save the project file internal to persisted.
            sproj.save()

    def on_selection_modified(self):
        ''' Show the abs position in the status bar for debugging. '''
        pos = self.view.sel()[0].begin()
        self.view.set_status("position", 'Pos {}'.format(pos))


#-----------------------------------------------------------------------------------
class SbotTestTestTestCommand(sublime_plugin.TextCommand):

    def run(self, edit, all=False):
        # _save_sbot_projects()
        v = self.view
        w = self.view.window()
        # for sheet in w.sheets():
        #     print('sheet:', sheet)
        # for view in w.views(): # These are in order L -> R.
        #     print('active view:', w.get_view_index(view), view.file_name()) # (group, index)
        # _get_project(v).dump() # These are not ordered like file.

        image = r'file://C:\Users\cepth\AppData\Roaming\Sublime Text 3\Packages\SublimeBagOfTricks\test\mark1.bmp'
        html = '<body><p>Hello!</p><img src="' + image + '" width="90" height="145"></body>'

        self.phantset = sublime.PhantomSet(v, "test")
        phant = sublime.Phantom(v.sel()[0], html, sublime.LAYOUT_BLOCK)
        phants = []
        phants.append(phant)
        self.phantset.update(phants)

#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. '''
    global settings
    settings = sublime.load_settings('SublimeBagOfTricks.sublime-settings')

    # Init logging.
    ddir = r'{0}\SublimeBagOfTricks'.format(sublime.packages_path())
    logf = ddir + r'\sbot_log.txt'
    logformat = "%(asctime)s %(levelname)8s <%(name)s> %(message)s"
    logging.basicConfig(filename=logf, filemode='w', format=logformat, level=logging.INFO) ### mode a/w
    logging.info("=============================== log start =========================================================");
    logging.info("ddir:" + ddir);


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    logging.info("plugin_unloaded()");
    # just in case...
    for id in list(sbot_projects):
        sbot_projects[id].save()

    
# =========================================================================
# ====================== SbotProject ======================================
# =========================================================================

#-----------------------------------------------------------------------------------
class SbotProject(object):
    ''' Container for project info. Converts persisted to/from internal. TODOC refactor all when ST4? '''

    def __init__(self, project_fn):
        self.fn = project_fn.replace('.sublime-project', SBOT_PROJECT_EXT)

        # Need this because ST window/view lifecycle is unreliable.
        self.views_inited = set()

        # Unpack persisted data into our internal convenience collections.
        self.signets = {}  # k:filename v:[rows]  0-based (like ST)
        self.highlights = {}  # k:filename v:[tokens]  tokens = {"token": "abc", "whole_word": true, "scope": "comment"}

        try:
            with open(self.fn, 'r') as fp:
                values = json.load(fp)

                if 'signets' in values:
                    for sig in values['signets']:
                        if os.path.exists(sig['filename']): # sanity check
                            self.signets[sig['filename']] = sig['rows']

                if 'highlights' in values:
                    for hl in values['highlights']:
                        if os.path.exists(sig['filename']): # sanity check
                            self.highlights[hl['filename']] = hl['tokens']

        except FileNotFoundError as e:
            # Assumes new file.
            sublime.status_message('Creating new sbot project file')

        except:
            s = 'bad thing!' + traceback.format_exc()
            sublime.error_message(s)

    def save(self):
        try:
            sigs = []
            hls = []
            values = {}

            # Persist our internal convenience collections as json.
            for filename, rows in self.signets.items():
                if len(rows) > 0:
                    if filename is not None and os.path.exists(filename): # sanity check
                        sigs.append({'filename': filename, 'rows': rows})
                values['signets'] = sigs

            for filename, tokens in self.highlights.items():
                if len(tokens) > 0:
                    if filename is not None and os.path.exists(filename): # sanity check
                        hls.append({'filename': filename, 'tokens': tokens})
                values['highlights'] = hls

            with open(self.fn, 'w') as fp:
                json.dump(values, fp, indent=4)

        except:
            s = 'bad thing!' + traceback.format_exc()
            sublime.error_message(s)


#-----------------------------------------------------------------------------------
def _get_project(view):
    ''' Get the sbot project for the view. None if invalid. '''
    sproj = None
    id = view.window().id()
    if id in sbot_projects:
        sproj = sbot_projects[id]
    return sproj


#-----------------------------------------------------------------------------------
def _load_project_maybe(v):
    ''' This is kind of crude but there is no project loaded event (ST4 has on_load_project() though...) '''
    sproj = None
    global sbot_projects
    id = v.window().id()

    # Persisted to internal. Check for already loaded.
    if not id in sbot_projects:
        fn = v.window().project_file_name()
        # Load the project file.
        sproj = SbotProject(fn)
        sbot_projects[id] = sproj
    else:
        sproj = sbot_projects[id]

    # If this is the first time through and project has signets and/or highlights for this file, get them all.
    if v.id() not in sproj.views_inited:
        sproj.views_inited.add(v.id())

        # Process signets internal to visual.
        if v.file_name() in sproj.signets:
            _toggle_signet(v, sproj.signets.get(v.file_name(), []))

        # Process highlights internal to visual.
        if v.file_name() in sproj.highlights:
            for tok in sproj.highlights.get(v.file_name(), {}):
                _highlight_view(v, tok['token'], tok['whole_word'], tok['scope'])


# =========================================================================
# ====================== SideBarStuff =====================================
# =========================================================================

#-----------------------------------------------------------------------------------
class SbotSbCopyNameCommand(sublime_plugin.WindowCommand):

    def run(self, paths):
        names = (os.path.split(path)[1] for path in paths)
        sublime.set_clipboard('\n'.join(names))


#-----------------------------------------------------------------------------------
class SbotSbCopyPathCommand(sublime_plugin.WindowCommand):

    def run(self, paths):
        sublime.set_clipboard('\n'.join(paths))


#-----------------------------------------------------------------------------------
class SbotSbTerminalCommand(sublime_plugin.WindowCommand):

    def run(self, paths):
        if len(paths) > 0:
            dir = paths[0] if os.path.isdir(paths[0]) else os.path.split(paths[0])[0]
            subprocess.call(['wt', '-d', dir])


#-----------------------------------------------------------------------------------
class SbotSbTreeCommand(sublime_plugin.WindowCommand):

    def run(self, paths):
        if len(paths) > 0:
            dir = paths[0] if os.path.isdir(paths[0]) else os.path.split(paths[0])[0]
            subprocess.call(['tree', dir, '/a', '/f', '|', 'clip'], shell=True)


#-----------------------------------------------------------------------------------
class SbotSbOpenBrowserCommand(sublime_plugin.WindowCommand):

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


# =========================================================================
# ====================== Signets ==========================================
# =========================================================================

#-----------------------------------------------------------------------------------
class SbotToggleSignetCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        v = self.view
        # Get current row.
        sel_row, _ = v.rowcol(v.sel()[0].a)
        _toggle_signet(v, _get_signet_rows(v), sel_row)


#-----------------------------------------------------------------------------------
def _go_to_signet(view, dir):
    ''' Navigate to signet in whole collection. dir is NEXT_SIG or PREV_SIG. '''
    v = view
    w = view.window()
    signet_nav_files = settings.get('signet_nav_files', True)

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
        sproj = _get_project(v)
        if sproj is not None:
            for sig_fn, sig_rows in sproj.signets.items():
                if w.find_open_file(sig_fn) is None and os.path.exists(sig_fn) and len(sig_rows) > 0:
                    vv = w.open_file(sig_fn)
                    sublime.set_timeout(lambda: _wait_load_file(vv, sig_rows[array_end]), 10) # already 1-based in file
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
        sproj = _get_project(self.view)
        if sproj is not None:
            sproj.signets.clear()

        # Clear visuals in open views.
        for vv in self.view.window().views():
            vv.erase_regions(SIGNET_REGION_NAME)


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
    sproj = _get_project(view)
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
    view.add_regions(SIGNET_REGION_NAME, regions, settings.get('signet_scope', 'comment'), SIGNET_ICON)


# =========================================================================
# ====================== Rendering ========================================
# =========================================================================

#-----------------------------------------------------------------------------------
class SbotRenderToHtmlCommand(sublime_plugin.TextCommand):
    ''' Make a pretty. '''
    def run(self, edit):
        v = self.view
        sproj = _get_project(v)

        ## Get prefs.
        html_font_size = settings.get('html_font_size', 12)
        html_font_face = settings.get('html_font_face', 'Arial')
        html_background = settings.get('html_background', 'white')
        html_line_numbers = settings.get('html_line_numbers', True)
        render_max_file = settings.get('render_max_file', 1)

        fsize = v.size() / 1024.0 / 1024.0

        if fsize > render_max_file:
            sublime.message_dialog('File too large to render. If you really want to, change your settings')
            return

        # Use tuples for everything as they can be hashable keys.
        # my_style = (foreground, background, bold, italic)

        ## Collect scope/style info.
        all_styles = {} # k:style v:id
        region_styles = [] # One [(Region, style)] per line
        highlight_regions = [] # (Region, style))


        ### Local helpers.
        def _add_style(style):
            # Add style to our collection.
            if style not in all_styles:
                all_styles[style] = len(all_styles)

        def _get_style(style):
                # Locate the style and return the id.
                return all_styles.get(style, -1)

        def _view_style_to_tuple(view_style):
            # print(view_style)
            tt = (view_style['foreground'], view_style.get('background', None), view_style.get('bold', False), view_style.get('italic', False))
            return tt

        v.set_status('render', 'Render setting up')

        ## If there are highlights, collect them.
        highlight_scopes = settings.get('highlight_scopes')
        num_highlights = min(len(highlight_scopes), MAX_HIGHLIGHTS)
        for i in range(num_highlights):

            # Get the style and invert for highlights.
            scope = highlight_scopes[i]
            ss = v.style_for_scope(scope)
            background = ss['background'] if 'background' in ss else ss['foreground']
            foreground = html_background
            hl_style = (foreground, background, False, False)
            _add_style(hl_style)

            # Collect the highlight regions.
            reg_name = HIGHLIGHT_REGION_NAME % highlight_scopes[i]
            for region in v.get_regions(reg_name):
                highlight_regions.append((region, hl_style))

        # Put all in order.
        highlight_regions.sort(key=lambda v: v[0].a)

        ## Tokenize selection by syntax scope.
        has_selection = len(v.sel()[0]) > 0
        sel_reg = v.sel()[0] if has_selection else sublime.Region(0, v.size())

        pc = SbotPerfCounter('render_html')

        rows, _ = v.rowcol(v.size() - 1)
        row_num = 0

        # TODOC Kind of slow: ~1 msec per line
        for line_region in v.split_by_newlines(sel_reg):
            pc.start()
            self.view.set_status('render', 'Render {} of {}'.format(row_num, rows))
            row_num += 1
            
            line_styles = [] # (Region, style))

            # Start a new line.
            current_style = None
            # new_style = None
            current_style_start = line_region.a # current chunk

            # Process the individual line chars.
            point = line_region.a

            while point < line_region.b:
                # Check if it's a highlight first as they take precedence.
                if len(highlight_regions) > 0 and point >= highlight_regions[0][0].a:

                    # Start a highlight.
                    new_style =  highlight_regions[0][1]

                    # Save last maybe.
                    if point > current_style_start:
                        line_styles.append((sublime.Region(current_style_start, point), current_style))

                    # Save highlight info.
                    line_styles.append((highlight_regions[0][0], new_style))

                    _add_style(new_style)

                    # Bump ahead.
                    point = highlight_regions[0][0].b
                    current_style = new_style
                    current_style_start = point

                    del highlight_regions[0]

                else:
                    # Plain ordinary style. Did it change?
                    new_style = _view_style_to_tuple(v.style_for_scope(v.scope_name(point)))

                    if new_style != current_style:

                        # Save last maybe.
                        if point > current_style_start:
                            line_styles.append((sublime.Region(current_style_start, point), current_style))

                        current_style = new_style
                        current_style_start = point

                        _add_style(new_style)

                    # Bump ahead.
                    point += 1

            # Done. Save last maybe.
            if point > current_style_start:
                line_styles.append((sublime.Region(current_style_start, point), current_style))

            # Add to master list.
            region_styles.append(line_styles)

        # Done loop.
        pc.stop()
        logging.info('loop:' + pc.dump())

        ## Create css.
        style_text = ""
        # print('all_styles', all_styles)
        for style, id in all_styles.items():
            props = '{{ color:{}; '.format(style[0])
            if style[1] is not None:
                props += 'background-color:{}; '.format(style[1])
            if style[2]:
                props += 'font-weight:bold; '
            if style[3]:
                props += 'font-style:italic; '
            props += '}'
            style_text += '.st{} {}\n'.format(id, props)

        ## Content text.
        content = []
        line_num = 1

        ii = 0

        ## Iterate collected lines.
        gutter_size = math.ceil(math.log(len(region_styles), 10))
        padding = 1.4 + gutter_size * 0.5

        for line_styles in region_styles:
            if html_line_numbers:
                content.append("<p>{:0{size}}  ".format(line_num, size=gutter_size))
            else:
                content.append("<p>")

            for region, style in line_styles:
                #[(Region, style(ref))]
                text = v.substr(region)

                # Locate the style.
                id = _get_style(style)
                if id >= 0:
                    content.append('<span class=st{}>{}</span>'.format(id, escape(text)))
                else:
                    content.append(text) # plain text

            # Done line.
            content.append('</p>\n')
            line_num += 1

        ## Output html. Lang tag? <html lang="en">
        html1 = textwrap.dedent('''
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">
            <style  type="text/css">
            .contentpane {{
              font-family: {};
              font-size: {}em;
              background-color: {};
              text-indent: -{}em;
              padding-left: {}em;
            }}
            p {{
              white-space:pre-wrap;
              margin: 0em;
            }}
            '''.format(html_font_face, html_font_size / 16, html_background, padding, padding)) # em

        html2 = textwrap.dedent('''
            </style>
            </head>
            <body>
            <div class="container">
            <div class="contentpane">
            ''')

        html3 = textwrap.dedent('''
            </div>
            </div>
            </body>
            </html>
            ''')

        _output_html(edit, v, [html1, style_text, html2, "".join(content), html3])


#-----------------------------------------------------------------------------------
class SbotRenderMarkdownCommand(sublime_plugin.TextCommand):
    ''' Turn md into html.'''

    def is_visible(self):
        v = self.view
        vis = False
        fn = v.file_name()
        if fn is not None:
            vis = v.file_name().endswith('.md')
        return vis

    def run(self, edit):
        v = self.view
        ##### Get prefs.
        md_background = settings.get('md_background', 'white')
        md_font_size = settings.get('md_font_size', 12)
        md_font_face = settings.get('md_font_face', 'Arial')

        html = []
        html.append("<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
        html.append("<style>body {{ background-color:{}; font-family:{}; font-size:{}; }}".format(md_background, md_font_face, md_font_size))
        html.append("</style></head><body>")

        html.append(v.substr(sublime.Region(0, v.size())))

        html.append("<!-- Markdeep: --><style class=\"fallback\">body{visibility:hidden;white-space:pre;font-family:monospace}</style><script src=\"markdeep.min.js\" charset=\"utf-8\"></script><script src=\"https://casual-effects.com/markdeep/latest/markdeep.min.js\" charset=\"utf-8\"></script><script>window.alreadyProcessedMarkdeep||(document.body.style.visibility=\"visible\")</script>")
        html.append("</body></html>")

        content = '\n'.join(html)

        _output_html(edit, v, content)


#-----------------------------------------------------------------------------------
def _output_html(edit, view, content=[]):
    output_type = settings.get('render_output', 'new_file')

    if output_type == 'clipboard':
        sublime.set_clipboard("".join(content))

    elif output_type == 'new_file':
        new_view = sublime.active_window().new_file()
        new_view.set_syntax_file('Packages/HTML/HTML.tmLanguage')
        new_view.insert(edit, 0, "".join(content))

    elif output_type == 'default_file' or output_type == 'default_file_open':
        if view.file_name() is None:
            sublime.error_message("Can't use render_output=default_file for unnamed files")
        else:
            hfile = view.file_name() + '.html'
            with open(hfile, 'w') as f:
                f.write("".join(content))
                if output_type == 'default_file_open':
                    webbrowser.open_new_tab(hfile)


# =========================================================================
# ====================== Highlighting =====================================
# =========================================================================

#-----------------------------------------------------------------------------------
class SbotHighlightTextCommand(sublime_plugin.TextCommand):
    ''' Highlight specific words using scopes. Parts borrowed from StyleToken.
    Persistence supported via sbot-project container.

    Note: Regions added by v.add_regions() can not set the foreground color. The scope color is used
    for the region background color. Also they are not available via extract_scope().
    '''

    def run(self, edit, hl_index):
        v = self.view

        # Prefs.
        highlight_scopes = settings.get('highlight_scopes')

        # Get whole word or specific span.
        region = v.sel()[0]

        whole_word = region.empty()
        if whole_word:
            region = v.word(region)
        token = v.substr(region)

        num_highlights = min(len(highlight_scopes), MAX_HIGHLIGHTS)
        hl_index = min(hl_index, num_highlights)

        scope = highlight_scopes[hl_index]

        _highlight_view(v, token, whole_word, scope)

        # Add to internal.
        sproj = _get_project(v)
        if v.file_name() not in sproj.highlights:
            sproj.highlights[v.file_name()] = []
        sproj.highlights[v.file_name()].append( { "token": token, "whole_word": whole_word, "scope": scope } )


#-----------------------------------------------------------------------------------
class SbotClearHighlightCommand(sublime_plugin.TextCommand):
    ''' Clear all marks where the cursor is. '''

    def run(self, edit):
        # Locate specific region, crudely.
        v = self.view
        sproj = _get_project(v)
        highlight_scopes = settings.get('highlight_scopes')
        num_highlights = min(len(highlight_scopes), MAX_HIGHLIGHTS)

        point = v.sel()[0].a

        highlight_scope = ''

        for i in range(num_highlights):
            reg_name = HIGHLIGHT_REGION_NAME % highlight_scopes[i]
            for region in v.get_regions(reg_name):
                if region.contains(point):
                    highlight_scope = highlight_scopes[i]
                    v.erase_regions(reg_name)

                    # Remove from internal.
                    if v.file_name() in sproj.highlights:
                        for i in range(len(sproj.highlights[v.file_name()])):
                            if sproj.highlights[v.file_name()][i]['scope'] == highlight_scope:
                                del sproj.highlights[v.file_name()][i]
                                break;
                    break;


#-----------------------------------------------------------------------------------
class SbotClearAllHighlightsCommand(sublime_plugin.TextCommand):
    ''' Clear all marks where the cursor is.'''

    def run(self, edit):
        v = self.view
        sproj = _get_project(v)
        highlight_scopes = settings.get('highlight_scopes')
        num_highlights = min(len(highlight_scopes), MAX_HIGHLIGHTS)

        for i in range(num_highlights):
            reg_name = HIGHLIGHT_REGION_NAME % highlight_scopes[i]
            v.erase_regions(reg_name)

        # Remove from internal.
        if v.file_name() in sproj.highlights:
            del sproj.highlights[v.file_name()]


#-----------------------------------------------------------------------------------
class SbotShowScopesCommand(sublime_plugin.TextCommand):
    ''' Show style info for common scopes. List from https://www.sublimetext.com/docs/3/scope_naming.html. '''

    def run(self, edit):
        v = self.view
        style_text = []
        content = []
        scopes = [
            'comment', 'constant', 'constant.character.escape', 'constant.language', 'constant.numeric', 'entity.name',
            'entity.name.section', 'entity.name.tag', 'entity.other', 'invalid', 'invalid.deprecated', 'invalid.illegal',
            'keyword', 'keyword.control', 'keyword.declaration', 'keyword.operator', 'markup', 'punctuation', 'source',
            'storage.modifier', 'storage.type', 'string', 'support', 'text', 'variable', 'variable.function',
            'variable.language', 'variable.parameter']

        for scope in scopes:
            style = v.style_for_scope(scope)
            # print(scope, style)
            props = '{{ color:{}; '.format(style['foreground'])
            props2 = 'fg:{} '.format(style['foreground'])
            if 'background' in style:
                props += 'background-color:{}; '.format(style['background'])
                props2 += 'bg:{} '.format(style['background'])
            if style['bold']:
                props += 'font-weight:bold; '
                props2 += 'bold '
            if style['italic']:
                props += 'font-style:italic; '
                props2 += 'italic '
            props += '}'

            i = len(style_text)
            style_text.append('.st{} {}'.format(i, props))
            content.append('<p><span class=st{}>{}  {}</span></p>'.format(i, scope, props2))

        # Output html.
        html1 = '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<style  type="text/css">\np {\nmargin: 0em;\nfont-family: Consolas;\nfont-size: 1.0em;\nbackground-color: white;\n}\n'
        html2 = '</style>\n</head>\n<body>\n'
        html3 = '</body>\n</html>\n'
        # Could also: sublime.set_clipboard(html1 + '\n'.join(style_text) + html2 + '\n'.join(content) + html3)

        # Do popup
        html = '''
            <body>
                <style>
                    p {{ margin: 0em; }}
                    {}
                </style>
                {}
                {}
            </body>
        '''.format('\n'.join(style_text), '\n'.join(content), html3)

        v.show_popup(html, max_width=512)


#-----------------------------------------------------------------------------------
def _highlight_view(view, token, whole_word, scope):

    escaped = re.escape(token)
    if whole_word and escaped[0].isalnum():
        escaped = r'\b%s\b' % escaped

    highlight_regions = view.find_all(escaped) if whole_word else view.find_all(token, sublime.LITERAL)
    if len(highlight_regions) > 0:
        view.add_regions(HIGHLIGHT_REGION_NAME % scope, highlight_regions, scope)


# =========================================================================
# ====================== Misc commands ====================================
# =========================================================================

#-----------------------------------------------------------------------------------
class SbotSplitViewCommand(sublime_plugin.WindowCommand):
    ''' Toggles betweensplit file in new row.'''

    def run(self):
        lo = self.window.layout()
        w = self.window

        if(len(lo['rows']) > 2):
            # Remove split.
            w.run_command("focus_group", { "group": 1 } )
            w.run_command("close_file")
            w.run_command("set_layout", { "cols": [0.0, 1.0], "rows": [0.0, 1.0], "cells": [[0, 0, 1, 1]] } )
        else:
            # Add split.
            sel_row, _ = w.active_view().rowcol(w.active_view().sel()[0].a) # current sel
            w.run_command("set_layout", { "cols": [0.0, 1.0], "rows": [0.0, 0.5, 1.0], "cells": [[0, 0, 1, 1], [0, 1, 1, 2]] } )
            w.run_command("focus_group", { "group": 0 } )
            w.run_command("clone_file")
            w.run_command("move_to_group", { "group": 1 } )
            w.active_view().run_command("goto_line", {"line": sel_row})


#-----------------------------------------------------------------------------------
class SbotOpenSiteCommand(sublime_plugin.ApplicationCommand):
    ''' Open a web page. '''

    def run(self, url):
        webbrowser.open_new_tab(url)


# =========================================================================
# ====================== Utilities ========================================
# =========================================================================

#-----------------------------------------------------------------------------------
def _dump_view(preamble, view):
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

    logging.info(" ".join(s));
            

#-----------------------------------------------------------------------------------
def _wait_load_file(view, line):
    ''' Open file asynchronously then position at line. '''
    if view.is_loading():
        sublime.set_timeout(lambda: _wait_load_file(view, line), 100) # maybe not forever?
    else: # good to go
        view.run_command("goto_line", {"line": line})


#-----------------------------------------------------------------------------------
class SbotPerfCounter(object):
    ''' Container for perf counter. '''

    def __init__(self, id):
        self.id = id
        self.vals = []
        self.start_time = 0

    def start(self):
        self.start_time = time.perf_counter()

    def stop(self):
        if self.start_time != 0:
            self.vals.append(time.perf_counter() - self.start_time)
            self.start_time = 0

    def dump(self):
        avg = sum(self.vals) / len(self.vals)
        s = self.id + ': '
        if len(self.vals) > 0:
            s += str(avg)
        else:
            s += 'No data'
        return s

    def clear(self):
        self.vals = []


# =========================================================================
# ====================== Holding tank examples ============================
# =========================================================================

#-----------------------------------------------------------------------------------
class SbotExUserInputCommand(sublime_plugin.TextCommand):
    ''' Command: Get input from user. sbot_ex_user_input
    When a command with arguments is called without them, but it defines an input() method, Sublime will call
    the input() method to see if there is an input handler that can be used to gather the arguments instead.
    Every input handler represents an argument to the command, and once the entire chain of them is finished, 
    Sublime re-invokes the command with the arguments that it gathered.
    '''

    def run(self, edit, my_example):
        # print("!!!StptUserInputCommand.run() name:{0} my_example:{1}".format(self.name(), my_example)) # self.name is "sbot_ex_user_input"
        for i in range(len(self.view.sel())):
            sel = self.view.sel()[i]
            data = self.view.substr(sel)
            # print("*** sel:{0} data:{1}".format(sel, data))
            # replace selected text.
            self.view.replace(edit, sel, my_example)

    def input(self, args):
        # print("!!!StptUserInputCommand.input() " + str(args))
        return SbotExInputHandler(self.view)


#-----------------------------------------------------------------------------------
class SbotExGetNumberCommand(sublime_plugin.WindowCommand):
    ''' A window command. sbot_ex_get_number '''

    def run(self):
        # Bottom input area.
        self.window.show_input_panel("Give me a number:", "", self.on_done, None, None)

    def on_done(self, text):
        try:
            line = int(text)
            if self.window.active_view():
                self.window.active_view().run_command("goto_line", {"line": line})
                self.window.active_view().run_command("expand_selection", {"to": "line"})
        except ValueError:
            pass


#-----------------------------------------------------------------------------------
class SbotExMsgBoxCommand(sublime_plugin.TextCommand):
    ''' Command: Simple message box. sbot_ex_msg_box '''

    def run(self, edit, cmd=None):
        # print("MsgBox! {0} {1}".format(self.name(), edit))
        sublime.ok_cancel_dialog("Hi there from StptMsgBoxCommand")


#-----------------------------------------------------------------------------------
class SbotExListSelectCommand(sublime_plugin.TextCommand):
    ''' Command: Select from list. sbot_ex_list_select '''

    def run(self, edit, cmd=None):
        # print("ListSelect! {0} {1}".format(self.name(), edit))
        self.panel_items = ["Duck", "Cat", "Banana"]
        # self.window.show_quick_panel(self.panel_items, self.on_done_panel)
        self.view.window().show_quick_panel(self.panel_items, self.on_done_panel)

    def on_done_panel(self, choice):
        if choice >= 0:
            print("You picked {0}".format(self.panel_items[choice]))
            os.startfile(ddir + r"\test1.txt")


#-----------------------------------------------------------------------------------
class SbotExMenuCommand(sublime_plugin.TextCommand):
    ''' Container for other menu items. sbot_ex_menu '''

    def run(self, edit, cmd=None):
        # Individual menu items.
        CMD1 = {'text': 'UserInput',  'command' : 'sbot_ex_user_input'}
        CMD2 = {'text': 'GetNumber',  'command' : 'sbot_ex_get_number'}
        CMD3 = {'text': 'MsgBox',     'command' : 'sbot_ex_msg_box'}
        CMD4 = {'text': 'ListSelect', 'command' : 'sbot_ex_list_select'}

        menu_items = [CMD1, CMD2, CMD3, CMD4]

        def on_done(index):
            if index >= 0:
                self.view.run_command(menu_items[index]['command'], {'cmd': cmd})

        self.view.window().show_quick_panel([item['text'] for item in menu_items], on_done)


#-----------------------------------------------------------------------------------
class SbotExInputHandler(sublime_plugin.TextInputHandler):
    ''' Generic user input handler. '''

    def __init__(self, view):
        self.view = view

    def placeholder(self):
        return "placeholder - optional"

    def description(self, sdef):
        return "description for SbotExInputHandler"

    def initial_text(self):
        # Check if something selected.
        if len(self.view.sel()) > 0:
            if(self.view.sel()[0].size() == 0):
                return "default initial contents"
            else:
                return self.view.substr(self.view.sel()[0])
        else:
            return "wtf?"

    def preview(self, my_example):
        # Optional peek at current value.
        # print("SbotExInputHandler.preview() name:{0} my_example:{1}".format(self.name(), my_example))
        return my_example

    def validate(self, my_example):
        # Is it ok?
        # print("SbotExInputHandler.validate() name:{0} my_example:{1}".format(self.name(), my_example))
        return True
