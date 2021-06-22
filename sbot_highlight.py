import os
import re
import json
import sublime
import sublime_plugin
from sbot_common import *

# print('Load sbot_highlight')


# Definitions.
HIGHLIGHT_REGION_NAME = 'highlight_%s'
HIGHLIGHT_FILE_EXT = '.sbot-hls'


# The current highlight collections. Key is window id which corresponds to a project.
_hls = {}

# Need to track what's been initialized.
_views_inited = set()


#-----------------------------------------------------------------------------------
class HighlightEvent(sublime_plugin.ViewEventListener):
    ''' Listener for view specific events of interest. See lifecycle notes in README.md. '''

    def on_activated(self):
        ''' When focus/tab received. '''
        view = self.view
        global _views_inited
        vid = view.id()
        winid = view.window().id()
        fn = view.file_name()

        trace(TraceCat.ACTV_XXX, 'HighlightEvent.on_activated', fn, vid, winid, _views_inited)

        # Lazy init.
        if fn is not None: # Sometimes this happens...
            # Is the persist file read yet?
            if winid not in _hls:
                _open_hls(winid, view.window().project_file_name())

            # Init the view, maybe.
            if vid not in _views_inited:
                _views_inited.add(vid)

                # Init the view with any persist values.
                tokens = _get_persist_tokens(view, False)
                if tokens is not None:
                    for token, tparams in tokens.items():
                        _highlight_view(view, token, tparams['whole_word'], tparams['scope'])


    def on_load(self):
        ''' Called when file loaded. '''
        view = self.view
        trace(TraceCat.LOAD, 'HighlightEvent.on_load', view.file_name(), view.id(), view.window().project_file_name())


    def on_deactivated(self):
        ''' Save to file when focus/tab lost. '''
        view = self.view
        winid = view.window().id()
        trace(TraceCat.ACTV, 'HighlightEvent.on_deactivated', view.id(), winid)

        if winid in _hls:
            _save_hls(winid, view.window().project_file_name())


    def on_close(self):
        ''' Called when a view is closed. Note there may still be other views into the same buffer. '''
        view = self.view
        trace(TraceCat.LOAD, 'HighlightEvent.on_close', view.file_name(), view.id())


#-----------------------------------------------------------------------------------
class SbotHighlightTextCommand(sublime_plugin.TextCommand):
    ''' Highlight specific words using scopes. Parts borrowed from StyleToken.
    Persistence supported via sbot-project container.
    Note: Regions added by self.view.add_regions() can not set the foreground color. The scope color is used
    for the region background color. Also they are not available via extract_scope().
    '''

    def run(self, edit, hl_index):
        settings = sublime.load_settings(SETTINGS_FN)
        highlight_scopes = settings.get('highlight_scopes')

        # Get whole word or specific span.
        region = self.view.sel()[0]

        whole_word = region.empty()
        if whole_word:
            region = self.view.word(region)
        token = self.view.substr(region)

        hl_index %= len(highlight_scopes)
        scope = highlight_scopes[hl_index]
        tokens = _get_persist_tokens(self.view, True)

        if tokens is not None:
            tokens[token] = { "scope": scope, "whole_word": whole_word }
        _highlight_view(self.view, token, whole_word, scope)


#-----------------------------------------------------------------------------------
class SbotClearHighlightsCommand(sublime_plugin.TextCommand):
    ''' Clear all in this file.'''

    def run(self, edit):
        global _hls

        # Clean displayed colors.
        settings = sublime.load_settings(SETTINGS_FN)
        highlight_scopes = settings.get('highlight_scopes')

        for i, value in enumerate(highlight_scopes):
            reg_name = HIGHLIGHT_REGION_NAME % value
            self.view.erase_regions(reg_name)

        # Remove from persist collection.
        winid = self.view.window().id()
        fn = self.view.file_name()
        del _hls[winid][fn]


#-----------------------------------------------------------------------------------
def _save_hls(winid, stp_fn):
    ''' General project saver. '''
    ok = True
    ppath = get_persistence_path(stp_fn, HIGHLIGHT_FILE_EXT)

    if ppath is not None:
        try:
            # Remove invalid files and any empty values.
            if winid in _hls:
                for fn, _ in _hls[winid].items():
                    if not os.path.exists(fn):
                        del _hls[winid][fn]
                    elif len(_hls[winid][fn]) == 0:
                        del _hls[winid][fn]

                # Now save.
                with open(ppath, 'w') as fp:
                    json.dump(_hls[winid], fp, indent=4)

        except Exception as e:
            unhandled_exception('Save highlights error', e)
            ok = False

    return ok


#-----------------------------------------------------------------------------------
def _open_hls(winid, stp_fn):
    ''' General project opener. '''
    global _hls
    ok = True
    ppath = get_persistence_path(stp_fn, HIGHLIGHT_FILE_EXT)

    if ppath is not None:
        try:
            with open(ppath, 'r') as fp:
                values = json.load(fp)
                _hls[winid] = values

        except FileNotFoundError as fe:
            # Assumes new file.
            sublime.status_message('Creating new highlights file')
            _hls[winid] = { }

        except Exception as e:
            unhandled_exception('Open highlights error', e)
            ok = False

    return ok


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
def _get_persist_tokens(view, init_empty):
    ''' General helper to get the data values from collection. If init_empty and there are none, add a default value. '''
    global _hls
    vals = None # Default
    winid = view.window().id()
    fn = view.file_name()

    if winid in _hls:
        if fn not in _hls[winid]:
            if init_empty:
                # Add a new one.
                _hls[winid][fn] = {}
                vals = _hls[winid][fn]
        else:
            vals = _hls[winid][fn]

    return vals
