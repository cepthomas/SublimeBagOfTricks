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



