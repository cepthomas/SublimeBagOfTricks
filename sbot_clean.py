import os
import sys
import re
import sublime
import sublime_plugin
import sbot_common
import sbot_misc



#-----------------------------------------------------------------------------------
def _do_sub(v, e, reo, sub):
    # Generic substitution function.
    regions = sbot_misc.get_regions(v)
    for reg in regions:
        orig = v.substr(reg)
        new = reo.sub(sub, orig)
        if orig != new: #TODO efficient to do this strcmp every time? Profile.
            v.replace(e, reg, new)


#-----------------------------------------------------------------------------------
class SbotTrimCommand(sublime_plugin.TextCommand):
    def run(self, edit, which):
        sub = ''
        if which == 'leading':
            reo = re.compile('^[ \t]+', re.MULTILINE)
        elif which == 'trailing':
            reo = re.compile('[\t ]+$', re.MULTILINE)
        else: # both
            reo = re.compile('^[ \t]+|[\t ]+$', re.MULTILINE)
        _do_sub(self.view, edit, reo, sub)


#-----------------------------------------------------------------------------------
class SbotRemoveEmptyLinesCommand(sublime_plugin.TextCommand):
    def run(self, edit, normalize):
        if normalize:
            reo = re.compile(r'(?:\s*)(\r?\n)(?:\s*)(?:\r?\n+)', re.MULTILINE)
            sub = r'\1\1'
        else:
            reo = re.compile('^[ \t]*$\r?\n', re.MULTILINE)
            sub = ''
        _do_sub(self.view, edit, reo, sub)


#-----------------------------------------------------------------------------------
class SbotRemoveWsCommand(sublime_plugin.TextCommand):
    def run(self, edit, normalize):
        if normalize:
            reo = re.compile('([ ])[ ]+')
            sub = r'\1'
        else:
            reo = re.compile(r'[ \t\r\n\v\f]')
            sub = ''
        _do_sub(self.view, edit, reo, sub)

