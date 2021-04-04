import sys
import unittest
from unittest.mock import MagicMock
import sublime
import sbot_format



class TestFormatJson(unittest.TestCase):

    def setUp(self):
        sbot_format.plugin_loaded()

    def tearDown(self):
        sbot_format.plugin_unloaded()

    def test_json_clean_comments_commas(self):
        '''The happy path.'''
        v = sublime.View(601)

        with open(r'.\files\test.json', 'r') as fp:
            # The happy path.
            s = fp.read()
            #print('000000', s)
            cmd = sbot_format.SbotFormatJsonCommand(v)
            res = cmd._do_one_region(s)
            self.assertEqual(res[:50], '{\n    "MarkPitch": {\n        "Original": 0,\n      ')

            # Make it a bad file.
            s = s.replace('\"Original\"', '')
            res = cmd._do_one_region(s)
            self.assertEqual(res[:50], "Error: ('Expecting property name enclosed in doubl")

    def test_xml(self):
        '''Also has tests for the simple sbot.py.'''
        v = sublime.View(602)

        # class SbotFormatXmlCommand(sublime_plugin.TextCommand):
        #     def run(self, edit):
        #         # Installation: pip3 install lxml.
        #         v = self.v
        #     def is_visible(self):

    def test_html(self):
        '''Also has tests for the simple sbot.py.'''
        # self.assertEqual('foo'.upper(), 'FOO')

        v = sublime.View(603)

        # class SbotFormatHtmlCommand(sublime_plugin.TextCommand):
        #     def run(self, edit):
        #         v = self.v
        #     def is_visible(self):


if __name__ == '__main__':
    unittest.main()
