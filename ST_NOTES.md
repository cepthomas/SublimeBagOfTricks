# Sublime Text Stuff

Accumulated notes that will eventually go away.

## Misc Notes
- package-metadata.json is used for package management - remove while developing/debugging because PackageControl will delete it.
- Commands can't end with `_numeral`: `my_cmd_1` should be `stpt_cmd1`.
- There is a bunch of magic naming for Commands and InputHandlers to support mapping to the menu and key maps.
  e.g. `class MyExampleInputHandler` maps to command `my_example`.
- Other good examples in Packages\Default:
    - arithmetic.py Accepts an input from the user when run via the Command Palette
    - exec.py Uses phantoms to display errors inline
    - font.py Shows how to work with settings
    - goto_line.py Prompts the user for input, then updates the selection
    - mark.py Uses add_regions() to add an icon to the gutter
    - show_scope_name.py Uses a popup to show the scope names at the caret
- Themes basically decorate the core UI elements like side-pane, tabs, menus etc: "theme": "Soda Light 3.sublime-theme"
- Color-schemes are responsible for the syntax-highlighting: "color_scheme": "Packages\Visual Studio Bold Color Scheme\Visual Studio Bold.tmTheme",


## Directories and Files
- `%executable_dir%`: C:\Program Files\Sublime Text
- `%data_dir%`: %APPDATA%\Sublime Text 3 (C:\Users\%user%\AppData\Roaming\Sublime Text 3)

Nearly all of the interesting files for users live under `%data_dir%`.

Zipped packages (*.sublime-package) may be stored in:
- `%executable_dir\Packages`: Usually just ST shipped packages.%
- `%data_dir%\Installed Packages`: User packages, incl via package control.

Loose packages are stored in:
- `%data_dir%`\Packages

Any loose files in `%data_dir%\Packages\%name%` will override files stored in the `%name%.sublime-package file`.

There are two special packages: Default and User. Default is always ordered first, User is always ordered last, and others are ordered alphabetically. Package ordering comes into effect when merging files between packages, for example Main.sublime-menu. Any package may contain a file called Main.sublime-menu, however this won't override the main menu, instead the files will be merged according to the order of the packages.

To create a new package, simply create a new directory under `%data_dir%\Installed Packages`. You can access this directory from the Preferences > Browse Packages menu.

To override a file in an existing package, just create a file with the same name under the `Packages\%name%` directory.

For example to override the file function.sublime-snippet in the Python.sublime-package package that ships with Sublime Text, create a directory called Python under the `%data_dir%\Packages` directory, and place your function.sublime-snippet file there.


```
%data_dir%
+---Installed Packages
|       *.sublime-package
|       Theme - Soda.sublime-package
|       ...
|       
+---Lib
|   \---python3.3  ???  empty - for adding other py libs?
|
+---Local
|       License.sublime_license
|       Session.sublime_session
|       
\---Packages
    +---...
    +---PluginTemplate
    +---...
    \---User
        |   C#.sublime-settings
        |   C.sublime-settings
        |   Default (Windows).sublime-keymap
        |   JSON.sublime-settings
        |   oscrypto-ca-bundle.crt
        |   Package Control.last-run
        |   Package Control.merged-ca-bundle
        |   Package Control.sublime-settings
        |   Package Control.user-ca-bundle
        |   Preferences.sublime-settings (!!!)
        |   StyleToken.sublime-settings
        |   XML.sublime-settings
        |   
        \---Package Control.cache


%executable_dir%
|   plugin_host.exe
|   subl.exe
|   sublime.py
|   sublime_plugin.py
|   sublime_text.exe
|   ...
|   
\---Packages = factory defaults
        Default.sublime-package
        $theme%.sublime-package
        ....
        %language%.sublime-package
        ....
```

## Menus
Sublime Text has seven menus that may be customized:
- Main.sublime-menu: Primary menu for the application
- Side Bar Mount Point.sublime-menu: Context menu for top-level folders in the side bar
- Side Bar.sublime-menu: Context menu for files and folders in the side bar. Has "magic" args for passing file and folder names to commands.Entries with an arg "files": [] will be enabled for files and will pass file names to the command via the arg files. Entries with an arg "dirs": [] will be enabled for folders and will pass file names to the command via the arg dirs. Entries with an arg "paths": [] will be enabled for files and folders and will pass file and folder names to the command via the arg paths.
- Tab Context.sublime-menu: Context menu for file tabs
- Context.sublime-menu: Context menu for text areas
- Find in Files.sublime-menu: Menu shown when clicking the ... button in Find in Files panel
- Widget Context.sublime-menu: Context menu for text inputs in various panels. Technically this file name can be changed via the "context_menu" setting inside of Widget.sublime-settings.


## API

### CORE COMPONENTS - in sublime Module
- sublime.Window Class: desc?
- sublime.Sheet Class: Represents a content container, i.e. a tab, within a window. Sheets may contain a View, or an image preview.
- sublime.View Class: Represents a view into a text buffer. Note that multiple views may refer to the same buffer, but they have their own unique selection and geometry.
- sublime.Selection Class: Maintains a set of Regions, ensuring that none overlap. The regions are kept in sorted order.
- sublime.Region Class: Represents an area of the buffer. Empty regions, where a == b are valid.
- sublime.Phantom Class: Represents an HTML-based decoration to display non-editable content interspersed in a View. Used with PhantomSet to actually add the phantoms to the View. Once a Phantom has been constructed and added to the View, changes to the attributes will have no effect.
- sublime.PhantomSet Class: A collection that manages Phantoms and the process of adding them, updating them and removing them from the View.
- sublime.Edit Class: Edit objects have no functions, they exist to group buffer modifications.
- sublime.Settings Class:

### PLUGIN EXTENSION POINTS - in sublime_plugin Module
- sublime_plugin.EventListener Class: Note that many of these events are triggered by the buffer underlying the view, and thus the method is only called once, with the first view as the parameter.
- sublime_plugin.ViewEventListener Class: A class that provides similar event handling to EventListener, but bound to a specific view. Provides class method-based filtering to control what views objects are created for.
- sublime_plugin.ApplicationCommand Class: dexc?
- sublime_plugin.WindowCommandClass: WindowCommands are instantiated once per window. The Window object may be retrieved via self.window
- sublime_plugin.TextCommand Class: TextCommands are instantiated once per view. The View object may be retrieved via self.view
- sublime_plugin.TextInputHandler Class: TextInputHandlers can be used to accept textual input in the Command Palette. Return a subclass of this from the input() method of a command.
- sublime_plugin.ListInputHandler Class: ListInputHandlers can be used to accept a choice input from a list items in the Command Palette. Return a subclass of this from the input() method of a command.
- CommandInputHandler: a subclass of either TextInputHandler or ListInputHandler.

> if you are going to interact with the current view, use TextCommand, otherwise use WindowCommand. I have yet to see a use case for ApplicationCommand, but I guess if you need to interact with all windows.

### TYPES
- location: a tuple of (str, str, (int, int)) that contains information about a location of a symbol. The first string is the absolute file path, the second is the file path relative to the project, the third element is a two-element tuple of the row and column.
- point: an int that represents the offset from the beginning of the editor buffer. The View methods text_point() and rowcol() allow converting to and from this format.
- value: any of the Python data types bool, int, float, str, list or dict.
- dip: a float that represents a device-independent pixel.
- vector: a tuple of (dip, dip) representing x and y coordinates.
