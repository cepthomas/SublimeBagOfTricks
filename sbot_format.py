
import os
import sys
import re
import json
import sublime
import sublime_plugin
import sbot_common
import sbot_misc


_has_lxml = False # TODO-ST4
try:
    import lxml
    _has_lxml = True
except Exception as e:
    # print(e)
    _has_lxml = False


#-----------------------------------------------------------------------------------
class SbotFormatJsonCommand(sublime_plugin.TextCommand):
    ''' sbot_format_json'''

    def run(self, edit):
        v = self.view

        sres = []
        serr = ''
        regions = sbot_misc.get_regions(v)

        try:
            for reg in regions:
                orig = v.substr(reg)
                parsed = json.loads(orig)
                sres.append(json.dumps(parsed, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))
        except Exception as e:
            has_err = True
            serr = 'Parse error: {}'.format(e.args)

        if len(serr) > 0:
            sublime.ok_cancel_dialog(serr)
        else:
            s = '\n'.join(sres)
            vnew = v.window().new_file()
            vnew.set_scratch(True)
            vnew.insert(edit, 0, s)

    # def is_visible(self):
    #     fn = self.view.file_name()
    #     vis = True
    #     return vis


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
        # fn = self.view.file_name()
        # vis = False if fn is None else self.view.file_name().endswith('.md')
        return _has_lxml


#-----------------------------------------------------------------------------------
class SbotFormatHtmlCommand(sublime_plugin.TextCommand):
    ''' sbot_format_html'''

    def run(self, edit):
        # Like xml.
        v = self.view

    def is_visible(self):
        # fn = self.view.file_name()
        # vis = False if fn is None else self.view.file_name().endswith('.md')
        return _has_lxml
