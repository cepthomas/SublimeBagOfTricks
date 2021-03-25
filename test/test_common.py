import unittest
#import unittest.mock
from unittest.mock import MagicMock
import sublime
#import sublime_plugin
import sbot
import sbot_common



# from unittest.mock import create_autospec
#def function(a, b, c):
#    pass
#
#mock_function = unittest.mock.create_autospec(function, return_value='fishy')
#mock_function(1, 2, 3)
#
#mock_function.assert_called_once_with(1, 2, 3)
##mock_function('wrong arguments')


#from unittest.mock import MagicMock
#thing = ProductionClass()
#thing.method = MagicMock(return_value=3)
#thing.method(3, 4, 5, key='value')

#thing.method.assert_called_with(3, 4, 5, key='value')




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

        self.assertEqual(1, 2, 'just a test test')




# TODO-T sbot_common stuff:
# def trace(*args, cat=None):
# # Check for file size limit.
# def error(info, exc):
# def get_sel_regions(view):
# def create_new_view(window, text):
# def write_to_console(text):
# def dump_view(preamble, view):
# def wait_load_file(view, line):
# class SbotPerfCounter(object):


if __name__ == '__main__':
    unittest.main()
