import os
import re
import json
import sublime
import sublime_plugin
from sbot_common import *

print('Python: load sbot_scope')


#-----------------------------------------------------------------------------------
class SbotShowScopesCommand(sublime_plugin.TextCommand):
    ''' Show style info for common scopes. List from https://www.sublimetext.com/docs/3/scope_naming.html. '''

    def run(self, edit):
        settings = sublime.load_settings(SETTINGS_FN)
        scopes = settings.get('scopes_to_show')
        _render_scopes(scopes, self.view)


#-----------------------------------------------------------------------------------
class SbotScopeInfoCommand(sublime_plugin.TextCommand):
    ''' Like builtin ShowScopeNameCommand but with coloring added. '''

    def run(self, edit):
        scope = self.view.scope_name(self.view.sel()[-1].b).rstrip()
        scopes = scope.split()
        _render_scopes(scopes, self.view)


#-----------------------------------------------------------------------------------
def _render_scopes(scopes, view):
    ''' Make popup for list of scopes. '''

    style_text = []
    content = []

    for scope in scopes:
        style = view.style_for_scope(scope)
        # trace(scope, style)
        props = f'{{ color:{style["foreground"]}; '
        props2 = f'fg:{style["foreground"]} '
        if 'background' in style:
            props += f'background-color:{style["background"]}; '
            props2 += f'bg:{style["background"]} '
        if style['bold']:
            props += 'font-weight:bold; '
            props2 += 'bold '
        if style['italic']:
            props += 'font-style:italic; '
            props2 += 'italic '
        props += '}'

        i = len(style_text)
        style_text.append(f'.st{i} {props}')
        content.append(f'<p><span class=st{i}>{scope}  {props2}</span></p>')

    # Do popup
    st = '\n'.join(style_text)
    ct = '\n'.join(content)

    html = f'''
        <body>
            <style> p {{ margin: 0em; }} {st} </style>
            {ct}
        </body>'''

    view.show_popup(html, max_width=512, max_height=600)
