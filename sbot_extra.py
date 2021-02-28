import os
import sys
import sublime
import sublime_plugin


# Holding tank for examples, leftovers, bits and pieces.


#-----------------------------------------------------------------------------------
class SbotFindNonAsciiCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        v = self.view

        # TODO hex processor/editor? Can't look at view, must open file.
        # Files containing null bytes are opened as hexadecimal by default In your User or Default Settings file:
        # "enable_hexadecimal_encoding": false
        # OR
        # In your User or Default Settings file(s):
        # "preview_on_click": false
        # Go to File -> Reopen with Encoding and select UTF-8. This will bring back the normal text view.

        find = []

        reg = sublime.Region(0, v.size())
        s = v.substr(reg)

        row = 1
        col = 1

        for c in s:
            if c == '\n':
                # Valid.
                row += 1
                col = 1
            elif c == '\r':
                # Valid.
                col = 1
            elif c == '\t':
                # Valid.
                col += 1
            elif c < ' ' or c > '~': # 32  SPACE  126  ~
                # Invalid.
                find.append('row:{} col:{} char:{}'.format(row, col, int(c)))
                col += 1
            else:
                # Valid.
                col += 1

                
        print('----------- find non-ascii ---------------\n')
        for d in find:
            print(d)


#-----------------------------------------------------------------------------------
class SbotTestCommand(sublime_plugin.TextCommand):
    ''' Just for hacking/testing. '''

    def run(self, edit, all=False):
        v = self.view
        w = self.view.window()
        
        # for sheet in w.sheets():
        #     print('sheet:', sheet)
        # for view in w.views(): # These are in order L -> R.
        #     print('active view:', w.get_view_index(view), view.file_name()) # (group, index)
        # get_project(v).dump() # These are not ordered like file.

        # # Phantom phun
        # image = os.path.join(sublime.packages_path(), 'SublimeBagOfTricks', 'test', 'mark1.bmp')
        # print(image)
        # html = '<body><p>Hello!</p><img src="file://' + image + '" width="90" height="145"></body>'
        # self.phantset = sublime.PhantomSet(v, "test")
        # phant = sublime.Phantom(v.sel()[0], html, sublime.LAYOUT_BLOCK)
        # phants = []
        # phants.append(phant)
        # self.phantset.update(phants)

        # global global_thing
        # print(global_thing)
        # global_thing['item' + str(len(global_thing) + 5)] = 1234
        # v.show_popup(str(global_thing))


        # if action == 'white_space':
        #     pname, pval1, pval2 = "draw_white_space", "all", "selection"
        # elif action == 'gutter':
        #     pname, pval1, pval2 = "gutter", False, True
        # elif action == 'line_no':
        #     pname, pval1, pval2 = "line_numbers", False, True
        # elif action == 'indent_guide':
        #     pname, pval1, pval2 = "draw_indent_guides", False, True
        # if pname:
        #     propertyValue = pval1 if v.settings().get(pname, pval1) != pval1 else pval2
        #     v.settings().set(pname, propertyValue)

        print('11111111111111')
        c = sys.stdin.read(1)
        print('========', c)
        print('22222222222222')
        
        # sys.stderr.write("started\n")
        # i = 4
        # import pdb ; pdb.set_trace()
        # # import spdb ; spdb.start()
        # z = 5
        
        # winpdb will be launched, if not yet launched from Plugin Debugger. Each later call of this function sets a breakpoint.
        # If winpdb (started from Plugin Debugger) has been terminated in between, it will be restarted.
        # spdb.setbreak()
        # sets a breakpoint. You need to have to attached debug client for using this.
        # Note: If you start winpdb manually, use sublime as password for finding scripts on localhost.
        
        # Test your installation
        # Run "Plugin Debugger: run debug_example (opens Debugger)" from command palette.
        # Your sublime text will freeze for few seconds and then will open a winpdb window ready for debugging DebugExampleCommand.

        # Module rpdb2 havily hooks into python interpreter, so if you really want to quit the debug session, you have to restart your sublime text.
        # Once Winpdb has opened, you should keep it open, because it will inform you on any uncaught exception. If you 
        # close winpdb, your sublime simply freezes on an uncaught exception (because it breaks on that exception), but you are 
        # not informed on this because of missing frontend.


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
class SbotExampleMsgBoxCommand(sublime_plugin.TextCommand):
    ''' Command: Simple message box. sbot_example_msg_box '''

    def run(self, edit, cmd=None):
        # print("MsgBox! {0} {1}".format(self.name(), edit))
        sublime.ok_cancel_dialog("Hi there from StptMsgBoxCommand")


#-----------------------------------------------------------------------------------
class SbotExampleListSelectCommand(sublime_plugin.TextCommand):
    ''' Command: Select from list. sbot_example_list_select '''

    def run(self, edit, cmd=None):
        # print("ListSelect! {0} {1}".format(self.name(), edit))
        self.panel_items = ["Duck", "Cat", "Banana"]
        # self.window.show_quick_panel(self.panel_items, self.on_done_panel)
        self.view.window().show_quick_panel(self.panel_items, self.on_done_panel)

    def on_done_panel(self, choice):
        if choice >= 0:
            print("You picked {0}".format(self.panel_items[choice]))
            os.startfile(ddir + r"\test1.txt")


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

    https://forum.sublimetext.com/t/simple-examples-for-textinputhandler/48422/13
    you also need to add the command to the command palette by adding an entry to a sublime-commands file;
    Something you may have missed is that only commands that appear in the command palette support using 
    input handlers because the handlers display input in the command palette itself as a part of its operation.
    '''

    def __init__(self, view):
        self.view = view

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
        print('argument:', my_value)
        # for i in range(len(self.view.sel())):
        #     sel = self.view.sel()[i]
        #     data = self.view.substr(sel)
        #     # print("*** sel:{0} data:{1}".format(sel, data))
        #     # replace selected text.
        #     self.view.replace(edit, sel, my_value)

    def input(self, args):
        if "text" not in args:
            return SbotExampleArgumentInputHandler(self.view)
