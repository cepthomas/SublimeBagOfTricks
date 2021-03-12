# What It Is
A hodge-podge Sublime Text plugin containing odds and ends missing from or over-developed in other packages.
The focus is not on code development but rather general text processing.

No support as yet for PackageControl.

Built for Windows and ST3. Other OSes and ST2 might require some hacking.


![logo](felix.jpg)

# Features

## General

| Setting                  | Description |
|:--------                 |:-------     |
| enable_persistence       | Save/load signet/highlight persistence - default is true |


## Colorizing
- Word colorizing similar to [StyleToken](https://github.com/vcharnahrebel/style-token).
- Persists to sbot project file.
- Also a handy scope popup that shows you the style associated with each scope.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_highlight_text      | Highlight text 1 through 6 using highlight_scopes |
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
| sbot_render_to_html      | Render current open file including scope colors and highlights to html |
| sbot_render_markdown     | Render current open markdown file to html |


| Setting                  | Description |
|:--------                 |:-------     |
| html_font_face           | For rendered html |
| html_font_size           | For rendered html |
| html_background          | If you need to change the bg color (not done automatically from color scheme) |
| html_line_numbers        | Optionally add line numbers |
| md_font_face             | For rendered markdown |
| md_font_size             | For rendered markdown |
| md_background            | If you need to change the markdown bg color (not done automatically from color scheme) |
| render_output            | One of: `clipboard`, `file` (original fn or temp + .html), `show` |
| render_max_file          | Max file size to render |
| sel_all                  | Option for selection defaults: if true and no user selection, assumes the whole document (like ST) |

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
| sbot_split_view          | Toggles simple horizontal split screen, like e.g. `MS Word` |
| sbot_show_eol            | Toggles showing EOLs |
| sbot_insert_line_indexes | Insert sequential numbers in first column |

| Setting                  | Description |
|:--------                 |:-------     |
| eol_scope                | ST scope name for EOL marker |

## SideBar
Commands added to the sidebar. Just the stuff I want.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_sb_copy_name        | Copy file/dir name to clipboard |
| sbot_sb_copy_path        | Copy full file/dir path to clipboard |
| sbot_sb_terminal         | Open a Windows Terminal here |
| sbot_sb_folder           | Open a Windows Explorer here |
| sbot_sb_open_browser     | Open html file in your browser |
| sbot_sb_tree             | Run tree cmd to clipboard |
| sbot_sidebar_exclude     | Hide selected file/dir in project |

## Cleaning
Trimming etc.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_trim                | Line end ws trim, arg:`how` should be `leading` or `trailing` or `both` |
| sbot_remove_empty_lines  | Like it says, arg:`normalize`=True leaves one |
| sbot_remove_ws           | Like it says, arg:`normalize`=True leaves one |


## Format
Prettify json. xml, html later when ST4.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_format_json         | Format json content and show in new view |
| sbot_format_xml          | Format xml content and show in new view |
| sbot_format_html         | Format html content and show in new view |


## Examples
Leftovers that will eventually be deleted or subsumed.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_example_menu        | Menu |
| sbot_example_get_number  | User text input |
| sbot_example_input       | User text input |
| sbot_example_list_select | User list sel |
| sbot_example_msg_box     | User message |

# Notes

Accumulated notes that will probably eventually go away.

## This Project
- In general `line` refers to editor lines and is 1-based. `row` refers to buffer contents as an array and is 0-based.
- Project collections, variables, functions, etc use:
  - `persisted` is the json compatible file format.
  - `visual` is the way ST API handles elements.
  - `internal` is the plugin format.
- Commands can't end with `<underscore numeral>` e.g. `my_cmd_1` should be `stpt_cmd1`.
- There is magic naming for Commands and InputHandlers to support mapping to the menu and key maps. e.g. a command like `big_brown_dog` is mapped to a handler named 'BigBrownDogCommand()'.
- `package-metadata.json` is used for package management so remove it while developing/debugging plugins because PackageControl will delete the entire package.
- There's lots of good plugin examples in `Packages\Default`.
- If you pass a dict as value in View.settings().set(name, value), it seems that the dict key must be a string.


## Sublime

### General
- Read the [API](https://www.sublimetext.com/docs/api_reference.html).
- I learned the hard way that ST doesn't handle python modules/packages as you expect. It may load modules multiple times, making the standard way
  of handling globals difficult if not impossible. [Details}(https://forum.sublimetext.com/t/accessing-settings-from-within-a-multi-module-st-package/46128/5).
- EventListeners are instantiated exactly once (on plugin load time), as are ApplicationCommands. WindowCommands are instantiated for each window and TextCommands for each view, or even every time a command is run???
- There is one global context and all plugins share the same process.
- For the specific case of Sublime plugins, when your plugin modules are loaded by sublime it invokes the dir function on the loaded module to find all of the symbols it contains and ignores everything that’s not a subclass of one of the special plugin classes (i.e. ApplicationCommand, WindowCommand, TextCommand, EventListener and ViewEventListener).
- These are in sublime_plugin module.
If you are going to interact with the current view, use TextCommand, otherwise use WindowCommand. I have yet to see a use case for ApplicationCommand, but I guess if you need to interact with all windows.
- sublime_plugin.EventListener Class: Note that many of these events are triggered by the buffer underlying the view, and thus the method is only called once, with the first view as the parameter.


### Directories
```
%data_dir%
+---Installed Packages
|       *.sublime-package
|       Theme - Soda.sublime-package
|       ...
|       
+---Lib
|   \---python3.3 (empty)
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
        |   Preferences.sublime-settings
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

### Files
- `%executable_dir%`: `C:\Program Files\Sublime Text 3`
- `%data_dir%`: `%APPDATA%\Sublime Text 3` aka `C:\Users\%user%\AppData\Roaming\Sublime Text 3`
- Nearly all of the interesting files for users live under `%data_dir%`.
- Zipped packages (`*.sublime-package`) may be stored in:
  - `%executable_dir%\Packages`: Usually just ST shipped packages. Includes stuff like `*.sublime-syntax`.
  - `%data_dir%\Installed Packages`: User packages, including those installed via package control.
- Loose packages are stored in:
  - `%data_dir%\Packages`
- Any loose files in `%data_dir%\Packages\%name%` will override files stored in the `%name%.sublime-package file`.
- There are two special packages: `Default` and `User`. Default is always ordered first, User is always ordered last, and others are ordered alphabetically. Package ordering comes into effect when merging files between packages, for example `Main.sublime-menu`. Any package may contain a file called `Main.sublime-menu`, however this won't override the main menu, instead the files will be merged according to the order of the packages.
- To create a new package, simply create a new directory under `%data_dir%\Installed Packages`. You can access this directory from the `Preferences > Browse Packages` menu.
- To override a file in an existing package, just create a file with the same name under the `Packages\%name%` directory.
- To remove items from default menus: In `<user>\AppData\Roaming\Sublime Text 3\Packages`, create a new folder that’s named exactly like the package you want to overwrite. For Sublime Core, this is `Default`. In this folder, create a new `.sublime-menu` file. Either add only your own stuff, or copy the default content and edit it.
- Style:
  - Themes (`*.sublime-theme`) basically decorate the core UI elements like side-pane, tabs, menus etc.
  - Color schemes are responsible for the syntax-highlighting e.g. `Visual Studio Bold.tmTheme` or `abc.sublime-color-scheme`.
- Menu filess
  - `Main.sublime-menu`: Primary menu for the application
  - `Side Bar Mount Point.sublime-menu`: Context menu for top-level folders in the side bar
  - `Side Bar.sublime-menu`: Context menu for files and folders in the side bar. Has "magic" args for passing file and folder names to commands.Entries with an arg "files": [] will be enabled for files and will pass file names to the command via the arg files. Entries with an arg "dirs": [] will be enabled for folders and will pass file names to the command via the arg dirs. Entries with an arg "paths": [] will be enabled for files and folders and will pass file and folder names to the command via the arg paths.
  - `Tab Context.sublime-menu`: Context menu for file tabs
  - `Context.sublime-menu`: Context menu for text areas
  - `Find in Files.sublime-menu`: Menu shown when clicking the ... button in Find in Files panel
  - `Widget Context.sublime-menu`: Context menu for text inputs in various panels. Technically this file name can be changed via the "context_menu" setting inside of `Widget.sublime-settings`.

