import unittest
from unittest.mock import MagicMock
import sublime
import sbot
import sbot_common



class TestCommon(unittest.TestCase):
    def setUp(self):
        sbot.plugin_loaded()

    def tearDown(self):
        sbot.plugin_unloaded()

    def test_sbot(self):
        '''Also has tests for the simple sbot.py.'''
        # self.assertEqual('foo'.upper(), 'FOO')

        view = sublime.View(600)

        sel = sublime.Selection(view.id())
        sel.add(sublime.Region(10, 20, 101))
        view.sel = MagicMock(return_value = sel)

        evt = sbot.SbotEvent()
        evt.on_selection_modified(view)

        #self.assertEqual(1, 2, 'just a test test')


if __name__ == '__main__':
    unittest.main()
