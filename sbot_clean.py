import os
import sys
import re
import sublime
import sublime_plugin
import sbot_common
import sbot_misc



#-----------------------------------------------------------------------------------
def _do_sub(view, edit, reo, sub):
    # Generic substitution function.
    regions = sbot_misc.get_sel_regions(view)
    for reg in regions:
        orig = view.substr(reg)
        new = reo.sub(sub, orig)
        view.replace(edit, reg, new)


#-----------------------------------------------------------------------------------
class SbotTrimCommand(sublime_plugin.TextCommand):
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
    def run(self, edit, how):
        if how == 'normalize':
            reo = re.compile(r'(?:\s*)(\r?\n)(?:\s*)(?:\r?\n+)', re.MULTILINE)
            sub = r'\1\1'
        else:
            reo = re.compile('^[ \t]*$\r?\n', re.MULTILINE)
            sub = ''
        _do_sub(self.view, edit, reo, sub)


#-----------------------------------------------------------------------------------
class SbotRemoveWsCommand(sublime_plugin.TextCommand):
    def run(self, edit, how):
        if how == 'normalize':
            reo = re.compile('([ ])[ ]+')
            sub = r'\1'
        elif how == 'keep_eol':
            reo = re.compile(r'[ \t\v\f]')
            sub = ''
        else:
            reo = re.compile(r'[ \t\r\n\v\f]')
            sub = ''
        _do_sub(self.view, edit, reo, sub)

