import os
import re
import pdb
import textwrap
import math
import uuid
import json
import webbrowser
import sys
import logging
from html import escape
import sublime
import sublime_plugin
import Default.goto_line
import time
from collections import defaultdict


### Defs.
HIGHLIGHT_REGION_NAME = 'highlight_%d'
SIGNET_REGION_NAME = 'signet'
NUM_HIGHLIGHTS = 10
WHITESPACE = '_ws'
SIGNET_ICON = 'bookmark'
# SIGNET_ICON = 'Packages/Theme - Default/common/label.png'
SBOT_PROJECT_EXT = '.sbot-project'

### Vars.
settings = {}
views_inited = set()
highlight_slots = set()
sbot_projects = {} # {window_id:SbotProject}



#-----------------------------------------------------------------------------------
class TestTestTestCommand(sublime_plugin.TextCommand):

    def run(self, edit, all=False):
        # save_sbot_projects()
        v = self.view
        w = self.view.window()
        # for sheet in w.sheets():
        #     print('sheet:', sheet)
        for view in w.views(): # These are in order L -> R.
            print('active view:', w.get_view_index(view), view.file_name()) # (group, index)
        get_project(v).dump() # These are not ordered like file.


#-----------------------------------------------------------------------------------
class SbotProject(object):
    ''' Container for persistence. '''

    def __init__(self, project_fn):
        self.fn = project_fn.replace('.sublime-project', SBOT_PROJECT_EXT)

        # Unpack into our convenience collections.
        self.signets = {} # {filename:[signet_rows]} # persisted row is 1-based, internally is 0-based (like ST)
        self.highlights = {} # {filename:[{"token":"abc", "wholeword":true, "scope":"xyz"}]}

    # "highlights": [
    #     {
    #         "filename": "C:\\Users\\cepth\\AppData\\Roaming\\Sublime Text 3\\Packages\\SublimeBagOfTricks\\test\\tt.cs",
    #         "tokens": [
    #             { "token":"int", "wholeword":true, "scope":"xyz" },
    #             { "token":"void", "wholeword":true, "scope":"xyz" },
    #         ]
    #     }
    # ]



        try:
            with open(self.fn, 'r') as fp:
                values = json.load(fp)
                for sig in values['signets']:
                    self.signets[sig['filename']] = sig['rows']
        except FileNotFoundError as e:
            # Assumes new file.
            sublime.status_message('Creating new sbot project file')
        except:
            e, v, t = sys.exc_info() # (type, value, traceback)
            sublime.error_message('bad thing! {} {} {}'.format(e, v, t))

    def save(self):
        try:
            sigs = []
            for filename, rows in self.signets.items():
                if len(rows) > 0:
                    if os.path.exists(filename): # last check
                        sigs.append({'filename': filename, 'rows': rows})
            values = {}
            values['signets'] = sigs

            with open(self.fn+'xxx', 'w') as fp:
                json.dump(values, fp, indent=4)
        except:
            e, v, t = sys.exc_info() # (type, value, traceback)
            sublime.error_message('bad thing! {} {} {}'.format(e, v, t))

    def dump(self):
        for filename, rows in self.signets.items():
            print('signet file:', filename, len(rows))


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module stuff. '''
    global settings
    # Init logging.
    ddir = r'{0}\SublimeBagOfTricks'.format(sublime.packages_path())
    logf = ddir + r'\sbot_log.txt'
    logformat = "%(asctime)s %(levelname)8s <%(name)s> %(message)s"
    logging.basicConfig(filename=logf, filemode='a', format=logformat, level=logging.INFO) ### mode a/w
    # logging.info("cwd:" + os.getcwd());
    logging.info("=============================== log start =========================================================");
    logging.info("ddir:" + ddir);

    settings = sublime.load_settings('SublimeBagOfTricks.sublime-settings')


#-----------------------------------------------------------------------------------
def dump_view(preamble, view):
    ''' Helper util. '''
    s = []
    s.append('***')
    s.append(preamble)
    if view is None:
        s.append('view:None')
    else:
        s.append('view:' + str(view.id()))

        fn = view.file_name()
        if fn is None:
            s.append('file_name:None')
        else:
            s.append('file_name:' + os.path.split(fn)[1])

        w = view.window()
        if w is not None:
            fn = w.project_file_name()
            if fn is None:
                s.append('project_file_name:None')
            else:
                s.append('project_file_name:' + os.path.split(fn)[1])

    logging.info(" | ".join(s));
            

#-----------------------------------------------------------------------------------
def save_sbot_projects():
    ''' For rent. '''
    for id in list(sbot_projects):
        sbot_projects[id].save()


#-----------------------------------------------------------------------------------
def get_project(view):
    ''' Get the sbot project for the view. None if invalid. '''
    sproj = None
    id = view.window().id()
    if id in sbot_projects:
        sproj = sbot_projects[id]
    return sproj


#-----------------------------------------------------------------------------------
def get_signet_rows(view):
    ''' Get all the signet row numbers in the view. Returns a sorted list. '''
    # Current signets in this view.
    sig_rows = []
    for reg in view.get_regions('signet'):
        row, _ = view.rowcol(reg.a)
        sig_rows.append(row)
    sig_rows.sort()
    return sig_rows


#-----------------------------------------------------------------------------------
def wait_load_file(view, line):
    ''' Helper. '''
    if view.is_loading():
        sublime.set_timeout(lambda: wait_load_file(view, line), 100) # TODOC2 not forever...
    else: # good to go
        view.run_command("goto_line", {"line": line})


#-----------------------------------------------------------------------------------
class ViewEvent(sublime_plugin.ViewEventListener):
    ''' Listener. '''

    def on_activated(self):
        ''' When focus/tab received. '''
        v = self.view
        dump_view('ViewEventListener.on_activated', v)

        # If this is the first time through and project has signets for this file, set them all.
        if not v.id() in views_inited:
            sproj = get_project(v)
            if sproj is not None and v.file_name() in sproj.signets:
                scope = settings.get('signet_scope', 'comment')
                regions = []
                for r in sproj.signets.get(v.file_name(), []):
                    # A new signet.
                    pt = v.text_point(r - 1, 0) # Adjust to 0-based
                    regions.append(sublime.Region(pt, pt))
                v.add_regions(SIGNET_REGION_NAME, regions, scope, SIGNET_ICON)
            views_inited.add(v.id()) # Tag as initialized.

    # def on_deactivated(self):
    #     dump_view('ViewEventListener.on_deactivated', v)

    # def on_new(self): # When creating new window -> ctrl-shift-n
    #     dump_view('ViewEventListener.on_new', self.view)

    # def on_load(self): # When user opens file (not from persistence at start up!)
    #     dump_view('ViewEventListener.on_load', self.view)

    # def on_close(self): # 
    #     dump_view('ViewEventListener.on_close', self.view)

    # def on_pre_close(self):
    #     dump_view('ViewEventListener.on_pre_close', v)


#-----------------------------------------------------------------------------------
class WindowEvent(sublime_plugin.EventListener):
    ''' Listener. '''

    def on_activated(self, view):
        ''' When focus/tab received. '''
        dump_view('EventListener.on_activated', view) # Sometimes gets valid view with None file_name
        # This is kind of crude but there is no project_loaded event (ST4 does though...)
        global sbot_projects
        id = view.window().id()
        # Check for already loaded.
        if not id in sbot_projects:
            fn = view.window().project_file_name()
            # Load the project file.
            sbot_projects[id] = SbotProject(fn)

    def on_deactivated(self, view):
        ''' When focus/tab lost. '''
        # Save to file. Also crude, but on_close is not reliable so we take the conservative approach. (Fixed in ST4)
        v = view
        dump_view('EventListener.on_deactivated', v)
        sbot_project = get_project(v)

        if sbot_project is not None:

            sig_lines = []

            for row in get_signet_rows(v):
                sig_lines.append(row + 1) # Adjust to 1-based

            if len(sig_lines) > 0:
                sbot_project.signets[v.file_name()] = sig_lines
            elif v.file_name() in sbot_project.signets:
                del sbot_project.signets[v.file_name()]

            # Save the project file.
            sbot_project.save()

    # def on_new(self, view): # When creating new window -> ctrl-shift-n
    #     dump_view('EventListener.on_new', view)

    # def on_load(self, view): # When user opens file (not from persistence at start up!)
    #     dump_view('EventListener.on_load', view)

    # def on_close(self, view):
    #     dump_view('EventListener.on_close', view)

    # def on_pre_close(self, view):
    #     dump_view('EventListener.on_pre_close', view)


 #-----------------------------------------------------------------------------------
class ToggleSignetCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        v = self.view

        # Current location.
        sel_row, _ = v.rowcol(v.sel()[0].a)

        signet_rows = []

        existing = False
        for row in get_signet_rows(v):
            if sel_row == row:
                existing = True
            else:
                signet_rows.append(row)

        if not existing:
            signet_rows.append(sel_row)

        # Update signets, brutally.
        v.erase_regions(SIGNET_REGION_NAME)
        regions = []
        for r in signet_rows:
            pt = v.text_point(r, 0) # 0-based
            regions.append(sublime.Region(pt, pt))
        v.add_regions(SIGNET_REGION_NAME, regions, 'comment', SIGNET_ICON)


#-----------------------------------------------------------------------------------
class NextSignetCommand(sublime_plugin.TextCommand):
    ''' Navigate to signet in whole collection. TODOC2 Probably combine next and previous since they are similar. '''

    def run(self, edit):
        # TODOC2 Probably should enable only if there are any signets in views or project.
        v = self.view
        w = self.view.window()
        done = False
        sel_row, _ = v.rowcol(v.sel()[0].a) # current sel

        # 1) If there's another bookmark below >>> goto it
        if not done:
            sig_rows = get_signet_rows(v)
            for sr in sig_rows:
                if sr > sel_row:
                    w.active_view().run_command("goto_line", {"line": sr + 1})
                    done = True
                    break

        # 2) Else if there's an open signet file to the right of this tab >>> focus tab, goto first signet
        if not done:
            view_index = w.get_view_index(v)[1] + 1

            while not done and view_index < len(w.views()):
                vv = w.views()[view_index]
                sig_rows = get_signet_rows(vv)
                if(len(sig_rows) > 0):
                    w.focus_view(vv)
                    vv.run_command("goto_line", {"line": sig_rows[0] + 1})
                    done = True
                else:
                    view_index += 1

        # 3) Else if there is a signet file in the project that is not open >>> open it, focus tab, goto first signet
        if not done:
            sig_files = []
            sproj = get_project(self.view)
            if sproj is not None:
                for sig_fn, sig_rows in sproj.signets.items():
                    if w.find_open_file(sig_fn) is None and os.path.exists(sig_fn) and len(sig_rows) > 0:
                        vv = w.open_file(sig_fn)
                        sublime.set_timeout(lambda: wait_load_file(vv, sig_rows[0]), 10) # already 1-based in file
                        w.focus_view(vv)
                        done = True
                        break

        # 4) Else >>> find first tab/file with signets, focus tab, goto first signet
        if not done:
            view_index = 0
            while not done and view_index < len(w.views()):
                vv = w.views()[view_index]
                sig_rows = get_signet_rows(vv)
                if(len(sig_rows) > 0):
                    w.focus_view(vv)
                    vv.run_command("goto_line", {"line": sig_rows[0] + 1})
                    done = True
                else:
                    view_index += 1
       

#-----------------------------------------------------------------------------------
class PreviousSignetCommand(sublime_plugin.TextCommand):
    ''' Navigate to signet in whole collection. '''

    def run(self, edit):
        # TODOC2 Probably should enable only if there are any signets in views or project.
        v = self.view
        w = self.view.window()
        done = False
        sel_row, _ = v.rowcol(v.sel()[0].a) # current sel

        # 1) If there's another bookmark above >>> goto it
        if not done:
            sig_rows = get_signet_rows(v)
            sig_rows.reverse()
            for sr in sig_rows:
                if sr < sel_row:
                    w.active_view().run_command("goto_line", {"line": sr + 1})
                    done = True
                    break

        # 2) Else if there's an open signet file to the left of this tab >>> focus tab, goto last signet
        if not done:
            view_index = w.get_view_index(v)[1] - 1

            while not done and view_index >= 0:
                vv = w.views()[view_index]
                sig_rows = get_signet_rows(vv)
                if(len(sig_rows) > 0):
                    w.focus_view(vv)
                    vv.run_command("goto_line", {"line": sig_rows[-1] + 1})
                    done = True
                else:
                    view_index -= 1

        # 3) Else if there is a signet file in the project that is not open >>> open it, focus tab, goto first signet
        if not done:
            sig_files = []
            sproj = get_project(self.view)
            if sproj is not None:
                for sig_fn, sig_rows in sproj.signets.items():
                    if w.find_open_file(sig_fn) is None and os.path.exists(sig_fn) and len(sig_rows) > 0:
                        vv = w.open_file(sig_fn)
                        sublime.set_timeout(lambda: wait_load_file(vv, sig_rows[-1]), 10) # already 1-based in file
                        w.focus_view(vv)
                        done = True
                        break

        # 4) Else >>> find last tab/file with signets, focus tab, goto last signet
        if not done:
            view_index = len(w.views()) - 1
            while not done and view_index >= 0:
                vv = w.views()[view_index]
                sig_rows = get_signet_rows(vv)
                if(len(sig_rows) > 0):
                    w.focus_view(vv)
                    vv.run_command("goto_line", {"line": sig_rows[-1] + 1})
                    done = True
                else:
                    view_index -= 1


#-----------------------------------------------------------------------------------
class ClearSignetsCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        sproj = get_project(self.view)
        # clear persistence
        if sproj is not None:
            sproj.signets.clear()
        # clear visual
        for vv in self.view.window().views():
            vv.erase_regions(SIGNET_REGION_NAME)


#-----------------------------------------------------------------------------------
class RenderHtmlCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        ''' Get prefs.'''
        html_font_size = settings.get('html_font_size', 12)
        html_font_face = settings.get('html_font_face', 'Consolas')
        html_plain_text = settings.get('html_plain_text', '#000000')
        html_background = settings.get('html_background', 'transparent')
        html_line_numbers = settings.get('html_line_numbers', True)

        ## Collect scope/style info.
        all_scopes = set() # All unique values
        scope_tokens = [] # One [(Region, scope)] per line

        ## Html style info.
        css1 = dict() # {selector:properties}
        css2 = dict() # {properties:selector}
        style_map = dict() # {scope:selector}

        ## Tokenize by scope.
        has_selection = len(v.sel()[0]) > 0
        selreg = v.sel()[0] if has_selection else sublime.Region(0, v.size())

        for line_region in v.split_by_newlines(selreg): # TODOC2 Optimize using python splitlines()?
            # line_num += 1
            line_tokens = [] # (Region, scope)

            # Process the line chars.
            current_scope = ""
            new_scope = ""
            current_scope_start = line_region.a # current chunk

            for point in range(line_region.a, line_region.b + 1):
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

        ## Output everything. 
        output_type = settings.get('html_output', 'new_file')

        if(output_type == 'clipboard'):
            sublime.set_clipboard(html1 + style_text + html2 + "".join(content) + html3)
        elif(output_type == 'new_file'):
            new_view = sublime.active_window().new_file()
            new_view.set_syntax_file('Packages/HTML/HTML.tmLanguage')
            new_view.insert(edit, 0, html1 + style_text + html2 + "".join(content) + html3)
        elif(output_type == 'default_file'):
            if v.file_name() is None:
                sublime.error_message("Can't use html_output=default_file for unnamed files")
            else:
                with open(v.file_name() + '.html', 'w') as file:
                    file.write(html1 + style_text + html2 + "".join(content) + html3)


#-----------------------------------------------------------------------------------
class ShowScopesCommand(sublime_plugin.TextCommand):
    ''' Show style info for common scopes. List from https://www.sublimetext.com/docs/3/scope_naming.html. '''

    def run(self, edit):
        v = self.view
        style_text = []
        content = []
        scopes = ['entity.name', 'entity.other.inherited-class', 'entity.name.section', 'entity.name.tag', 'entity.other.attribute-name',
            'variable', 'variable.language', 'variable.parameter', 'variable.function', 'constant', 'constant.numeric', 'constant.language',
            'constant.character.escape', 'storage.type', 'storage.modifier', 'support', 'keyword', 'keyword.control', 'keyword.operator',
            'keyword.declaration', 'string', 'comment', 'invalid', 'invalid.deprecated']


        ''' All primary scopes
        scopes = ['comment.block', 'comment.block.documentation', 'comment.line', 'constant.character.escape', 'constant.language', 'constant.numeric',
            'constant.numeric.complex', 'constant.numeric.complex.imaginary', 'constant.numeric.complex.real', 'constant.numeric.float',
            'constant.numeric.float.binary', 'constant.numeric.float.decimal', 'constant.numeric.float.hexadecimal', 'constant.numeric.float.octal',
            'constant.numeric.float.other', 'constant.numeric.integer', 'constant.numeric.integer.binary', 'constant.numeric.integer.decimal',
            'constant.numeric.integer.hexadecimal', 'constant.numeric.integer.octal', 'constant.numeric.integer.other', 'constant.other',
            'constant.other.placeholder', 'entity.name.class', 'entity.name.class.forward-decl', 'entity.name.constant', 'entity.name.enum',
            'entity.name.function', 'entity.name.function.constructor', 'entity.name.function.destructor', 'entity.name.impl', 'entity.name.interface',
            'entity.name.label', 'entity.name.namespace', 'entity.name.section', 'entity.name.struct', 'entity.name.tag', 'entity.name.trait',
            'entity.name.type', 'entity.name.union', 'entity.other.attribute-name', 'entity.other.inherited-class', 'invalid.deprecated', 'invalid.illegal',
            'keyword.control', 'keyword.control.conditional', 'keyword.control.import', 'keyword.declaration.class', 'keyword.declaration.enum', 
            'keyword.declaration.function', 'keyword.declaration.impl', 'keyword.declaration.interface', 'keyword.declaration.struct', 
            'keyword.declaration.trait', 'keyword.declaration.type', 'keyword.declaration.union', 'keyword.operator', 'keyword.operator.arithmetic', 
            'keyword.operator.assignment', 'keyword.operator.bitwise', 'keyword.operator.logical', 'keyword.operator.word', 'keyword.other', 'markup.bold', 
            'markup.deleted', 'markup.heading', 'markup.inserted', 'markup.italic', 'markup.list.numbered', 'markup.list.unnumbered', 'markup.other', 
            'markup.quote', 'markup.raw.block', 'markup.raw.inline', 'markup.underline', 'markup.underline.link', 'punctuation.accessor', 
            'punctuation.definition.annotation', 'punctuation.definition.comment', 'punctuation.definition.keyword', 'punctuation.definition.string.begin', 
            'punctuation.definition.string.end', 'punctuation.definition.variable', 'punctuation.section.interpolation.begin', 
            'punctuation.section.interpolation.end', 'punctuation.separator', 'punctuation.separator.continuation', 'punctuation.terminator', 'source', 
            'source.language-suffix.embedded', 'storage.modifier', 'storage.type', 'storage.type', 'storage.type.class', 'storage.type.enum', 
            'storage.type.function', 'storage.type.impl', 'storage.type.interface', 'storage.type.struct', 'storage.type.trait', 'storage.type.union', 
            'string.quoted.double', 'string.quoted.other', 'string.quoted.single', 'string.quoted.triple', 'string.regexp', 'string.unquoted', 'support.class', 
            'support.constant', 'support.function', 'support.module', 'support.type', 'text.html', 'text.xml', 'variable.annotation', 'variable.function', 
            'variable.language', 'variable.other', 'variable.other.constant', 'variable.other.member', 'variable.other.readwrite', 'variable.parameter']
        '''

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
class HighlightTextCommand(sublime_plugin.TextCommand): #TODOC1 persist these.
    ''' Parts borrowed from StyleToken.
    Apparently, regions added by v.add_regions() can not set the foreground color.
    By default they only color the background and with options they can also color the outline
    only or underline the region. Setting the foreground color is not supported.
    Also note that they are not added to scopes accessible by extract_scope(point).
    '''

    def run(self, edit):
        v = self.view
        # Find open slot.
        which = -1

        for i in range(NUM_HIGHLIGHTS):
            if i not in highlight_slots:
                which = i
                highlight_slots.add(i)
                break;

        if which >= 0:
            # Get the region.
            mark_regions = v.get_regions(HIGHLIGHT_REGION_NAME % which)
            tokens = set()

            for region in v.sel():
                whole_word = region.empty()
                if whole_word:
                    region = v.word(region)
                    if region.empty():
                        continue
                        
                literal = v.substr(region)
                escaped = re.escape(literal)

                if whole_word and escaped[0].isalnum():
                    escaped = r'\b%s\b' % escaped

                tokens.add(escaped)

            if len(tokens) == 1 and not whole_word:
                mark_regions.extend(v.find_all(literal, sublime.LITERAL))
            elif len(tokens) > 0:
                mark_regions.extend(v.find_all('|'.join(tokens)))

            mark_scopes = settings.get('mark_scopes')
            scope = mark_scopes[which]
            v.erase_regions(HIGHLIGHT_REGION_NAME % which) # does this work?
            v.add_regions(HIGHLIGHT_REGION_NAME % which, mark_regions, scope)


