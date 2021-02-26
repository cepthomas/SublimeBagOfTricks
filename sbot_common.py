import os
import sublime
import sublime_plugin

# Vars shared across project.

def initialize():
    global settings
    settings = sublime.load_settings('SublimeBagOfTricks.sublime-settings')
