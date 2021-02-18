import os
import sublime
import sublime_plugin


def initialize():
    global settings
    #TODOC not the best place for these:
    global HIGHLIGHT_REGION_NAME
    global MAX_HIGHLIGHTS

    settings = None
    HIGHLIGHT_REGION_NAME = 'highlight_%s'
    MAX_HIGHLIGHTS = 6

