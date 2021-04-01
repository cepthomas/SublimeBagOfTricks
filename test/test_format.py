import sys
import unittest
#import unittest.mock
from unittest.mock import MagicMock
import sublime
#import sublime_plugin
import sbot_format



class TestFormatJson(unittest.TestCase):
    def setUp(self):
        sbot_format.plugin_loaded()

    def tearDown(self):
        sbot_format.plugin_unloaded()

    def test_json_clean_comments_commas(self):
        '''The happy path.'''

        view = sublime.View(601)

        with open(r'.\files\test.json', 'r') as fp:
            s = fp.read()

            #sel = sublime.Selection(view.id())
            #sel.add(sublime.Region(0, len(s), 0))
            #view.sel = MagicMock(return_value = sel)

            cmd = sbot_format.SbotFormatJsonCommand(view)

            res = cmd._do_one_region(s)

            print(res)








    def test_xml(self):
        '''Also has tests for the simple sbot.py.'''
        # self.assertEqual('foo'.upper(), 'FOO')

        v = sublime.View(602)

        # class SbotFormatXmlCommand(sublime_plugin.TextCommand):
        #     def run(self, edit):
        #         # Installation: pip3 install lxml.
        #         v = self.view
        #     def is_visible(self):

    def test_html(self):
        '''Also has tests for the simple sbot.py.'''
        # self.assertEqual('foo'.upper(), 'FOO')

        v = sublime.View(603)

        # class SbotFormatHtmlCommand(sublime_plugin.TextCommand):
        #     def run(self, edit):
        #         v = self.view
        #     def is_visible(self):


if __name__ == '__main__':
    unittest.main()
