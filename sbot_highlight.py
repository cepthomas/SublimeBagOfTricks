import os
import sys
import re
import json
import sublime
import sublime_plugin
import sbot_common

# print('^^^^^ Load sbot_highlight')


HIGHLIGHT_REGION_NAME = 'highlight_%s'
MAX_HIGHLIGHTS = 6

# The current highlight collections. Key is window id which corresponds to a project.
_hls = {}

# Need to track these because ST window/view lifecycle is unreliable.
_views_inited = set()

# The settings.
_settings = {}

#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. '''
    sbot_common.trace('plugin_loaded sbot_highlight')
    global _settings
    _settings = sublime.load_settings('SublimeBagOfTricks.sublime-settings')


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    ''' Clean up module global stuff. '''
    sbot_common.trace('plugin_unloaded sbot_highlight')


#-----------------------------------------------------------------------------------
def _highlight_view(view, token, whole_word, scope):
    ''' Colorize one token. '''
    escaped = re.escape(token)
    if whole_word and escaped[0].isalnum():
        escaped = r'\b%s\b' % escaped

    highlight_regions = view.find_all(escaped) if whole_word else view.find_all(token, sublime.LITERAL)
    if len(highlight_regions) > 0:
        view.add_regions(HIGHLIGHT_REGION_NAME % scope, highlight_regions, scope)


#-----------------------------------------------------------------------------------
def _get_collection_values(view):
    ''' General helper to get the data values from collection. Initializes for new files. '''
    global _hls

    vals = {} # Default
    winid = view.window().id()
    fn = view.file_name()
    if winid in _hls:
        if fn not in _hls[winid]:
            # Add a new one.
            _hls[winid][fn] = {}
        vals = _hls[winid][fn]
    else:
        pass # TODO error

    return vals


#-----------------------------------------------------------------------------------
class HighlightEvent(sublime_plugin.EventListener):
    ''' Listener for events of interest. '''

    def on_activated(self, view):
        ''' When focus/tab received. This is the only reliable event - on_load() doesn't get called when showing previously opened files. '''
        global _views_inited
        vid = view.id()
        winid = view.window().id()
        fn = view.file_name()
        
        sbot_common.trace('HighlightEvent.on_activated', fn, vid, winid, _views_inited)

        # Lazy init.
        if fn is not None: # TODO Sometimes this happens...
            if vid not in _views_inited:
                _views_inited.add(vid)

                # Init the view.
                for token, tparams in _hls.get(fn, {}).items():
                    _highlight_view(view, token, tparams['whole_word'], tparams['scope'])


    def on_close(self, view):
        ''' Called when a view is closed (note, there may still be other views into the same buffer). '''
        sbot_common.trace('HighlightEvent.on_close', view.file_name(), view.id(), 'view.window is None', 'ng view.window().project_file_name()', 'end')
        # if view.file_name() is not None:


    def on_load(self, view):
        ''' Called when a view is closed (note, there may still be other views into the same buffer). '''
        sbot_common.trace('HighlightEvent.on_load', view.file_name(), view.id(), view.window, view.window().project_file_name())
        # if view.file_name() is not None:


    def on_activated(self, view):
        ''' When focus/tab received. This is the only reliable event - on_load() doesn't get called when showing previously opened files. '''
        winid = view.window().id()
        sbot_common.trace('HighlightEvent.on_activated', view.file_name(), view.id(), winid, view.window().project_file_name())

        if winid not in _hls:
            _open_hls(winid, view.window().project_file_name())
        else:
            pass # TODO error?


    def on_deactivated(self, view): # use on_close() TODO?
        ''' When focus/tab lost. Save to file. Crude, but on_close is not reliable so we take the conservative approach. TODO-ST4 has on_pre_save_project(). '''
        winid = view.window().id()
        sbot_common.trace('HighlightEvent.on_deactivated', view.id(), winid)

        if winid in _hls:
            _save_hls(winid, view.window().project_file_name())
        else:
            pass # TODO error?



#-----------------------------------------------------------------------------------
def _save_hls(winid, stp_fn):
    ''' General project saver. '''
    ok = True
    return ok #TODO

    if _settings.get('enable_persistence', True):
        fn = stp_fn.replace('.sublime-project', '.sbot_hls')
        
        try:
            with open(fn, 'w') as fp:
                json.dump(_hls[winid], fp, indent=4)

        except Exception as e:
            sres = 'Save sbot-project error: {}'.format(e.args)
            sublime.error_message(sres)
            ok = False

    return ok


