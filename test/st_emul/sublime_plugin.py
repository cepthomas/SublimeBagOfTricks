
class CommandInputHandler():
    pass


class TextInputHandler(CommandInputHandler):
    pass


class ListInputHandler(CommandInputHandler):
    pass


class Command():
    pass


class WindowCommand(Command):
    def __init__(self, window):
        self.window = window

    #def run_(self, edit_token, args):
    #    pass

    def run(self, *args):
        pass  #TODO-T

    #def run(self):
    #    pass


class TextCommand(Command):
    def __init__(self, view):
        self.view = view

    #def run_(self, edit_token, args):
    #    pass

    def run(self, edit, *args):
        pass  #TODO-T


class EventListener():
    pass


class ViewEventListener():
    def __init__(self, view):
        self.view = view
