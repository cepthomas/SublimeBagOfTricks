import json
#import sublime
import sublime_plugin
import sbot_common


# print('Load sbot_extra')

# IGNORE Temp holding tank for examples, leftovers, bits and pieces.


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


#-----------------------------------------------------------------------------------
class SbotExampleGetNumberCommand(sublime_plugin.WindowCommand):
    ''' A window command that gets input from bottom input area. sbot_example_get_number '''

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
        CMD2 = {'text': 'MsgBox',     'command' : 'sbot_example_msg_box'} # not impl
        CMD3 = {'text': 'ListSelect', 'command' : 'sbot_example_list_select'}

        menu_items = [CMD1, CMD2, CMD3, CMD4]

        def on_done(index):
            if index >= 0:
                cmd = menu_items[index]['command']
                self.view.run_command(cmd)

        self.view.window().show_quick_panel([item['text'] for item in menu_items], on_done)


#-----------------------------------------------------------------------------------
class SbotExampleUserInputCommand(sublime_plugin.TextCommand):

    def run(self, edit, my_value): # Has to be called exactly my_value - another convention.
        print('!!!! run()', my_value)
        sbot_common.trace('argument:', my_value)

    def input(self, args):
        print('!!!! input()', args)
        return SbotExampleArgumentInputHandler() if "my_value" not in args else None


#-----------------------------------------------------------------------------------
class SbotExampleArgumentInputHandler(sublime_plugin.TextInputHandler):
    '''
    When a command with arguments is called without them, but it defines an input() method, Sublime will call
    the input() method to see if there is an input handler that can be used to gather the arguments instead.
    Every input handler represents an argument to the command, and once the entire chain of them is finished,
    Sublime re-invokes the command with the arguments that it gathered.

    TextInputHandlers can be used to accept textual input in the Command Palette. Return a subclass of this from the input() method of a command.

    For an input handler to be shown to the user, the command returning the input handler MUST be made available in the Command Palette
    by adding the command to a Default.sublime-commands file.
    '''

    def placeholder(self):
        return "placeholder - optional"

    def name(self):
        return "my_value"

    def description(self, args):
        return "description - optional"

    def initial_text(self):
        return 'Put whatever here'
