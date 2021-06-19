import sys
import json
import string
import re
import xml
import xml.dom.minidom
import sublime_plugin
from sbot_common import *


# print('Load sbot_format')

INDENT = '    '


# #-----------------------------------------------------------------------------------
# def plugin_loaded():
#     ''' Initialize module global stuff. '''
#    trace('plugin_loaded sbot_format')


# #-----------------------------------------------------------------------------------
# def plugin_unloaded():
#     ''' Clean up module global stuff. '''
#    trace('plugin_unloaded sbot_format')


#-----------------------------------------------------------------------------------
class SbotFormatJsonCommand(sublime_plugin.TextCommand):
    ''' sbot_format_json'''

    def is_visible(self):
        # return self.view.settings().get('syntax').endswith('JSON.sublime-syntax')
        return True

    def run(self, edit):
        sres = []
        err = False

        reg = get_sel_regions(self.view)[0]
        s = self.view.substr(reg)
        s = self._do_one(s)
        sres.append(s)
        if s.startswith('Error'):
            err = True

        vnew = create_new_view(self.view.window(), '\n'.join(sres))
        if not err:
            vnew.set_syntax_file('Packages/JavaScript/JSON.sublime-syntax')

    def _do_one(self, s):
        ''' Clean and reformat the string. Returns the new string. '''

        # TODOST4 Use enum ScanState { SS_STRING, SS_COMMENT, SS_DEFAULT, SS_DONE } 
        SS_DEFAULT = 0    # Idle
        SS_STRING = 1     # Process a quoted string
        SS_COMMENT = 2    # Processing a comment
        SS_DONE = 3       # Finito

        # tabWidth = 4
        comment_count = 0
        sreg = []
        state = SS_DEFAULT
        current_comment = []
        current_char = -1
        next_char = -1
        escaped = False

        # Iterate the string.
        try:
            slen = len(s)
            i = 0
            while i < slen:
                current_char = s[i]
                next_char = s[i + 1] if i < slen-1 else -1

                # Remove whitespace and transform comments into legal json.
                if state == SS_STRING:
                    sreg.append(current_char)
                    # Handle escaped chars.
                    if current_char == '\\':
                        escaped = True
                    elif current_char == '\"':
                        if not escaped: state = SS_DEFAULT
                        escaped = False
                    else:
                        escaped = False
                elif state == SS_COMMENT:
                    # Handle comments.
                    if current_char == '\n':
                        # End of comment.
                        scom = ''.join(current_comment)
                        stag = '\"//{}\":\"{}\",'.format(comment_count, scom)
                        comment_count += 1
                        sreg.append(stag)
                        state = SS_DEFAULT
                        current_comment.clear()
                    elif current_char == '\r':
                        # ignore
                        pass
                    else:
                        # Maybe escape.
                        if current_char == '\"' or current_char == '\\':
                            current_comment.append('\\')
                        current_comment.append(current_char)
                elif state == SS_DEFAULT:
                    # Check for start of a comment.
                    if current_char == '/' and next_char == '/':
                        state = SS_COMMENT
                        current_comment.clear()
                        # Skip next char.
                        i += 1
                    # Skip ws.
                    elif current_char not in string.whitespace:
                        sreg.append(current_char)
                else: # state == SS_DONE:
                    pass
                i += 1 # next

            # Prep for formatting.
            ret = ''.join(sreg)

            # Remove any trailing commas.
            ret = re.sub(',}','}', ret)
            ret = re.sub(',]',']', ret)

            # Run it through the formatter.
            ret = json.loads(ret)
            ret = json.dumps(ret, indent=4)
        #except json.JSONDecodeError as je:
        #    ret = 'Error: {}'.format(je.args)
        except Exception as e:
            ret = 'Error: {}'.format(e.args)
            # TODO help the user with the problem print(ret)

        return ret


#-----------------------------------------------------------------------------------
class SbotFormatXmlCommand(sublime_plugin.TextCommand):
    ''' sbot_format_xml'''

    def is_visible(self):
        return self.view.settings().get('syntax').endswith('XML.sublime-syntax')

    def run(self, edit):
        err = False

        reg = get_sel_regions(self.view)[0]
        s = self.view.substr(reg)
        s = self._do_one(s)
        if s.startswith('Error'):
            err = True

        vnew = create_new_view(self.view.window(), s)
        if not err:
            vnew.set_syntax_file('Packages/XML/XML.sublime-syntax')

    def _do_one(self, s):
        ''' Clean and reformat the string. Returns the new string. '''

        def clean(node):
            for n in node.childNodes:
                if n.nodeType == xml.dom.minidom.Node.TEXT_NODE:
                    if n.nodeValue:
                        n.nodeValue = n.nodeValue.strip()
                elif n.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
                    clean(n)

        try:
            top = xml.dom.minidom.parseString(s)
            clean(top)
            top.normalize()
            ret = top.toprettyxml(indent=INDENT)
        except Exception as e:
            ret = 'Error: {}'.format(e.args)

        return ret
