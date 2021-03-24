import unittest
import unittest.mock
import sublime
#import sublime_plugin
import sbot
import sbot_common


    
# from unittest.mock import create_autospec
#def function(a, b, c):
#    pass

#mock_function = unittest.mock.create_autospec(function, return_value='fishy')
#mock_function(1, 2, 3)

#mock_function.assert_called_once_with(1, 2, 3)
##mock_function('wrong arguments')


class TestCommon(unittest.TestCase):
    def setUp(self):
        sbot.plugin_loaded()

    def tearDown(self):
        sbot.plugin_unloaded()

    def test_sbot(self):
        '''Also has tests for the simple sbot.py.'''
        # self.assertEqual('foo'.upper(), 'FOO')

        view = sublime.View(600)
        evt = sbot.SbotEvent()
        evt.on_selection_modified(view)




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


# if __name__ == '__main__':
#     unittest.main()
