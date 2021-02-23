import os
import sys
import time
import logging
import math
import textwrap
import webbrowser
# from html import escape
import sublime
import sublime_plugin
import sbot_common

"""

- xml/html/json formatter: From *** indentxml (also does json), jsformat, htmlbeautify.
    https://www.askpython.com/python-modules/htmlparser-in-python
    https://docs.python.org/3/library/html.parser.html
sbot_format_json
sbot_format_xml
sbot_format_html


- trimmer:
    - Trim whitespace at the end of each line. "caption": "Trimmer: Trim trailing whitespace.", "command": "trimmer"
    - Trim whitespace at the start of each line.  "caption": "Trimmer: Trim leading whitespace.", "command": "trim_leading_whitespace"
    - Trim whitespace at the start and end of each line. "caption": "Trimmer: Trim leading AND trailing whitespace.",  "command": "trim_leading_trailing_whitespace"
    - Trim whitespace from selection(s).  "caption": "Trimmer: Trim selections.", "command": "trim_selections"
    - Delete empty, whitespace only lines.  "caption": "Trimmer: Delete empty lines.",  "command": "delete_empty_lines"
    - Collapse multiple consecutive empty lines into one empty line.  "caption": "Trimmer: Collapse lines.", "command": "collapse_lines"
    - Collapse multiple consecutive spaces into one space.  "caption": "Trimmer: Collapse spaces.", "command": "collapse_spaces"
    - Remove blank space characters.  "caption": "Trimmer: Remove blank spaces.", "command": "remove_blank_spaces"
collapse_lines
collapse_spaces
delete_empty_lines
remove_blank_spaces
trim_leading_trailing_whitespace
trim_leading_whitespace
trim_selections
trim_trailing_whitespace


- display/remove non-ascii
    - like binsniff.cs
    - ??? RemoveNonAsciiChars.sublime-package - uses unicodedata.normalize()
sbot_find_non_ascii
sbot_replace_non_ascii  ,,remove


"""  

#-----------------------------------------------------------------------------------
class SbotXyzCommand(sublime_plugin.TextCommand):
    ''' sbot_xyz.'''

    def is_visible(self):
        fn = self.view.file_name()
        vis = False if fn is None else self.view.file_name().endswith('.md')
        return vis

    def run(self, edit):
        v = self.view
        ##### Get prefs.
        md_background = sbot_common.settings.get('md_background', 'white')
        md_font_size = sbot_common.settings.get('md_font_size', 12)
        md_font_face = sbot_common.settings.get('md_font_face', 'Arial')

        html = []
        html.append("<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
        html.append("<style>body {{ background-color:{}; font-family:{}; font-size:{}; }}".format(md_background, md_font_face, md_font_size))
        html.append("</style></head><body>")

        html.append(v.substr(sublime.Region(0, v.size())))

        html.append("<!-- Markdeep: --><style class=\"fallback\">body{visibility:hidden;white-space:pre;font-family:monospace}</style><script src=\"markdeep.min.js\" charset=\"utf-8\"></script><script src=\"https://casual-effects.com/markdeep/latest/markdeep.min.js\" charset=\"utf-8\"></script><script>window.alreadyProcessedMarkdeep||(document.body.style.visibility=\"visible\")</script>")
        html.append("</body></html>")

        content = '\n'.join(html)

        _output_html(v, content)



