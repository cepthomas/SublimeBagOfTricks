import json
#import sublime
import sublime_plugin
import sbot_common


# print('Load sbot_extra')

# Holding tank for examples, leftovers, bits and pieces.


#-----------------------------------------------------------------------------------
class SbotTestCommand(sublime_plugin.TextCommand):
    ''' Just for hacking/testing. '''

    def run(self, edit, cmd=None):
        view = self.view


        # for sheet in window.sheets():
        #     sbot_common.trace('sheet:', sheet)
        # for view in window.views(): # These are in order L -> R.
        #     sbot_common.trace('active view:', window.get_view_index(view), view.file_name()) # (group, index)
        # get_project(v).dump() # These are not ordered like file.

        # # Phantom phun
        # image = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', 'test', 'mark1.bmp')
        # sbot_common.trace(image)
        # html = '<body><p>Hello!</p><img src="file://' + image + '" width="90" height="145"></body>'
        # self.phantset = sublime.PhantomSet(v, "test")
        # phant = sublime.Phantom(view.sel()[0], html, sublime.LAYOUT_BLOCK)
        # phants = []
        # phants.append(phant)
        # self.phantset.update(phants)

        # global global_thing
        # sbot_common.trace(global_thing)
        # global_thing['item' + str(len(global_thing) + 5)] = 1234
        # view.show_popup(str(global_thing))


        # if action == 'white_space':
        #     pname, pval1, pval2 = "draw_white_space", "all", "selection"
        # elif action == 'gutter':
        #     pname, pval1, pval2 = "gutter", False, True
        # elif action == 'line_no':
        #     pname, pval1, pval2 = "line_numbers", False, True
        # elif action == 'indent_guide':
        #     pname, pval1, pval2 = "draw_indent_guides", False, True
        # if pname:
        #     propertyValue = pval1 if view.settings().get(pname, pval1) != pval1 else pval2
        #     view.settings().set(pname, propertyValue)


        # with open(r'C:\Users\cepth\AppData\Roaming\Sublime Text 3\Packages\SublimeBagOfTricks\test\new_proj.json', 'r') as fp:
        #     o = json.load(fp)
        #     sigs = o['signets']
        #     hls = o['highlights']
        #     for k, v in sigs.items():
        #         sbot_common.trace(k, v)
        #     for k, v in hls.items():
        #         sbot_common.trace(k, v)



#-----------------------------------------------------------------------------------
def _clean_json(s):

    pass

    # # shameless copy paste from json/decoder.py
    # FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
    # WHITESPACE = re.compile(r"[ \t\n\r]*", FLAGS)

    # https://docs.python.org/3/library/json.html#encoders-and-decoders
    # decode(s)
    # Return the Python representation of s (a str instance containing a JSON document).
    # JSONDecodeError will be raised if the given JSON document is not valid.
    # raw_decode(s)
    # Decode a JSON document from s (a str beginning with a JSON document) and return a 2-tuple of the Python representation and the index in s where the document ended.
    # This can be used to decode a JSON document from a string that may have extraneous data at the end.


    # class ConcatJSONDecoder(json.JSONDecoder):
    #     def decode(self, s, _w=WHITESPACE.match):
    #         s_len = len(s)
    #         bs = s

    #         objs = []
    #         end = 0
    #         while end != s_len:
    #             obj, end = self.raw_decode(bs, idx=_w(bs, end).end())
    #             end = _w(bs, end).end()
    #             objs.append(obj)
    #         return objs




    # https://sublime-text-unofficial-documentation.readthedocs.io/en/latest/reference/key_bindings.html

    # Structure of a Context
    # key - Name of the context whose value you want to query.
    # operator - Type of test to perform against key’s value. Defaults to equal.
    # operand - The result returned by key is tested against this value.
    # match_all - Requires the test to succeed for all selections. Defaults to false.


    #try:
    #    with open(r'C:\Users\cepth\AppData\Roaming\Sublime Text 3\Packages\SublimeBagOfTricks\default-keymap.json', 'r') as fp:
    #    # C:\Dev\SublimePluginsSourceCode\Default.sublime-package\Default (Windows).sublime-keymap

    #        # print(fp.read())
    #        # s = fp.read()
    #        kmap = json.load(fp)

    #        fixes = { '"': 'dblquote', "'": 'snglquote', '(': 'lparen', ')': 'rparen',
    #            '[': 'lbracket', ']': 'rbracket', '{': 'lbrace', '}': 'rbrace' }

    #        s = []
    #        s.append('cmd, keys, args, context')


    #        for entry in kmap:
    #            # print(entry)
    #            keys = ' '.join(entry['keys'])
    #            if keys in fixes:
    #                keys = fixes[keys]
    #            cmd = entry['command']

    #            # args = list(entry.get('args', []))
    #            # s = '{}, {}, {}'.format(cmd, keys, ','.join(args))

    #            # args:
    #            # {'extensions': ['cpp', 'cxx', 'cc', 'c', 'hpp', 'hxx', 'hh', 'h', 'ipp', 'inl', 'm', 'mm']}
    #            # {'forward': False, 'by': 'pages', 'extend': True}
    #            # {'rows': [0.0, 0.5, 1.0], 'cols': [0.0, 1.0], 'cells': [[0, 0, 1, 1], [0, 1, 1, 2]]}

    #            # context:
    #            # [
    #            #     {'operand': '(text.html, text.xml) - string - comment', 'key': 'selector', 'operator': 'equal', 'match_all': True},
    #            #     {'operand': '.*<$', 'key': 'preceding_text', 'operator': 'regex_match', 'match_all': True}, {'key': 'setting.auto_close_tags'}
    #            # ]


    #            na = '' # or None or 'xxx'
    #            repl = '' #'~'
    #            args = str(entry.get('args', na)).replace(',', repl)
    #            context = str(entry.get('context', na)).replace(',', repl)
    #            s.append('{}, {}, {}, {}'.format(cmd, keys, args, context))

    #        s = '\n'.join(s)
    #        # print(s)
    #        sbot_common.create_new_view(view.window(), s)

    #except Exception as e:
    #    print('exception', e)


    # try:
    #     # Each of these classes is layered over a supplied raw FileIO object (f)
    #     f = io.FileIO(fn) # Open the file (raw I/O)
    #     g = io.BufferedReader(f) # Put buffering around it
    #     read_ch = rdr.read(1)
    #     currentChar = read_ch[0] if len(read_ch) > 0 else -1
    #     next_ch = rdr.peek(1)
    #     nextChar = next_ch[0] if len(next_ch) > 0 else -1
    # except Exception as e:
    #     ret = $"ERROR: {e.GetType()} {e.Message}"
    # # Clean up.
    # io.close(g)
    # io.close(f)

