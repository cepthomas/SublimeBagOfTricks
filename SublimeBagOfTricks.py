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
import sublime
import sublime_plugin



# ====== Defs ========
HIGHLIGHT_REGION_NAME = 'highlight_%s'
MAX_HIGHLIGHTS = 6
SIGNET_REGION_NAME = 'signet'
WHITESPACE = '_ws'
SIGNET_ICON = 'bookmark'  # 'Packages/Theme - Default/common/label.png'
SBOT_PROJECT_EXT = '.sbot-project'
NEXT_SIG = 1
PREV_SIG = 2

# ====== Vars - global across all Windows ====
settings = None
sbot_projects = {} # k:window_id v:SbotProject


# =========================================================================
# ====================== System stuff =====================================
# =========================================================================

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

        vals = []
        for i in range(100):
            start = time.perf_counter()
            selreg = sublime.Region(0, v.size())
            for line_region in v.split_by_newlines(selreg):
                pass
            # for s in v.substr(selreg):
            #     pass
            vals.append(time.perf_counter() - start)
        print('split_by_newlines', sum(vals) / len(vals))


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module stuff. '''
    global settings
    settings = sublime.load_settings('SublimeBagOfTricks.sublime-settings')

    # Init logging.
    ddir = r'{0}\SublimeBagOfTricks'.format(sublime.packages_path())
    logf = ddir + r'\sbot_log.txt'
    logformat = "%(asctime)s %(levelname)8s <%(name)s> %(message)s"
    logging.basicConfig(filename=logf, filemode='w', format=logformat, level=logging.INFO) ### mode a/w
    logging.info("=============================== log start =========================================================");
    logging.info("ddir:" + ddir);


# =========================================================================
# ====================== SbotProject ======================================
# =========================================================================

#-----------------------------------------------------------------------------------
class SbotProject(object):
    ''' Container for persistence. '''

    def __init__(self, project_fn):
        self.fn = project_fn.replace('.sublime-project', SBOT_PROJECT_EXT)

        # Need this because ST window/view lifecycle is unreliable.
        self.views_inited = set()

        # Unpack into our convenience collections.
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
            highlights = []
            values = {}

            for filename, rows in self.signets.items():
                if len(rows) > 0:
                    sigs.append({'filename': filename, 'rows': rows})
            values['signets'] = sigs

            for filename, tokens in self.highlights.items():
                if len(tokens) > 0:
                    highlights.append({'filename': filename, 'tokens': tokens})
            values['highlights'] = highlights

            with open(self.fn, 'w') as fp:
                json.dump(values, fp, indent=4)

        except:
            s = 'bad thing!' + traceback.format_exc()
            sublime.error_message(s)


#-----------------------------------------------------------------------------------
def _save_sbot_projects():
    ''' Save all projects to file. '''
    for id in list(sbot_projects):
        sbot_projects[id].save()


#-----------------------------------------------------------------------------------
def _get_project(view):
    ''' Get the sbot project for the view. None if invalid. '''
    sproj = None
    id = view.window().id()
    if id in sbot_projects:
        sproj = sbot_projects[id]
    return sproj


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


# =========================================================================
# ====================== EventListeners ===================================
# =========================================================================

#-----------------------------------------------------------------------------------
class ViewEvent(sublime_plugin.ViewEventListener):
    ''' Listener. '''

    def on_activated(self):
        ''' When focus/tab received. '''
        v = self.view
        _dump_view('ViewEventListener.on_activated', v)

        # This is kind of crude but there is no project_loaded event (ST4 does though...)
        sproj = None
        global sbot_projects
        id = v.window().id()

        # Check for already loaded.
        if not id in sbot_projects:
            fn = v.window().project_file_name()
            # Load the project file.
            sproj = SbotProject(fn)
            sbot_projects[id] = sproj
        else:
            sproj = sbot_projects[id]

        # If this is the first time through and project has signets and/or highlights for this file, set them all.
        if v.id() not in sproj.views_inited:

            # Process signets.
            if v.file_name() in sproj.signets:
                _toggle_signet(v, sproj.signets.get(v.file_name(), []))

            # Process highlights.
            if v.file_name() in sproj.highlights:
                for tok in sproj.highlights.get(v.file_name(), {}):
                    _highlight_one(v, tok['token'], tok['whole_word'], tok['scope'])

    def on_deactivated(self):
        ''' When focus/tab lost. '''
        # Save to file. Also crude, but on_close is not reliable so we take the conservative approach. (Fixed in ST4)
        v = self.view
        # _dump_view('EventListener.on_deactivated', v)
        sbot_project = _get_project(v)

        if sbot_project is not None:
            # Gather signets.
            sig_rows = []

            for row in _get_signet_rows(v):
                sig_rows.append(row)
                # sig_rows.append(row + 1) # Adjust to 1-based

            if len(sig_rows) > 0:
                sbot_project.signets[v.file_name()] = sig_rows
            elif v.file_name() in sbot_project.signets:
                del sbot_project.signets[v.file_name()]

            # Save the project file.
            sbot_project.save()


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
def move_to_signet(view, dir):
    ''' Navigate to signet in whole collection. dir is NEXT_SIG or PREV_SIG. '''
    v = view
    w = view.window()
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
        move_to_signet(self.view, NEXT_SIG)


#-----------------------------------------------------------------------------------
class SbotPreviousSignetCommand(sublime_plugin.TextCommand):
    ''' Navigate to signet in whole collection. '''

    def run(self, edit):
        move_to_signet(self.view, PREV_SIG)


#-----------------------------------------------------------------------------------
class SbotClearSignetsCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        sproj = _get_project(self.view)
        # clear persistence
        if sproj is not None:
            sproj.signets.clear()
        # clear visual
        for vv in self.view.window().views():
            vv.erase_regions(SIGNET_REGION_NAME)


#-----------------------------------------------------------------------------------
def _get_signet_rows(view):
    ''' Get all the signet row numbers in the view. Returns a sorted list. '''
    # Current signets in this view. 0-based.
    sig_rows = []
    for reg in view.get_regions('signet'):
        row, _ = view.rowcol(reg.a)
        sig_rows.append(row)
    sig_rows.sort()
    return sig_rows


#-----------------------------------------------------------------------------------
def _toggle_signet(view, rows, sel_row=-1):
    signet_rows = []

    if sel_row != -1:
        # Is there one there?
        existing = False
        for row in rows:
            if sel_row == row:
                existing = True
            else:
                signet_rows.append(row)

        if not existing:
            signet_rows.append(sel_row)
    else:
        signet_rows = rows

    # Update visual signets, brutally.
    regions = []
    for r in signet_rows:
        pt = view.text_point(r, 0) # 0-based
        regions.append(sublime.Region(pt, pt))

    view.add_regions(SIGNET_REGION_NAME, regions, settings.get('signet_scope', 'comment'), SIGNET_ICON)


# =========================================================================
# ====================== Rendering ========================================
# =========================================================================



#-----------------------------------------------------------------------------------
class SbotRenderTextCommand(sublime_plugin.TextCommand): #TODOC consolidate adjacent styles when separated only by ws.

    def run(self, edit):
        v = self.view
        sproj = _get_project(v)

        ## Get prefs.
        html_font_size = settings.get('html_font_size', 12)
        html_font_face = settings.get('html_font_face', 'Arial')
        html_plain_text = settings.get('html_plain_text', '#000000')
        html_background = settings.get('html_background', 'transparent')
        html_line_numbers = settings.get('html_line_numbers', True)

        ## Collect scope/style info.
        all_scopes = set() # All unique values
        scope_tokens = [] # One [(Region, scope)] per line
        highlight_regions = [] # (Region, scope)

        ## Html style info.
        css1 = dict() # {selector:properties}
        css2 = dict() # {properties:selector}
        style_map = dict() # {scope:selector}

        ## If there are highlights, collect them.
        if v.file_name() in sproj.highlights:
            highlight_scopes = settings.get('highlight_scopes')
            num_highlights = min(len(highlight_scopes), MAX_HIGHLIGHTS)
            for i in range(num_highlights):
                reg_name = HIGHLIGHT_REGION_NAME % highlight_scopes[i]
                for region in v.get_regions(reg_name):
                    highlight_regions.append((region, highlight_scopes[i] + '.highlight')) # discriminate for post-processing

            highlight_regions.sort(key=lambda v: v[0].a)
            # print('highlight_regions', highlight_regions)
            # [((11381, 11384), 'constant.language'), ((11728, 11731), 'constant.language'), ((11750, 11753), 'constant.language'), ((17840, 17849), 'markup.list'), 

        ## Tokenize whole file by syntax scope.
        has_selection = len(v.sel()[0]) > 0
        selreg = v.sel()[0] if has_selection else sublime.Region(0, v.size())
        
        for line_region in v.split_by_newlines(selreg): # s.splitlines() seems to be about 3x faster but would double memory use.
            # line_num += 1
            line_tokens = [] # (Region, scope)

            # Process the line chars.
            current_scope = ""
            new_scope = ""
            current_scope_start = line_region.a # current chunk

            for point in range(line_region.a, line_region.b + 1):

                # # Check highlights first
                # if len(highlight_regions) > 0:
                #     if point >= highlight_regions[0].a:
                #         # In a highlight.
                #         if point > current_scope_start:
                #             # Save old.
                #             line_tokens.append((sublime.Region(current_scope_start, point), current_scope))
                #         current_scope = new_scope
                #         current_scope_start = point
                #         all_scopes.add(new_scope)
                #     else:
                #         pass



                # Get new scope. Check if it's ws.
                new_scope = WHITESPACE if v.substr(point).isspace() else v.scope_name(point)

                # Check for scope change.
                if new_scope != current_scope:
                    if point > current_scope_start:
                        # Save old.
                        line_tokens.append((sublime.Region(current_scope_start, point), current_scope))
                    current_scope = new_scope
                    current_scope_start = point
                    all_scopes.add(new_scope)

            # Save last.
            if point > current_scope_start:
                line_tokens.append((sublime.Region(current_scope_start, line_region.b), current_scope))

            scope_tokens.append(line_tokens)

        ## Fix up styles and output css.
        for scope in all_scopes:
            if scope == WHITESPACE:
                pass # Ignore, treat as plain text.
            else:
                style = v.style_for_scope(scope)
                # Check for plain text, ignore style.
                if style['foreground'] == html_plain_text and style['bold'] == False and style['italic'] == False:
                    pass 
                else:
                    # Legit style.
                    props = '{{ color:{}; '.format(style['foreground'])
                    if 'background' in style:
                        props += 'background-color:{}; '.format(style['background'])
                    if style['bold']:
                        props += 'font-weight:bold; '
                    if style['italic']:
                        props += 'font-style:italic; '
                    props += '}'

                    if props in css2:
                        style_map[scope] = css2[props]
                    else:
                        sel = 'st{}'.format(len(css1))
                        css1[sel] = props
                        css2[props] = sel
                        style_map[scope] = sel

        ## Highlight styles. They are handled differently.
        highlight_scopes = settings.get('highlight_scopes')
        num_highlights = min(len(highlight_scopes), MAX_HIGHLIGHTS)

        for i in range(num_highlights):
            # style_for_scope(scope_name) dict    Accepts a string scope name and returns a dict of style information,
            # include the keys foreground, bold, italic, source_line, source_column and source_file. 
            # If the scope has a background color set, the key background will be present. 
            # The foreground and background colors are normalized to the six character hex form with a leading hash, e.g. #ff0000.
            scope = highlight_scopes[i]
            ss = v.style_for_scope(scope)

            # Swapsies.
            background = ss['background'] if 'background' in ss else ss['foreground']
            props = '{{ color:{}; background-color:{}; }}'.format(html_background, background)

            # Fix name.
            scope += '.highlight'

            if props in css2:
                style_map[scope] = css2[props]
            else:
                sel = 'st{}'.format(len(css1))
                css1[sel] = props
                css2[props] = sel
                style_map[scope] = sel

        ## Create css.
        style_text = ""
        for k in css1.keys():
            style_text += '.{} {}\n'.format(k, css1[k])

        ## Content text.
        content = []
        line_num = 1

        ## Iterate collected lines.
        gutter_size = math.ceil(math.log(len(scope_tokens), 10))
        padding = 1.4 + gutter_size * 0.5

        for line_tokens in scope_tokens:
            if html_line_numbers:
                content.append("<p>{:0{size}}  ".format(line_num, size=gutter_size))
            else:
                content.append("<p>")

            for region, scope in line_tokens:
                #[(Region, scope)]
                text = v.substr(region)

                if scope == WHITESPACE:
                    content.append(text) # plain text
                elif scope in style_map:
                    content.append('<span class={}>{}</span>'.format(style_map[scope], escape(text)))
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
        html_background = settings.get('md_background', 'transparent')
        html_font_size = settings.get('md_font_size', 12)
        html_font_face = settings.get('md_font_face', 'Arial')

        html = []
        html.append("<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
        html.append("<style>body {{ background-color:{}; font-family:{}; font-size:{}; }}".format(html_background, html_font_face, html_font_size))
        html.append("</style></head><body>")

        html.append(v.substr(sublime.Region(0, v.size())))

        html.append("<!-- Markdeep: --><style class=\"fallback\">body{visibility:hidden;white-space:pre;font-family:monospace}</style><script src=\"markdeep.min.js\" charset=\"utf-8\"></script><script src=\"https://casual-effects.com/markdeep/latest/markdeep.min.js\" charset=\"utf-8\"></script><script>window.alreadyProcessedMarkdeep||(document.body.style.visibility=\"visible\")</script>")
        html.append("</body></html>")

        content = '\n'.join(html)

        _output_html(edit, v, content)


#-----------------------------------------------------------------------------------
def _output_html(edit, view, content=[]):
    output_type = settings.get('html_output', 'new_file')

    if output_type == 'clipboard':
        sublime.set_clipboard("".join(content))

    elif output_type == 'new_file':
        new_view = sublime.active_window().new_file()
        new_view.set_syntax_file('Packages/HTML/HTML.tmLanguage')
        new_view.insert(edit, 0, "".join(content))

    elif output_type == 'default_file' or output_type == 'default_file_open':
        if view.file_name() is None:
            sublime.error_message("Can't use html_output=default_file for unnamed files")
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

        # Get whole word or specific span.
        region = v.sel()[0]
        whole_word = region.empty()
        if whole_word:
            region = v.word(region)
        token = v.substr(region)

        highlight_scopes = settings.get('highlight_scopes')
        num_highlights = min(len(highlight_scopes), MAX_HIGHLIGHTS)
        hl_index = min(hl_index, num_highlights)

        scope = highlight_scopes[hl_index]

        _highlight_one(v, token, whole_word, scope)

        # Add to persistence.
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

        for i in range(num_highlights):
            reg_name = HIGHLIGHT_REGION_NAME % highlight_scopes[i]
            for region in v.get_regions(reg_name):
                if region.contains(point):
                    v.erase_regions(reg_name)
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

        # Remove from persistence.
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
            'comment', 'constant', 'constant.character.escape', 'constant.language', 'constant.numeric', 'entity.name', 'entity.name.section',
            'entity.name.tag', 'entity.other', 'invalid', 'invalid.deprecated', 'invalid.illegal', 'keyword', 'keyword.control',
            'keyword.declaration', 'keyword.operator', 'markup', 'punctuation', 'source', 'storage.modifier', 'storage.type', 'string',
            'support', 'text', 'variable', 'variable.function', 'variable.language', 'variable.parameter']

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
        html1 = '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<style  type="text/css">\np {\nmargin: 0em;\nfont-family: Consolas;\nfont-size: 1.0em;\nbackground-color: transparent;\n}\n'
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
def _highlight_one(view, token, whole_word, scope):

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
        sublime.ok_cancel_dialog("Hi there from StptMsgBoxCommand") # ok_cancel_dialog


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
