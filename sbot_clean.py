import re
#import sublime
import sublime_plugin
from sbot_common import *

# print('Load sbot_clean')


#-----------------------------------------------------------------------------------
def _do_sub(view, edit, reo, sub):
    # Generic substitution function.
    sels = get_sel_regions(view)
    for sel in sels:
        orig = view.substr(sel)
        new = reo.sub(sub, orig)
        view.replace(edit, sel, new)


#-----------------------------------------------------------------------------------
class SbotTrimCommand(sublime_plugin.TextCommand):
    '''sbot_trim how=leading|trailing|both'''

    def run(self, edit, how):
        # breakpoint()
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
            # Note: doesn't trim trailing.
            reo = re.compile('([ ])[ ]+')
            sub = r'\1'
        elif how == 'keep_eol':
            reo = re.compile(r'[ \t\v\f]')
            sub = ''
        else: # remove_all
            reo = re.compile(r'[ \t\r\n\v\f]')
            sub = ''
        _do_sub(self.view, edit, reo, sub)


#-----------------------------------------------------------------------------------
class SbotInsertLineIndexesCommand(sublime_plugin.TextCommand):
    ''' Insert sequential numbers in first column. Default is to start at 1. '''

    def run(self, edit):
        # Iterate lines.
        line_count = self.view.rowcol(self.view.size())[0]
        width = len(str(line_count))
        offset = 0

        for region in get_sel_regions(self.view):
            line_num = 1
            offset = 0
            for line_region in self.view.split_by_newlines(region):
                s = "{:0{size}} ".format(line_num, size=width)
                self.view.insert(edit, line_region.a + offset, s)
                line_num += 1
                # Adjust for inserts.
                offset += width+1
