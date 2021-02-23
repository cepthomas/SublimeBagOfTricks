import os
import sys
# import time
# import logging
import re
# import math
# import textwrap
# import webbrowser
# from html import escape
import sublime
import sublime_plugin
import sbot_common


"""

> [Trimmer](https://github.com/jonlabelle/Trimmer) is a [Sublime Text](http://www.sublimetext.com) plug-in for cleaning up whitespace.
### Trimmer Command API

|              Command               |                                              Description                                               |          Context          |
|------------------------------------|--------------------------------------------------------------------------------------------------------|---------------------------|
| `trim_trailing          | trim whitespace at the end of each line                                                   | entire file               |
| `trim_leading`          | trim whitespace at the start of each line                                                 | selection, or entire file |
| `trim` | trim whitespace at the start and end of each line                                         | selection, or entire file |
| `trim_selections`                  | trim whitespace from selection(s)                             | selection                 |
| `delete_empty_lines`               | delete empty, whitespace only lines                           | selection, or entire file |
| `collapse_lines`                   | collapse multiple consecutive empty lines into one empty line | selection, or entire file |
| `collapse_spaces`                  | collapse multiple consecutive spaces into one space           | selection, or entire file |
| `remove_blank_spaces`              | remove all blank space characters (tab, cr, ff, vt, space)    | selection, or entire file |


    { "caption": "Trim Both Ends WS", "command": "sbot_trim_both" },
    { "caption": "Trim Trailing WS", "command": "sbot_trim_trailing" },
    { "caption": "Trim Leading WS", "command": "sbot_trim_leading" },
    
    // { "caption": "Trim selections", "command": "trim_selections" },

    { "caption": "Remove Empty Lines", "command": "sbot_remove_empty_lines", "args" : {"residual" : 0} },
    { "caption": "Remove WS", "command": "sbot_remove_ws", "args" : {"residual" : 0} },
    // { "caption": "Collapse lines", "command": "collapse_lines" },
    // { "caption": "Collapse spaces", "command": "collapse_spaces" },

    { "caption": "Find Non-ascii", "command": "sbot_find_non_ascii" },
    { "caption": "Replace Non-ascii", "command": "sbot_replace_non_ascii", "args" : {"repval" : ""} },



## Author

[Jon LaBelle](https://jonlabelle.com)

## License

Trimmer is licensed under the [MIT license](http://opensource.org/licenses/MIT).
"""


"""
TODOC - display/remove non-ascii
    - like binsniff.cs
    - ??? RemoveNonAsciiChars.sublime-package - uses unicodedata.normalize()
sbot_find_non_ascii
sbot_replace_non_ascii  ,,remove
"""


# TODOC Sublime Text uses the Perl Compatible Regular Expressions (PCRE) engine from the Boost library to power regular expressions in search panels.
# Here’s the link:
# https://www.boost.org/doc/libs/1_69_0/libs/regex/doc/html 16


#-----------------------------------------------------------------------------------
def selections(v, default_to_all=True):
    regions = [r for r in v.sel() if not r.empty()]
    if not regions and default_to_all:
        regions = [sublime.Region(0, v.size())]
    return regions


#-----------------------------------------------------------------------------------
class SbotTrimTrailingCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        v = self.view
        regions = v.find_all('[\t ]+$')
        regions.reverse()
        for region in regions:
            v.erase(edit, region)


#-----------------------------------------------------------------------------------
class SbotTrimLeadingCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        v = self.view
        reobj = re.compile('^[ \t]+', re.MULTILINE)
        for region in selections(v):
            str_buffer = v.substr(region)
            trimmed = reobj.sub('', str_buffer)
            if str_buffer != trimmed:
                v.replace(edit, region, trimmed)


#-----------------------------------------------------------------------------------
class SbotTrimBothCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        v = self.view
        reobj = re.compile('^[ \t]+|[\t ]+$', re.MULTILINE)
        for region in selections(v):
            str_buffer = v.substr(region)
            trimmed = reobj.sub('', str_buffer)
            if str_buffer != trimmed:
                v.replace(edit, region, trimmed)


#-----------------------------------------------------------------------------------
class SbotRemoveEmptyLinesCommand(sublime_plugin.TextCommand):
    def run(self, edit, residual):
        v = self.view
        reobj = re.compile('^[ \t]*$\r?\n', re.MULTILINE)
        for region in selections(v):
            str_buffer = v.substr(region)
            trimmed = reobj.sub('', str_buffer)
            if str_buffer != trimmed:
                v.replace(edit, region, trimmed)


#-----------------------------------------------------------------------------------
class SbotCollapseLinesCommand(sublime_plugin.TextCommand): # TODOC combine with SbotRemoveEmptyLinesCommand
    def run(self, edit):
        v = self.view
        reobj = re.compile(r'(?:\s*)(\r?\n)(?:\s*)(?:\r?\n+)')
        for region in selections(v):
            str_buffer = v.substr(region)
            trimmed = reobj.sub(r'\1\1', str_buffer)
            if str_buffer != trimmed:
                v.replace(edit, region, trimmed)


#-----------------------------------------------------------------------------------
class SbotRemoveWsCommand(sublime_plugin.TextCommand):
    def run(self, edit, residual):
        v = self.view
        reobj = re.compile(r'[ \t\r\n\v\f]')
        for region in selections(v):
            str_buffer = v.substr(region)
            trimmed = reobj.sub('', str_buffer)
            if str_buffer != trimmed:
                v.replace(edit, region, trimmed)


#-----------------------------------------------------------------------------------
class SbotCollapseSpacesCommand(sublime_plugin.TextCommand): # TODOC combine with SbotRemoveWsCommand
    def run(self, edit):
        v = self.view
        reobj = re.compile('([ ])[ ]+')
        for region in selections(v):
            str_buffer = v.substr(region)
            trimmed = reobj.sub(r'\1', str_buffer)
            if str_buffer != trimmed:
                v.replace(edit, region, trimmed)


#-----------------------------------------------------------------------------------
class SbotFindNonAsciiCommand(sublime_plugin.TextCommand): # TODOC
    def run(self, edit):
        v = self.view


#-----------------------------------------------------------------------------------
class SbotReplaceNonAsciiCommand(sublime_plugin.TextCommand): # TODOC
    def run(self, edit, repval):
        v = self.view


#-----------------------------------------------------------------------------------
class SbotTrimSelectionsXXX(sublime_plugin.TextCommand): #TODOC example of brute force way.
    def run(self, edit):
        """
        Trim leading and trailing whitespace from selections.
        Originally from the 'Multi​Edit​Utils' Plug-in >>>>>>> https://github.com/philippotto/Sublime-MultiEditUtils
        """
        v = self.view
        selection = v.sel()
        new_regions = []

        for current_region in selection:
            text = v.substr(current_region)

            l_stripped_text = text.lstrip()
            r_stripped_text = l_stripped_text.rstrip()

            l_stripped_count = len(text) - len(l_stripped_text)
            r_stripped_count = len(l_stripped_text) - len(r_stripped_text)

            a = current_region.begin() + l_stripped_count
            b = current_region.end() - r_stripped_count

            if a == b:
                # the region only contained whitespace
                # use the old selection end to avoid jumping of cursor
                a = b = current_region.b

            new_regions.append(sublime.Region(a, b))

        selection.clear()
        for region in new_regions:
            selection.add(region)
