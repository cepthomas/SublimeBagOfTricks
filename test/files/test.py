import os
import sys
import re
import sublime
import sublime_plugin
from sbot_common import *



#-----------------------------------------------------------------------------------
def _do_sub(view, edit, reo, sub):
    # Generic substitution function.
    regions = sbot_common.get_sel_regions(view)
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
