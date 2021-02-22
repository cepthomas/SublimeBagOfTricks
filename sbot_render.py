import os
import sys
import time
import logging
import math
import textwrap
import webbrowser
from html import escape
import sublime
import sublime_plugin
import sbot_common
import sbot_misc


HIGHLIGHT_REGION_NAME = 'highlight_%s' # Duplicated from sbot_highlight. My bad.


#-----------------------------------------------------------------------------------
class SbotRenderToHtmlCommand(sublime_plugin.TextCommand):
    ''' Make a pretty. '''

    def run(self, edit):
        v = self.view

        ## Get prefs.
        render_max_file = sbot_common.settings.get('render_max_file', 1)

        fsize = v.size() / 1024.0 / 1024.0
        if fsize > render_max_file:
            sublime.message_dialog('File too large to render. If you really want to, change your SublimeBagOfTricks.sublime-settings')
        else:
            self._do_work()
            # Actually would like to run in a thread but takes 10x time, probably the GIL.
            # t = threading.Thread(target=self._do_work)
            # t.start()

    def _update_status(self):
        ''' Runs in main thread. '''

        v = self.view

        if self.row_num == 0:
            v.set_status('render', 'Render setting up')
            # v.show_popup('Render setting up')
            sublime.set_timeout(self._update_status, 100)
        elif self.row_num >= self.rows:
            v.set_status('render', 'Render done')
            # v.update_popup('Render done')
            # v.hide_popup()
        else:
            if self.rows % 100 == 0:
                v.set_status('render', 'Render {} of {}'.format(self.row_num, self.rows))
                # v.update_popup('Render {} of {}'.format(self.row_num, self.rows))

            # sublime.set_timeout(lambda: self._update_status(), 100)
            sublime.set_timeout(self._update_status, 100)

    def _do_work(self):
        ''' The worker thread. '''
        
        v = self.view
        
        # - html render msec per line:
        #   - medium (5k dense lines) 1.248921079999997 (5000)
        #   - small (1k sparse lines) 0.4043940577246477 (1178)
        #   - biggish (20k dense lines = 3Mb) 1.3607864668223 (20616)

        ## Get prefs.
        html_font_size = sbot_common.settings.get('html_font_size', 12)
        html_font_face = sbot_common.settings.get('html_font_face', 'Arial')
        html_background = sbot_common.settings.get('html_background', 'white')
        html_line_numbers = sbot_common.settings.get('html_line_numbers', True)
        html_background = sbot_common.settings.get('html_background', 'white')

        # Use tuples for everything as they can be hashable keys.
        # my_style = (foreground, background, bold, italic)

        ## Collect scope/style info.
        all_styles = {} # k:style v:id
        region_styles = [] # One [(Region, style)] per line
        highlight_regions = [] # (Region, style))

        self.rows, _ = v.rowcol(v.size())
        self.row_num = 0

        ### Local helpers.
        def _add_style(style):
            # Add style to our collection.
            if style not in all_styles:
                all_styles[style] = len(all_styles)

        def _get_style(style):
                # Locate the style and return the id.
                return all_styles.get(style, -1)

        def _view_style_to_tuple(view_style):
            tt = (view_style['foreground'], view_style.get('background', None), view_style.get('bold', False), view_style.get('italic', False))
            return tt

        # Start progress.
        sublime.set_timeout(self._update_status, 100)
        
        ## If there are highlights, collect them.
        highlight_scopes = sbot_common.settings.get('highlight_scopes')
        for i in range(len(highlight_scopes)):
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

        pc = sbot_misc.SbotPerfCounter('render_html')

        for line_region in v.split_by_newlines(sel_reg):
            pc.start()
            self.row_num += 1

            if self.row_num % 100 == 0:
                time.sleep(0.01)
                v.show_popup('!!!!!')

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

                    # Remove from the list.
                    del highlight_regions[0]
                else:
                    # Plain ordinary style. Did it change?
                    new_style = _view_style_to_tuple(v.style_for_scope(v.scope_name(point)))

                    if new_style != current_style:
                        # Save last chunk maybe.
                        if point > current_style_start:
                            line_styles.append((sublime.Region(current_style_start, point), current_style))

                        current_style = new_style
                        current_style_start = point

                        _add_style(new_style)

                    # Bump ahead.
                    point += 1

            # Done with this line. Save last chunk maybe.
            if point > current_style_start:
                line_styles.append((sublime.Region(current_style_start, point), current_style))

            # Add to master list.
            region_styles.append(line_styles)
            pc.stop()

        # Done all lines.
        logging.info('loop:' + pc.dump())
        # return

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

        ## Output html.
        html1 = textwrap.dedent('''
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">
            <style  type="text/css">
            .contentpane {{ font-family: {}; font-size: {}em; background-color: {}; text-indent: -{}em; padding-left: {}em; }}
            p {{ white-space: pre-wrap; margin: 0em; }}
            '''.format(html_font_face, html_font_size / 16, html_background, padding, padding))

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

        _output_html(v, [html1, style_text, html2, "".join(content), html3])


#-----------------------------------------------------------------------------------
class SbotRenderMarkdownCommand(sublime_plugin.TextCommand):
    ''' Turn md into html.'''

    def is_visible(self):
        fn = self.view.file_name()
        vis = False if fn is None else self.view.file_name().endswith('.md')
        return vis

    def run(self, edit):
        v = self.view
        ##### Get prefs.
        md_background = sbot_common.settings.get('md_background', 'white')
        md_font_size = sbot_common.settings.get('md_font_size', 12)
        md_font_face = sbot_common.settings.get('md_font_face', 'Arial')

        html = []
        html.append("<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
        html.append("<style>body {{ background-color:{}; font-family:{}; font-size:{}; }}".format(md_background, md_font_face, md_font_size))
        html.append("</style></head><body>")

        html.append(v.substr(sublime.Region(0, v.size())))

        html.append("<!-- Markdeep: --><style class=\"fallback\">body{visibility:hidden;white-space:pre;font-family:monospace}</style><script src=\"markdeep.min.js\" charset=\"utf-8\"></script><script src=\"https://casual-effects.com/markdeep/latest/markdeep.min.js\" charset=\"utf-8\"></script><script>window.alreadyProcessedMarkdeep||(document.body.style.visibility=\"visible\")</script>")
        html.append("</body></html>")

        content = '\n'.join(html)

        _output_html(v, content)


#-----------------------------------------------------------------------------------
def _output_html(view, content=[]):
    output_type = sbot_common.settings.get('render_output', 'new_file')

    if output_type == 'clipboard':
        sublime.set_clipboard("".join(content))

    elif output_type == 'new_file':
        new_view = sublime.active_window().new_file()
        new_view.set_syntax_file('Packages/HTML/HTML.tmLanguage')
        edit = new_view.begin_edit() 
        new_view.insert(edit, 0, "".join(content))
        new_view.end_edit(edit)

    elif output_type == 'default_file' or output_type == 'default_file_open':
        if view.file_name() is None:
            sublime.error_message("Can't use render_output=default_file for unnamed files")
        else:
            hfile = view.file_name() + '.html'
            with open(hfile, 'w') as f:
                f.write("".join(content))
                if output_type == 'default_file_open':
                    webbrowser.open_new_tab(hfile)

