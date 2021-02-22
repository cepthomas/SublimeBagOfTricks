import os
import sublime
import sublime_plugin

# Vars shared across project.

def initialize():
    global settings
    settings = None

