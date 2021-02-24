import os
import sys
import re
import sublime
import sublime_plugin
import sbot_common


#-----------------------------------------------------------------------------------
def _dosub(v, e, reo, sub):
    # Generic substitution function. TODO2 if no selections, process all?

    for reg in v.sel():
        orig = v.substr(reg)
        new = reo.sub(sub, orig)
        if orig != new: #TODO2 efficient?
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


#-----------------------------------------------------------------------------------
class SbotFindNonAsciiCommand(sublime_plugin.TextCommand): # TODO1 prob need a real hex editor
    def run(self, edit, mode): # find replace
        v = self.view

        find = []

        reg = sublime.Region(0, v.size())
        s = v.substr(reg)

        row = 1
        col = 1

        if mode == 'replace':
            sys.stdout.write('----------- replace non-ascii ---------------\n')

        for c in s:
            if c == '\n':
                # Valid.
                if mode == 'replace':
                    sys.stdout.write(r'<\n>')
                row += 1
                col += 1
            elif c == '\r':
                # Valid.
                if mode == 'replace':
                    sys.stdout.write(r'<\r>')
                col = 1
            elif c == '\t':
                # Valid.
                if mode == 'replace':
                    sys.stdout.write(r'<\t>')
                col += 1
            elif c < ' ' or c > '~': # 32  SPACE  126  ~
                # Invalid.
                if mode == 'replace':
                    sys.stdout.write('<{}>'.format(c))
                else:
                    find.append('row:{} col:{} i:{}'.format(row, col, c))
                col += 1
            else:
                # Valid.
                if mode == 'replace':
                    sys.stdout.write(c)
                col += 1

                
        if mode == 'find':
            sys.stdout.write('----------- find non-ascii ---------------\n')
            for d in find:
                sys.stdout.write(d)
                sys.stdout.write('\n')
