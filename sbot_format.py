import sys
import json
import string
import sublime_plugin
import sbot_common


# print('Load sbot_format')

_has_lxml = False
modulename = 'lxml'
#print(sys.modules)
if modulename in sys.modules:
    _has_lxml = True


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

    def is_visible(self):
        # return self.view.settings().get('syntax').endswith('JSON.sublime-syntax')
        return True

    def run(self, edit):
        sres = []
        err = False

        for reg in sbot_common.get_sel_regions(self.view):
            s = self.view.substr(reg)
            s = self._do_one_region(s)
            sres.append(s)
            if s.startswith('Error'):
                err = True
                break

        vnew = sbot_common.create_new_view(self.view.window(), '\n'.join(sres))

        if not err:
            vnew.set_syntax_file('Packages/JavaScript/JSON.sublime-syntax')

    def _do_one_region(self, s):
        ''' Clean and reformat the string. Returns the new string. '''

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

                # Prefilter and update position.
                # if current_char == -1:
                #     state = SS_DONE
                # elif current_char == '\n':
                #     originalLine++
                #     originalColumn = 0
                # elif current_char == '\r':
                #     originalColumn = 0
                # elif current_char == '\t':
                #     originalColumn = ((originalColumn / tabWidth) + 1) * tabWidth
                # else:
                #     originalColumn += 1


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

                i += 1

            # Prep for formatting.
            ret = ''.join(sreg)
            # Remove any trailing commas.
            ret = ret.replace(",}", "}").replace(",]", "]")
            # Run it through the formatter. If there are errors they will be caught and handled by the caller.
            #print(ret)
            ret = json.loads(ret)
            ret = json.dumps(ret, indent=4) #, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
        except json.JSONDecodeError as je:
            ret = 'Error: {}'.format(je.args)
        except Exception as e:
            ret = 'Error: {}'.format(e.args)

        return ret


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
        view = self.view

    def is_visible(self):
        return _has_lxml and self.view.settings().get('syntax').endswith('XML.sublime-syntax')


#-----------------------------------------------------------------------------------
class SbotFormatHtmlCommand(sublime_plugin.TextCommand):
    ''' sbot_format_html'''

    def run(self, edit):
        # Like xml.
        view = self.view

    def is_visible(self):
        return _has_lxml and self.view.settings().get('syntax').endswith('HTML.sublime-syntax')
