import os
import sys
import re
import json
import sublime
import sublime_plugin
import sbot_common


# print('Load sbot_format')

_has_lxml = False # TODOST4

try:
    import lxml
    _has_lxml = True
except Exception as e:
    # sbot_common.trace(e)
    _has_lxml = False


#-----------------------------------------------------------------------------------
def plugin_loaded():
    ''' Initialize module global stuff. '''
    sbot_common.trace('plugin_loaded sbot_format')


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    ''' Clean up module global stuff. '''
    sbot_common.trace('plugin_unloaded sbot_format')


#-----------------------------------------------------------------------------------
class SbotFormatJsonCommand(sublime_plugin.TextCommand):
    ''' sbot_format_json'''

    def run(self, edit):
        v = self.view

        sres = []

        try:
            for reg in sbot_common.get_sel_regions(v):
                s = v.substr(reg)
                s = json.loads(s)
                s = json.dumps(s, indent=4) #, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
                sres.append(s)
        except Exception as e:
            has_err = True
            sres.append('Parse error: {}'.format(e.args))

        vnew = sbot_common.create_new_view(v.window(), '\n'.join(sres))
        vnew.set_syntax_file('Packages/JavaScript/JSON.sublime-syntax')

    def is_visible(self):
        # return self.view.settings().get('syntax').endswith('JSON.sublime-syntax')
        return True


#-----------------------------------------------------------------------------------
class SbotFormatXmlCommand(sublime_plugin.TextCommand):
    ''' sbot_format_xml'''

    def run(self, edit):
        # Installation: pip3 install lxml.
        # Use lxml.etree.parse(source) to parse the XML file source and return an ElementTree object.
        # lxml.etree.tostring(element_or_tree, encoding="unicode" pretty_print=True) to pretty print the contents of the XML file,
        #   with element_or_tree as the result of the previous step.
        # tree = lxml.etree.parse("small.xml")
        # pretty = lxml.etree.tostring(tree, encoding="unicode", pretty_print=True)
        v = self.view

    def is_visible(self):
        return _has_lxml and view.settings().get('syntax').endswith('XML.sublime-syntax')


#-----------------------------------------------------------------------------------
class SbotFormatHtmlCommand(sublime_plugin.TextCommand):
    ''' sbot_format_html'''

    def run(self, edit):
        # Like xml.
        v = self.view

    def is_visible(self):
        return _has_lxml and self.view.settings().get('syntax').endswith('HTML.sublime-syntax')