#-----------------------------------------------------------------------------------
def _open_hls(winid, stp_fn):
    ''' General project opener. '''
    global _hls
    ok = True

    if _settings.get('enable_persistence', True):
        fn = stp_fn.replace('.sublime-project', '.sbot_hls')

        try:
            with open(fn, 'r') as fp:
                values = json.load(fp)
                _hls[winid] = values

        except FileNotFoundError as e:
            # Assumes new file.
            sublime.status_message('Creating new sbot project file')
            _hls[winid] = { 'highlights': {}, 'signets': {} }

        except Exception as e:
            sres = 'Open sbot-project error: {}'.format(e.args)
            sublime.error_message(sres)
            ok = False

    # if ok:
    #     sbot_global.init_highlights(winid, _hls[winid]['highlights'])
    #     # sbot_highlight.init_highlights(winid, _hls[winid]['highlights'])
    #     sbot_signet.init_signets(winid, _hls[winid]['signets'])

    return ok

#-----------------------------------------------------------------------------------
class SbotHighlightTextCommand(sublime_plugin.TextCommand):
    ''' Highlight specific words using scopes. Parts borrowed from StyleToken.
    Persistence supported via sbot-project container.
    Note: Regions added by v.add_regions() can not set the foreground color. The scope color is used
    for the region background color. Also they are not available via extract_scope().
    '''
    def run(self, edit, hl_index):
        v = self.view
        highlight_scopes = _settings.get('highlight_scopes')


        # Get whole word or specific span.
        region = v.sel()[0]

        whole_word = region.empty()
        if whole_word:
            region = v.word(region)
        token = v.substr(region)

        num_highlights = min(len(highlight_scopes), MAX_HIGHLIGHTS)
        hl_index = min(hl_index, num_highlights)

        scope = highlight_scopes[hl_index]
        tokens = _get_collection_values(v)

        # Add or replace in collection.
        tokens[token] = { "scope": scope, "whole_word": whole_word }
        _highlight_view(v, token, whole_word, scope)


#-----------------------------------------------------------------------------------
class SbotClearHighlightCommand(sublime_plugin.TextCommand):
    ''' Clear all where the cursor is. '''

    def run(self, edit):
        global _hls

        # Locate specific region, crudely.
        v = self.view

        tokens = _get_collection_values(v)

        highlight_scopes = _settings.get('highlight_scopes')
        num_highlights = min(len(highlight_scopes), MAX_HIGHLIGHTS)

        point = v.sel()[0].a

        highlight_scope = ''

        # Clean displayed colors.
        for i in range(num_highlights):
            reg_name = HIGHLIGHT_REGION_NAME % highlight_scopes[i]
            for region in v.get_regions(reg_name):
                if region.contains(point):
                    highlight_scope = highlight_scopes[i]
                    v.erase_regions(reg_name)

                    # # Remove from internal. old
                    # if v.file_name() in sproj.highlights:
                    #     for i in range(len(sproj.highlights[v.file_name()])):
                    #         if sproj.highlights[v.file_name()][i]['scope'] == highlight_scope:
                    #             del sproj.highlights[v.file_name()][i]
                    #             break;


                    # Remove from collection. TODO fix
                    # for hl in sproj.highlights:
                    #     fn = v.file_name()
                    #     if fn == hl['filename']:
                    #         for i in range(len(hl['tokens'])):
                    #             if hl['tokens'][i]['scope'] == highlight_scope:
                    #                 del hl['tokens'][i]
                    #                 break;

                    break;


#-----------------------------------------------------------------------------------
class SbotClearHighlightsCommand(sublime_plugin.TextCommand):
    ''' Clear all in this file.'''

    def run(self, edit):
        global _hls

        v = self.view

        # Clean displayed colors.
        highlight_scopes = _settings.get('highlight_scopes')
        num_highlights = min(len(highlight_scopes), MAX_HIGHLIGHTS)

        for i in range(num_highlights):
            reg_name = HIGHLIGHT_REGION_NAME % highlight_scopes[i]
            v.erase_regions(reg_name)

        # Remove from collection.
        winid = self.view.window().id()
        fn = self.view.file_name()
        del _hls[winid][fn]


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
            # sbot_common.trace(scope, style)
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

        # Do popup
        html = '''
            <body>
                <style> p {{ margin: 0em; }} {} </style>
                {}
                {}
            </body>
        '''.format('\n'.join(style_text), '\n'.join(content), html3)

        v.show_popup(html, max_width=512)

        # Could also: sublime.set_clipboard(html1 + '\n'.join(style_text) + html2 + '\n'.join(content) + html3)

