import os
import sys
import re
import sublime
import sublime_plugin
import sbot_common


# [Trimmer](https://github.com/jonlabelle/Trimmer) is a [Sublime Text](http://www.sublimetext.com) plug-in for cleaning up whitespace.
# [Jon LaBelle](https://jonlabelle.com)
# Trimmer is licensed under the [MIT license](http://opensource.org/licenses/MIT).


#-----------------------------------------------------------------------------------
def _dosub(v, e, reobj, sub):
    regions = [r for r in v.sel() if not r.empty()]  #TODOC global setting?
    if not regions and default_to_all:
        regions = [sublime.Region(0, v.size())]

    for region in regions:
        orig = v.substr(region)
        trimmed = reobj.sub('', orig)
        if orig != trimmed: #TODOC efficient?
            v.replace(e, region, trimmed)


#-----------------------------------------------------------------------------------
class SbotTrimCommand(sublime_plugin.TextCommand):
    def run(self, edit, which):
        if which == 'leading':
            reobj = re.compile('^[ \t]+', re.MULTILINE)
        elif which == 'trailing':
            reobj = re.compile('[\t ]+$', re.MULTILINE)
        else: # both
            reobj = re.compile('^[ \t]+|[\t ]+$', re.MULTILINE)
        _dosub(self.view, edit, reobj, '')


#-----------------------------------------------------------------------------------
class SbotRemoveEmptyLinesCommand(sublime_plugin.TextCommand):
    def run(self, edit, collapse):
        if collapse: #TODOC not quite right
            reobj = re.compile(r'(?:\s*)(\r?\n)(?:\s*)(?:\r?\n+)')
            sub = r'\1\1'
        else:
            reobj = re.compile('^[ \t]*$\r?\n', re.MULTILINE)
            sub = ''
        _dosub(self.view, edit, reobj, sub)


#-----------------------------------------------------------------------------------
class SbotRemoveWsCommand(sublime_plugin.TextCommand):
    def run(self, edit, collapse):
        if collapse:
            reobj = re.compile('([ ])[ ]+')
            sub = r'\1'
        else:
            reobj = re.compile(r'[ \t\r\n\v\f]')
            sub = ''
        _dosub(self.view, edit, reobj, sub)


#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
class SbotFindNonAsciiCommand(sublime_plugin.TextCommand): # TODOC
    def run(self, edit, replval): #replval=None if cump
        v = self.view
# class SbotTrimSelectionsXXXXCommand(sublime_plugin.TextCommand): #TODOC example of brute force way.
#     def run(self, edit):
#         """
#         Trim leading and trailing whitespace from selections.
#         Originally from the 'Multi​Edit​Utils' Plug-in >>>>>>> https://github.com/philippotto/Sublime-MultiEditUtils
#         """
#         v = self.view
#         sel = v.sel()
#         new_regions = []
#         for reg in sel:
#             text = v.substr(reg)
#             l_stripped_text = text.lstrip()
#             r_stripped_text = l_stripped_text.rstrip()
#             l_stripped_count = len(text) - len(l_stripped_text)
#             r_stripped_count = len(l_stripped_text) - len(r_stripped_text)
#             a = reg.begin() + l_stripped_count
#             b = reg.end() - r_stripped_count
#             if a == b:
#                 # the region only contained whitespace
#                 # use the old sel end to avoid jumping of cursor
#                 a = b = reg.b
#             new_regions.append(sublime.Region(a, b))
#         sel.clear()
#         for region in new_regions:
#             sel.add(region)
