import os
import sys
import re
import sublime
import sublime_plugin
import sbot_common


#-----------------------------------------------------------------------------------
def _dosub(v, e, reo, sub):
    # Generic substitution function. TODO1 if no selections, process all? That's what st does. setting?

    for reg in v.sel():
        orig = v.substr(reg)
        new = reo.sub(sub, orig)
        if orig != new: #TODO1 efficient?
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
        _dosub(self.view, edit, reo, sub)


#-----------------------------------------------------------------------------------
class SbotRemoveEmptyLinesCommand(sublime_plugin.TextCommand):
    def run(self, edit, normalize):
        if normalize:
            reo = re.compile(r'(?:\s*)(\r?\n)(?:\s*)(?:\r?\n+)', re.MULTILINE)
            sub = r'\1\1'
        else:
            reo = re.compile('^[ \t]*$\r?\n', re.MULTILINE)
            sub = ''
        _dosub(self.view, edit, reo, sub)


#-----------------------------------------------------------------------------------
class SbotRemoveWsCommand(sublime_plugin.TextCommand):
    def run(self, edit, normalize):
        if normalize:
            reo = re.compile('([ ])[ ]+')
            sub = r'\1'
        else:
            reo = re.compile(r'[ \t\r\n\v\f]')
            sub = ''
        _dosub(self.view, edit, reo, sub)

