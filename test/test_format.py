import sys
import unittest
from unittest.mock import MagicMock
import sublime
import sbot_format



class TestFormat(unittest.TestCase):

    def setUp(self):
        sbot_format.plugin_loaded()

    def tearDown(self):
        sbot_format.plugin_unloaded()

    def test_format_json(self):
        v = sublime.View(601)

        with open(r'.\files\test.json', 'r') as fp:
            # The happy path.
            s = fp.read()
            cmd = sbot_format.SbotFormatJsonCommand(v)
            res = cmd._do_one(s)
            self.assertEqual(res[:50], '{\n    "MarkPitch": {\n        "Original": 0,\n      ')

            # Make it a bad file.
            s = s.replace('\"Original\"', '')
            res = cmd._do_one(s)
            self.assertEqual(res[:50], "Error: ('Expecting property name enclosed in doubl")

    def test_format_xml(self):
        v = sublime.View(602)

        with open(r'.\files\test.xml', 'r') as fp:
            # The happy path.
            s = fp.read()
            cmd = sbot_format.SbotFormatXmlCommand(v)
            res = cmd._do_one(s)
            self.assertEqual(res[100:150], 'ype="Anti-IgG (PEG)" TestSpec="08 ABSCR4 IgG" Dump')

            # Make it a bad file.
            s = s.replace('ColumnType=', '')
            res = cmd._do_one(s)
            self.assertEqual(res, "Error: ('not well-formed (invalid token): line 6, column 4',)")


if __name__ == '__main__':
    unittest.main()
