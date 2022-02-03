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

    def test_persistence_path(self):
        settings = sublime.load_settings(SETTINGS_FN)
        settings.set('persistence_path', 'local')
        pers_path = get_persistence_path('abc123.sublime-project', '.xyz')
        self.assertEqual(pers_path, "abc123.xyz")

        settings.set('persistence_path', 'store')
        pers_path = get_persistence_path('abc123.sublime-project', '.xyz')
        self.assertEqual(pers_path, r"C:\Users\cepth\AppData\Roaming\Sublime Text\Packages\SublimeBagOfTricks\store\abc123.xyz")

    def test_trace_error(self):
        try:
            raise Exception('arg1', 'arg2', 'arg3')
        except Exception as e:
            plugin_exception(e)

if __name__ == '__main__':
    unittest.main()