#-----------------------------------------------------------------------------------
class ClearHighlightCommand(sublime_plugin.TextCommand):
    ''' Clear all marks where the cursor is.'''

    def run(self, edit):
        # Locate specific region.
        v = self.view
        point = v.sel()[0].a
        toremove = set()
        for i in highlight_slots:
            for region in v.get_regions(HIGHLIGHT_REGION_NAME % i):
                if region.contains(point):
                    v.erase_regions(HIGHLIGHT_REGION_NAME % i)
                    toremove.add(i)
                    break;
        for i in toremove:
            highlight_slots.remove(i)


#-----------------------------------------------------------------------------------
class ClearAllHighlightCommand(sublime_plugin.TextCommand):
    ''' Clear all marks where the cursor is.'''

    def run(self, edit):
        v = self.view
        for i in range(NUM_HIGHLIGHTS):
            v.erase_regions(HIGHLIGHT_REGION_NAME % i)
        highlight_slots.clear()


#-----------------------------------------------------------------------------------
class RenderMarkdownCommand(sublime_plugin.TextCommand):
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
        html_background = settings.get('html_background', 'transparent')

        html = []
        html.append("<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
        html.append("<style>body {{ background-color:{}; }}".format(html_background))
        html.append("</style></head><body>")

        html.append(v.substr(sublime.Region(0, v.size())))

        html.append("<!-- Markdeep: --><style class=\"fallback\">body{visibility:hidden;white-space:pre;font-family:monospace}</style><script src=\"markdeep.min.js\" charset=\"utf-8\"></script><script src=\"https://casual-effects.com/markdeep/latest/markdeep.min.js\" charset=\"utf-8\"></script><script>window.alreadyProcessedMarkdeep||(document.body.style.visibility=\"visible\")</script>")
        html.append("</body></html>")

        content = '\n'.join(html)

        ##### Output. 
        output_type = settings.get('html_output', 'new_file')

        if(output_type == 'clipboard'):
            sublime.set_clipboard(content)
        elif(output_type == 'new_file'):
            new_view = sublime.active_window().new_file()
            new_view.set_syntax_file('Packages/HTML/HTML.tmLanguage')
            new_view.insert(edit, 0, content)
        elif(output_type == 'default_file'):
            if v.file_name() is None:
                sublime.error_message("Can't use html_output=default_file for unnamed files")
            else:
                with open(v.file_name() + '.html', 'w') as file:
                    file.write(content)

        # Process.Start(fn);


#-----------------------------------------------------------------------------------
class SplitViewCommand(sublime_plugin.WindowCommand):
    ''' Toggles betweensplit file in new row.'''

    def run(self):
        lo = self.window.layout()

        if(len(lo['rows']) > 2):
            # Remove split.
            self.window.run_command("focus_group", { "group": 1 } )
            self.window.run_command("close_file")
            self.window.run_command("set_layout", { "cols": [0.0, 1.0], "rows": [0.0, 1.0], "cells": [[0, 0, 1, 1]] } )
        else:
            # Add split.
            self.window.run_command("set_layout", { "cols": [0.0, 1.0], "rows": [0.0, 0.5, 1.0], "cells": [[0, 0, 1, 1], [0, 1, 1, 2]] } )
            self.window.run_command("focus_group", { "group": 0 } )
            self.window.run_command("clone_file")
            self.window.run_command("move_to_group", { "group": 1 } )


#-----------------------------------------------------------------------------------
class OpenSiteCommand(sublime_plugin.ApplicationCommand):
    ''' Open a web page. '''

    def run(self, url):
        webbrowser.open_new_tab(url)


#-----------------------------------------------------------------------------------
# Holding tank for a bunch of examples and extras.
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
        # print("SbotExInputHandler.__init__")
        self.view = view

    def placeholder(self):
        return "placeholder - optional"

    def description(self, sdef):
        return "description for SbotExInputHandler"

    def initial_text(self):
        # for r in self.view.sel():
        #     print(r)
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
