import os
import time
import math
import textwrap
import webbrowser
from html import escape
import sublime
import sublime_plugin
from sbot_common import *

print('Python: load sbot_render')


#-----------------------------------------------------------------------------------
class SbotRenderToHtmlCommand(sublime_plugin.TextCommand):
    ''' Make a pretty. '''

    def __init__(self, view):
        # Get prefs.
        self.settings = sublime.load_settings(SETTINGS_FN)
        self.rows = 0
        self.row_num = 0
        super(SbotRenderToHtmlCommand, self).__init__(view)
        self.view = view

    def run(self, edit, line_numbers):
        try:
            self.line_numbers = line_numbers
            render_max_file = self.settings.get('render_max_file')
            fsize = self.view.size() / 1024.0 / 1024.0
            if fsize > render_max_file:
                sublime.message_dialog('File too large to render. If you really want to, change your settings')
            else:
                self._do_render()
                # Actually would like to run in a thread but takes 10x time, probably the GIL.
                # t = threading.Thread(target=self._do_render)
                # t.start()
        except Exception as e:
            plugin_exception(e)


    def _update_status(self):
        ''' Runs in main thread. '''
        if self.row_num == 0:
            self.view.set_status('render', 'Render setting up')
            # self.view.show_popup('Render setting up')
            sublime.set_timeout(self._update_status, 100)
        elif self.row_num >= self.rows:
            self.view.set_status('render', 'Render done')
            # self.view.update_popup('Render done')
            # self.view.hide_popup()
        else:
            if self.rows % 100 == 0:
                self.view.set_status('render', f'Render {self.row_num} of {self.rows}')

            # sublime.set_timeout(lambda: self._update_status(), 100)
            sublime.set_timeout(self._update_status, 100)

    def _do_render(self):
        '''
        The worker thread.
        html render msec per line:
        - medium (5000 dense lines) 1.25
        - small (1178 sparse lines) 0.40
        - biggish (20616 dense lines = 3Mb) 1.36
        '''

        ## Get prefs.
        html_font_size = self.settings.get('html_font_size')
        html_font_face = self.settings.get('html_font_face')
        html_background = self.settings.get('html_background')

        ## Collect scope/style info.
        all_styles = {} # k:style v:id
        region_styles = [] # One [(Region, style)] per line
        highlight_regions = [] # (Region, style))

        self.rows, _ = self.view.rowcol(self.view.size())
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
        highlight_scopes = self.settings.get('highlight_scopes')

        for i, value in enumerate(highlight_scopes):
            # Get the style and invert for highlights.
            ss = self.view.style_for_scope(value)
            background = ss['background'] if 'background' in ss else ss['foreground']
            foreground = html_background
            hl_style = (foreground, background, False, False)
            _add_style(hl_style)

            # Collect the highlight regions.
            reg_name = HIGHLIGHT_REGION_NAME % value
            for region in self.view.get_regions(reg_name):
                highlight_regions.append((region, hl_style))

        # Put all in order.
        highlight_regions.sort(key=lambda r: r[0].a)

        ## Tokenize selection by syntax scope.
        # pc = SbotPerfCounter('render_html')

        for region in get_sel_regions(self.view):
            for line_region in self.view.split_by_newlines(region):
                # pc.start()
                self.row_num += 1

                line_styles = [] # (Region, style))

                # Start a new line.
                current_style = None
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
                        new_style = _view_style_to_tuple(self.view.style_for_scope(self.view.scope_name(point)))

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
                # pc.stop()

        # Done all lines.
        
        # trace('loop:', pc.dump())
        # return

        ## Create css.
        style_text = ""
        for style, stid in all_styles.items():
            props = f'{{ color:{style[0]}; '
            if style[1] is not None:
                props += f'background-color:{style[1]}; '
            if style[2]:
                props += f'font-weight:bold; '
            if style[3]:
                props += f'font-style:italic; '
            props += '}'
            style_text += f'.st{stid} {props}\n'

        ## Content text.
        content = []
        line_num = 1

        ## Iterate collected lines.
        gutter_size = math.ceil(math.log(len(region_styles), 10))
        padding1 = 1.4 + gutter_size * 0.5
        padding2 = padding1

        for line_styles in region_styles:
            # Start line.
            content.append(f'<p>{line_num:0{gutter_size}} ' if self.line_numbers else "<p>" )

            if len(line_styles) == 0:
                content.append('<br>')
            else:
                for region, style in line_styles:
                    #[(Region, style(ref))]
                    text = self.view.substr(region)

                    # Locate the style.
                    stid = _get_style(style)
                    content.append(f'<span class=st{stid}>{escape(text)}</span>' if stid >= 0 else text)

            # Done line.
            content.append('</p>\n')
            line_num += 1

        ## Output html.
        html1 = textwrap.dedent(f'''
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">
            <style  type="text/css">
            .contentpane {{ font-family: {html_font_face}; font-size: {html_font_size/16}em; background-color: {html_background}; text-indent: -{padding1}em; padding-left: {padding2}em; }}
            p {{ white-space: pre-wrap; margin: 0em; }}
            ''')

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

        _output_html(self.view, [html1, style_text, html2, "".join(content), html3])


#-----------------------------------------------------------------------------------
class SbotRenderMarkdownCommand(sublime_plugin.TextCommand):
    ''' Turn md into html.'''

    def run(self, edit):
        try:
            # Get prefs.
            settings = sublime.load_settings(SETTINGS_FN)
            html_background = settings.get('html_background')
            html_font_size = settings.get('html_font_size')
            html_md_font_face = settings.get('html_md_font_face')

            html = []
            html.append("<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
            html.append(f"<style>body {{ background-color:{html_background}; font-family:{html_md_font_face}; font-size:{html_font_size}; }}")
            html.append("</style></head><body>")
            # To support Unicode input, you must add <meta charset="utf-8"> to the *top* of your document (in the first 512 bytes).

            for region in get_sel_regions(self.view):
                html.append(self.view.substr(region))

            html.append("<!-- Markdeep: --><style class=\"fallback\">body{visibility:hidden;white-space:pre}</style><script src=\"markdeep.min.js\" charset=\"utf-8\"></script><script src=\"https://casual-effects.com/markdeep/latest/markdeep.min.js\" charset=\"utf-8\"></script><script>window.alreadyProcessedMarkdeep||(document.body.style.visibility=\"visible\")</script>")
            html.append("</body></html>")

            _output_html(self.view, '\n'.join(html))
        except Exception as e:
            plugin_exception(e)
    

    def is_visible(self):
        return self.view.settings().get('syntax').endswith('Markdown.sublime-syntax')


#-----------------------------------------------------------------------------------
def _output_html(view, content=None):
    ''' Common html file formatter. '''

    settings = sublime.load_settings(SETTINGS_FN)
    output_type = settings.get('render_output')
    s = "" if content is None else "".join(content)

    if output_type == 'clipboard':
        sublime.set_clipboard(s)
    # elif output_type == 'new_file':
    #     view = create_new_view(self.view.window(), s)
    #     view.set_syntax_file('Packages/HTML/HTML.tmLanguage')
    elif output_type in ('file', 'show'):
        basefn = 'default.html' if view.file_name() is None else os.path.basename(view.file_name()) + '.html'
        fn = os.path.join(get_temp_path(), basefn) # TODO breaks on relative links like embedded images - render in origin?
        # fn = basefn
        with open(fn, 'w', encoding='utf-8') as f: # need to explicitly set encoding because default windows is ascii
            f.write(s)
        if output_type == 'show':
            webbrowser.open_new_tab(fn)
