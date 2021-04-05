import re
#import sublime
import sublime_plugin
import sbot_common

# print('Load sbot_clean')


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. '''
    sbot_common.trace('plugin_loaded sbot_clean')


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    ''' Clean up module global stuff. '''
    sbot_common.trace('plugin_unloaded sbot_clean')


#-----------------------------------------------------------------------------------
def _do_sub(view, edit, reo, sub):
    # Generic substitution function.
    sels = sbot_common.get_sel_regions(view)
    for sel in sels:
        orig = view.substr(sel)
        new = reo.sub(sub, orig)
        view.replace(edit, sel, new)


#-----------------------------------------------------------------------------------
class SbotTrimCommand(sublime_plugin.TextCommand):
    '''sbot_trim how=leading|trailing|both'''

    def run(self, edit, how):
        if how == 'leading':
            reo = re.compile('^[ \t]+', re.MULTILINE)
            sub = ''
        elif how == 'trailing':
            reo = re.compile('[\t ]+$', re.MULTILINE)
            sub = ''
        else: # both
            reo = re.compile('^[ \t]+|[\t ]+$', re.MULTILINE)
            sub = ''
        _do_sub(self.view, edit, reo, sub)


#-----------------------------------------------------------------------------------
class SbotRemoveEmptyLinesCommand(sublime_plugin.TextCommand):
    '''sbot_remove_empty_lines  how=remove_all|normalize'''

    def run(self, edit, how):
        if how == 'normalize':
            reo = re.compile(r'(?:\s*)(\r?\n)(?:\s*)(?:\r?\n+)', re.MULTILINE)
            sub = r'\1\1'
        else: # remove_all
            reo = re.compile('^[ \t]*$\r?\n', re.MULTILINE)
            sub = ''
        _do_sub(self.view, edit, reo, sub)


#-----------------------------------------------------------------------------------
class SbotRemoveWsCommand(sublime_plugin.TextCommand):
    '''sbot_remove_ws  how=remove_all|keep_eol|normalize'''

    def run(self, edit, how):
        if how == 'normalize':
            reo = re.compile('([ ])[ ]+')
            sub = r'\1'
        elif how == 'keep_eol':
            reo = re.compile(r'[ \t\v\f]')
            sub = ''
        else: # remove_all
            reo = re.compile(r'[ \t\r\n\v\f]')
            sub = ''
        _do_sub(self.view, edit, reo, sub)
