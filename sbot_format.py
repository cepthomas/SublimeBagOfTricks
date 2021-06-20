import sys
import json
import string
import re
import enum
import xml
import xml.dom.minidom
import sublime_plugin
from sbot_common import *


# print('Load sbot_format')

INDENT = '    '


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

        class ScanState(enum.IntFlag):
            DEFAULT = enum.auto()   # Idle
            STRING = enum.auto()    # Process a quoted string
            LCOMMENT = enum.auto()  # Processing a single line comment
            BCOMMENT = enum.auto()  # Processing a block/multiline comment
            DONE = enum.auto()      # Finito

        # tabWidth = 4
        comment_count = 0
        sreg = []
        state = ScanState.DEFAULT
        current_comment = []
        current_char = -1
        next_char = -1
        escaped = False

        # Index is in cleaned version, value is in original.
        pos_map = []

        #{"sublime_text": "*", "dependencies": [], "version": "1.1.9", "url": "https://github.com/wadetb/Sublime-Text-Advanced-CSV", "description": "Efficiently format, edit, arrange, and evaluate cells in CSV files", "platforms": ["*"]}

        # Iterate the string.
        try:
            slen = len(s)
            i = 0
            while i < slen:
                current_char = s[i]
                next_char = s[i + 1] if i < slen-1 else -1

                # Remove whitespace and transform comments into legal json.
                if state == ScanState.STRING:
                    sreg.append(current_char)
                    pos_map.append(i)
                    # Handle escaped chars.
                    if current_char == '\\':
                        escaped = True
                    elif current_char == '\"':
                        if not escaped: state = ScanState.DEFAULT
                        escaped = False
                    else:
                        escaped = False
                
                elif state == ScanState.LCOMMENT:
                    # Handle line comments.
                    if current_char == '\n':
                        # End of comment.
                        scom = ''.join(current_comment)
                        stag = f'\"//{comment_count}\":\"{scom}\",'
                        comment_count += 1
                        sreg.append(stag)
                        pos_map.append(i)
                        state = ScanState.DEFAULT
                        current_comment.clear()
                    elif current_char == '\r':
                        # ignore
                        pass
                    else:
                        # Maybe escape.
                        if current_char == '\"' or current_char == '\\':
                            current_comment.append('\\')
                        current_comment.append(current_char)

                elif state == ScanState.BCOMMENT:
                    # Handle block comments.
                    if current_char == '*' and next_char == '/':
                        # End of comment.
                        scom = ''.join(current_comment)
                        stag = f'\"//{comment_count}\":\"{scom}\",'
                        comment_count += 1
                        sreg.append(stag)
                        pos_map.append(i)
                        state = ScanState.DEFAULT
                        current_comment.clear()
                        i += 1 # Skip next char.
                    elif current_char == '\n' or current_char == '\r':
                        # ignore
                        pass
                    else:
                        # Maybe escape.
                        if current_char == '\"' or current_char == '\\':
                            current_comment.append('\\')
                        current_comment.append(current_char)

                elif state == ScanState.DEFAULT:
                    # Check for start of a line comment.
                    if current_char == '/' and next_char == '/':
                        state = ScanState.LCOMMENT
                        current_comment.clear()
                        i += 1 # Skip next char.
                    # Check for start of a block comment.
                    elif current_char == '/' and next_char == '*':
                        state = ScanState.BCOMMENT
                        current_comment.clear()
                        i += 1 # Skip next char.
                    elif current_char == '\"':
                        sreg.append(current_char)
                        pos_map.append(i)
                        state = ScanState.STRING
                    # Skip ws.
                    elif current_char not in string.whitespace:
                        sreg.append(current_char)
                        pos_map.append(i)

                else: # state == ScanState.DONE:
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
        except json.JSONDecodeError as je:
            # Get some context from the original string.
            context = []
            original_pos = pos_map[je.pos]
            start_pos = max(0, original_pos - 40)
            end_pos = min(len(s) - 1, original_pos + 40)
            context.append(f'Json Error: {je.msg} pos: {original_pos}')
            context.append(s[start_pos:original_pos])
            context.append('---------here----------')
            context.append(s[original_pos:end_pos])
            ret = '\n'.join(context)
        except Exception as e:
            ret = f'Other Error: {e.args}'

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
            ret = f'Error: {e.args}'

        return ret