#-----------------------------------------------------------------------------------
class SbotExampleGetNumberCommand(sublime_plugin.WindowCommand):
    ''' A window command. sbot_example_get_number '''

    def run(self):
        # Bottom input area.
        self.window.show_input_panel("Give me a number:", "", self.on_done, None, None)

    def on_done(self, text):
        try:
            line = int(text)
            if self.window.active_view():
                self.window.active_view().run_command("goto_line", {"line": line})
                self.window.active_view().run_command("expand_selection", {"to": "line"})
        except ValueError:
            pass


#-----------------------------------------------------------------------------------
class SbotExampleListSelectCommand(sublime_plugin.TextCommand):
    ''' Command: Select from list. sbot_example_list_select '''

    def __init__(self, view):
        self.panel_items = []
        super(SbotExampleListSelectCommand, self).__init__(view)

    def run(self, edit, cmd=None):
        self.panel_items = ["Duck", "Cat", "Banana"]
        self.view.window().show_quick_panel(self.panel_items, self.on_done_panel)

    def on_done_panel(self, choice):
        if choice >= 0:
            sbot_common.trace("You picked {0}".format(self.panel_items[choice]))


#-----------------------------------------------------------------------------------
class SbotExampleMenuCommand(sublime_plugin.TextCommand):
    ''' Container for other menu items. sbot_example_menu '''

    def run(self, edit, cmd=None):
        # Individual menu items.
        CMD1 = {'text': 'UserInput',  'command' : 'sbot_example_user_input'}
        CMD2 = {'text': 'GetNumber',  'command' : 'sbot_example_get_number'}
        CMD3 = {'text': 'MsgBox',     'command' : 'sbot_example_msg_box'}
        CMD4 = {'text': 'ListSelect', 'command' : 'sbot_example_list_select'}

        menu_items = [CMD1, CMD2, CMD3, CMD4]

        def on_done(index):
            if index >= 0:
                self.view.run_command(menu_items[index]['command'], {'cmd': cmd})

        self.view.window().show_quick_panel([item['text'] for item in menu_items], on_done)


#-----------------------------------------------------------------------------------
class SbotExampleArgumentInputHandler(sublime_plugin.TextInputHandler):
    ''' Command: Get input from user. sbot_example_user_input
    When a command with arguments is called without them, but it defines an input() method, Sublime will call
    the input() method to see if there is an input handler that can be used to gather the arguments instead.
    Every input handler represents an argument to the command, and once the entire chain of them is finished,
    Sublime re-invokes the command with the arguments that it gathered.

    This >>>>>> https://forum.sublimetext.com/t/simple-examples-for-textinputhandler/48422/13
    You also need to add the command to the command palette by adding an entry to a sublime-commands file;
    Something you may have missed is that only commands that appear in the command palette support using
    input handlers because the handlers display input in the command palette itself as a part of its operation.
    '''

    def placeholder(self):
        return "placeholder - optional"

    def name(self):
        return "my_value"

    def description(self, args):
        return "description - optional"

    def initial_text(self):
        # # Check if something selected.
        # if len(self.view.sel()) > 0:
        #     if(self.view.sel()[0].size() == 0):
        #         return "initial_text"
        #     else:
        #         return self.view.substr(self.view.sel()[0])
        # else:
        #     return "wtf?"
        return 'initial_text'


#-----------------------------------------------------------------------------------
class SbotExampleInputCommand(sublime_plugin.TextCommand):

    def run(self, edit, my_value): # Has to be called exactly my_value - another convention.
        sbot_common.trace('argument:', my_value)
        # for i in range(len(self.view.sel())):
        #     sel = self.view.sel()[i]
        #     data = self.view.substr(sel)
        #     # sbot_common.trace("*** sel:{0} data:{1}".format(sel, data))
        #     # replace selected text.
        #     self.view.replace(edit, sel, my_value)

    def input(self, args):
        return SbotExampleArgumentInputHandler(self.view) if "text" not in args else None
