import unittest
import sublime
#import sublime_plugin
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

        v = sublime.View(600)
        evt = sbot.SbotEvent()
        evt.on_selection_modified(v)

        # TODO-T sbot_common stuff:
        # def trace(*args, cat=None):
        # # Check for file size limit.
        # def error(info, exc):
        # def get_sel_regions(v):
        # ''' Generic function to get selections or optionally the whole view.'''
        # def create_new_view(window, text):
        # ''' Creates a temp view with text. Returns the view.'''
        # def write_to_console(text):
        # ''' This is crude but works. Sublime also adds an extra eol when writing to the console. '''
        # def dump_view(preamble, view):
        # ''' Helper util. '''
        # def wait_load_file(view, line):
        # ''' Open file asynchronously then position at line. '''
        # class SbotPerfCounter(object):
        # ''' Container for perf counter. All times in msec. '''


if __name__ == '__main__':
    unittest.main()
