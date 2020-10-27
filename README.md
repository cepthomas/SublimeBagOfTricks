# What It Is
A work-in-progress Sublime Text plugin containing odds and ends missing from other packages.
The focus is not on code development but rather text processing. It's also an excuse to brush up on my python.

Built for Windows and ST3 but most should work for other OSes and ST2.

# Features

## Colorizing
- Word colorizing similar to [StyleToken](https://github.com/vcharnahrebel/style-token).
- Persists to sbot project file.
- Also a handy scope popup that shows you the style associated with each scope.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_highlight_text      | Highlight text using next in highlight_scopes |
| sbot_clear_highlight     | Remove highlight in selection |
| sbot_clear_all_highlights| Remove all highlights |
| sbot_show_scopes         | Popup that shows style for scopes |

| Setting                  | Description |
|:--------                 |:-------     |
| highlight_scopes         | List of scopes for marking text |


## Render To Html
- Simple render to html with styles, primarily for printing.
- Line wrap with optional line numbers.
- Version to render markdown file to html using [Markdeep](https://casual-effects.com/markdeep/).

| Command                  | Description |
|:--------                 |:-------     |
| sbot_render_to_html      | Render current file including scope colors and highlights to html |
| sbot_render_markdown     | Render current markdown file to html |


| Setting                  | Description |
|:--------                 |:-------     |
| html_font_face           | For rendered html |
| html_font_size           | For rendered html |
| html_background          | If you need to change the bg color (not done automatically from color scheme) |
| html_line_numbers        | Optionally add line numbers |
| md_font_face             | For rendered markdown |
| md_font_size             | For rendered markdown |
| md_background            | If you need to change the markdown bg color (not done automatically from color scheme) |
| render_output            | One of: clipboard, new_file (view), default_file (original filename + .html), default_file_open (default_file + show) |


## Signets (bookmarks)
Enhanced bookmarks:
- Persists to sbot project file.
- Next/previous (optionally) traverses files in project - like VS.
- `Bookmark` and `mark` are already taken so I shall use `signet` which means in French:
> "Petit ruban ou filet qu'on insère entre les feuillets d'un livre pour marquer l'endroit que l'on veut retrouver."

| Command                  | Description |
|:--------                 |:-------     |
| sbot_toggle_signet       | Toggle at row |
| sbot_next_signet         | Goto next |
| sbot_previous_signet     | Goto previous |
| sbot_clear_signets       | Clear all |
  
| Setting                  | Description |
|:--------                 |:-------     |
| signet_scope             | ST scope name for gutter icon color |
| signet_nav_files         | Next/prev traverses all files otherwise just open one |

## Miscellany
| Command                  | Description |
|:--------                 |:-------     |
| sbot_split_view          | Toggles simple horizontal split screen, like MS products |

## SideBar
Commands added to the sidebar. Just the stuff I need.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_sb_copy_name        | Copy file/dir name to clipboard |
| sbot_sb_copy_path        | Copy full file/dir path to clipboard |
| sbot_sb_terminal         | Open a Windows Terminal here |
| sbot_sb_open_browser     | Open html file in your browser |
| sbot_sb_tree             | Subdir tree in clipboard |

## Examples
Leftovers that will eventually be deleted or subsumed.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_ex_menu             |             |
| sbot_ex_get_number       |             |
| sbot_ex_user_input       |             |
| sbot_ex_list_select      |             |
| sbot_ex_msg_box          |             |

# Notes

Accumulated notes that will probably eventually go away.

## Naming
- In general `line` refers to editor lines and is 1-based. `row` refers to buffer contents as an array and is 0-based.
- Collections, variables, functions, etc use:
  - `persisted` is the json compatible file format.
  - `visual` is the way ST API handles elements.
  - `internal` is the plugin format.
- Commands can't end with `<underscore numeral>` e.g. `my_cmd_1` should be `stpt_cmd1`.
- There is magic naming for Commands and InputHandlers to support mapping to the menu and key maps. e.g. a command like `big_brown_dog` is mapped to a handler named 'BigBrowwnDogCommand()'.


## Misc Notes
- `package-metadata.json` is used for package management so remove it while developing/debugging plugins because PackageControl will delete the entire package.
- There's lots of good plugin examples in `Packages\Default`.
- If you pass a dict as value in View.settings().set(name, value), it seems that the dict key must be a string.


## Directories
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


## Files
- `%executable_dir%`: C:\Program Files\Sublime Text
- `%data_dir%`: %APPDATA%\Sublime Text 3 (C:\Users\%user%\AppData\Roaming\Sublime Text 3)
- Nearly all of the interesting files for users live under `%data_dir%`.
- Zipped packages (*.sublime-package) may be stored in:
  - `%executable_dir%\Packages`: Usually just ST shipped packages.
  - `%data_dir%\Installed Packages`: User packages, incl via package control.
- Loose packages are stored in:
  - `%data_dir%`\Packages
- Any loose files in `%data_dir%\Packages\%name%` will override files stored in the `%name%.sublime-package file`.
- There are two special packages: Default and User. Default is always ordered first, User is always ordered last, and others are ordered alphabetically. Package ordering comes into effect when merging files between packages, for example Main.sublime-menu. Any package may contain a file called Main.sublime-menu, however this won't override the main menu, instead the files will be merged according to the order of the packages.
- To create a new package, simply create a new directory under `%data_dir%\Installed Packages`. You can access this directory from the Preferences > Browse Packages menu.
- To override a file in an existing package, just create a file with the same name under the `Packages\%name%` directory.
- To remove items from default menus: In `<user>\AppData\Roaming\Sublime Text 3\Packages`, create a new folder that’s named exactly like the package you want to overwrite. For Sublime Core, this is `Default`. In this folder, create a new `.sublime-menu` file. Either add only your own stuff, or copy the default content and edit it.
- Style:
  - Themes (`*.sublime-theme`) basically decorate the core UI elements like side-pane, tabs, menus etc.
  - Color-schemes are responsible for the syntax-highlighting e.g. `Visual Studio Bold.tmTheme`.


## Menus
Sublime Text has seven menus that may be customized:
- Main.sublime-menu: Primary menu for the application
- Side Bar Mount Point.sublime-menu: Context menu for top-level folders in the side bar
- Side Bar.sublime-menu: Context menu for files and folders in the side bar. Has "magic" args for passing file and folder names to commands.Entries with an arg "files": [] will be enabled for files and will pass file names to the command via the arg files. Entries with an arg "dirs": [] will be enabled for folders and will pass file names to the command via the arg dirs. Entries with an arg "paths": [] will be enabled for files and folders and will pass file and folder names to the command via the arg paths.
- Tab Context.sublime-menu: Context menu for file tabs
- Context.sublime-menu: Context menu for text areas
- Find in Files.sublime-menu: Menu shown when clicking the ... button in Find in Files panel
- Widget Context.sublime-menu: Context menu for text inputs in various panels. Technically this file name can be changed via the "context_menu" setting inside of Widget.sublime-settings.


## API - Core Components
These are in sublime Module.

- sublime.Window Class: One instance of app/window.
- sublime.Sheet Class: Represents a content container, i.e. a tab, within a window. Sheets may contain a View, or an image preview.
- sublime.View Class: Represents a view into a text buffer. Note that multiple views may refer to the same buffer, but they have their own unique selection and geometry.
- sublime.Selection Class: Maintains a set of Regions, ensuring that none overlap. The regions are kept in sorted order.
- sublime.Region Class: Represents an area of the buffer. Empty regions, where a == b are valid.
- sublime.Phantom Class: Represents an HTML-based decoration to display non-editable content interspersed in a View. Used with PhantomSet to actually add the phantoms to the View. Once a Phantom has been constructed and added to the View, changes to the attributes will have no effect.
- sublime.PhantomSet Class: A collection that manages Phantoms and the process of adding them, updating them and removing them from the View.
- sublime.Edit Class: Edit objects have no functions, they exist to group buffer modifications.
- sublime.Settings Class:


## API - Plugin Extension Points
These are in sublime_plugin Module.
If you are going to interact with the current view, use TextCommand, otherwise use WindowCommand. I have yet to see a use case for ApplicationCommand, but I guess if you need to interact with all windows.

- sublime_plugin.EventListener Class: Note that many of these events are triggered by the buffer underlying the view, and thus the method is only called once, with the first view as the parameter.
- sublime_plugin.ViewEventListener Class: A class that provides similar event handling to EventListener, but bound to a specific view. Provides class method-based filtering to control what views objects are created for.
- sublime_plugin.ApplicationCommand Class: 
- sublime_plugin.WindowCommandClass: WindowCommands are instantiated once per window. The Window object may be retrieved via self.window
- sublime_plugin.TextCommand Class: TextCommands are instantiated once per view. The View object may be retrieved via self.view
- sublime_plugin.TextInputHandler Class: TextInputHandlers can be used to accept textual input in the Command Palette. Return a subclass of this from the input() method of a command.
- sublime_plugin.ListInputHandler Class: ListInputHandlers can be used to accept a choice input from a list items in the Command Palette. Return a subclass of this from the input() method of a command.
- CommandInputHandler: a subclass of either TextInputHandler or ListInputHandler.
