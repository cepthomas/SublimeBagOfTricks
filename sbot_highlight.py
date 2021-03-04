import os
import sys
import re
import sublime
import sublime_plugin
import sbot_common
import sbot_project


HIGHLIGHT_REGION_NAME = 'highlight_%s'
MAX_HIGHLIGHTS = 6


#-----------------------------------------------------------------------------------
class SbotHighlightTextCommand(sublime_plugin.TextCommand):
    ''' Highlight specific words using scopes. Parts borrowed from StyleToken.
    Persistence supported via sbot-project container.

    Note: Regions added by v.add_regions() can not set the foreground color. The scope color is used
    for the region background color. Also they are not available via extract_scope().
    '''

    def run(self, edit, hl_index):
        v = self.view
        highlight_scopes = sbot_common.settings.get('highlight_scopes')

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
        sproj = sbot_project.get_project(v)
        if v.file_name() not in sproj.highlights:
            sproj.highlights[v.file_name()] = []
        sproj.highlights[v.file_name()].append( { "token": token, "whole_word": whole_word, "scope": scope } )


#-----------------------------------------------------------------------------------
class SbotClearHighlightCommand(sublime_plugin.TextCommand):
    ''' Clear all where the cursor is. '''

    def run(self, edit):
        # Locate specific region, crudely.
        v = self.view
        sproj = sbot_project.get_project(v)
        highlight_scopes = sbot_common.settings.get('highlight_scopes')
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
class SbotClearHighlightsCommand(sublime_plugin.TextCommand):
    ''' Clear all in this file.'''

    def run(self, edit):
        v = self.view
        sproj = sbot_project.get_project(v)
        highlight_scopes = sbot_common.settings.get('highlight_scopes')
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
    #TODO let user add more.

    def run(self, edit):
        v = self.view

        style_text = []
        content = []
        scopes = [
            'comment', 'constant', 'constant.character.escape', 'constant.language', 'constant.numeric', 'entity.name',
            'entity.name.section', 'entity.name.tag', 'entity.other', 'invalid', 'invalid.deprecated', 'invalid.illegal',
            'keyword', 'keyword.control', 'keyword.declaration', 'keyword.operator', 'markup', 'punctuation', 'source',
            'storage.modifier', 'storage.type', 'string', 'support', 'text', 'variable', 'variable.function',
            'variable.language', 'variable.parameter',
            'region.redish', 'region.orangish', 'region.yellowish', 'region.greenish', 'region.cyanish', 
            'region.bluish', 'region.purplish', 'region.pinkish'
            ]

        # scopes = set()
        # for i in range(v.size()):
        #     scopes.add(v.scope_name(i))

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
                <style> p {{ margin: 0em; }} {} </style>
                {}
                {}
            </body>
        '''.format('\n'.join(style_text), '\n'.join(content), html3)

        v.show_popup(html, max_width=512)


#-----------------------------------------------------------------------------------
def init_highlights(view, tokens):

    for tok in tokens:
        _highlight_view(view, tok['token'], tok['whole_word'], tok['scope'])


#-----------------------------------------------------------------------------------
def _highlight_view(view, token, whole_word, scope):

    escaped = re.escape(token)
    if whole_word and escaped[0].isalnum():
        escaped = r'\b%s\b' % escaped

    highlight_regions = view.find_all(escaped) if whole_word else view.find_all(token, sublime.LITERAL)
    if len(highlight_regions) > 0:
        view.add_regions(HIGHLIGHT_REGION_NAME % scope, highlight_regions, scope)
