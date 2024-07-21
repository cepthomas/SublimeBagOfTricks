
TODO1 update these docs

in each project.: _logger.setLevel(logging.DEBUG)
settings:
// Log level: "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"
"log_level": "DEBUG",


%APPDATA%


# What It Is
Odds and ends in the Sbot family that don't have a better home for now. You can add them to your personal 
Context and/or Sidebar menus.

>>>>>>>> all commands are added into the user Context.sublime-menu. give examples.

A hodge-podge Sublime Text plugin containing odds and ends missing from or over-developed in other packages.
The focus is not on code development but rather general text processing.

![logo](felix.jpg)


Built for ST4 on Windows and Linux. Caveats:
- For the tree command, Linux needs something like: `sudo apt-get install tree`

?? No support as yet for PackageControl.





# SbotUtils

- Display absolute text position in status bar next to row/col.
- One click view splitter that works like VS, Word, etc.
- Run a script file (py, lua, cmd, bat, sh) and show the output.
- Open file (html, py, etc) as if you double clicked it.
- Open terminal in current path.
- Open path under cursor if formatted like `[tag](C:\my\best\file.txt)`


## Commands
| Command                         | Type                | Description                                            |
| :--------                       | :-------            | :-------                                               |
| sbot_split_view                 | Context or Sidebar  | Toggle split view                                      |
| sbot_copy_name                  | Tab or Sidebar      | Copy file/dir name to clipboard                        |
| sbot_copy_path                  | Tab or Sidebar      | Copy full file/dir path to clipboard                   |
| sbot_copy_file                  | Tab or Sidebar      | Copy selected file to a new file in the same directory |
| sbot_delete_file                | Tab or Context      | Moves the file in current view to recycle/trash bin.   |
| sbot_run                        | Context or Sidebar  | Run selected script with output to new view            |
| sbot_open                       | Context or Sidebar  | Like you clicked it in explorer                        |
| sbot_terminal                   | Context or Sidebar  | Open a terminal here                                   |
| sbot_tree                       | Context or Sidebar  | Run tree cmd to new view (win only)                    |
| sbot_open_context_path          | Context             | Open path under cursor                                 |
| sbot_insert_target_from_clip    | Context             | Insert path target from clipboard                      |

Context and Tab menu items like:
`{ "caption": "Copy Name", "command": "sbot_copy_name"},`

Sidebar menu items like:
`{ "caption": "Copy Name", "command": "sbot_copy_name", "args": {"paths": []} },`


## Settings
No internal but the right click stuff works better with this setting:
```
"preview_on_click": "only_left",
```


# SbotClean

Sublime Text plugin to perform some common text clean up: removing white space in different ways.

## Commands
| Command                    | Type     | Description               | Args                                                                         |
| :--------                  | :------- | :-------                  | :-------                                                                     |
| sbot_trim                  | Context  | Remove ws from Line ends  | how: "leading" OR "trailing" OR "both"                                       |
| sbot_remove_empty_lines    | Context  | Like it says              | how: "remove_all" (all lines) OR "normalize" (compact to one)                |
| sbot_remove_ws             | Context  | Like it says              | how: "remove_all" (all ws) OR "keep_eol" OR "normalize" (compact to one ws   |

## Settings
| Setting            | Description         | Options                                                               |
| :--------          | :-------            | :------                                                               |
>>>> | scopes_to_show            |    |    |



# SbotALogger


import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


A simple logger for use by the sbot family of plugins. It works in conjunction with `def slog(str, message)` in
`sbot_common.py`. If this plugin is imported, slog() uses it otherwise slog() writes to stdout.

- Intercepts the ST console write and copies to a file.
- Adds timestamp and (three letter) category.
- If the category appear in `notify_cats`, a dialog is presented. Those in `ignore_cats` are ignored.
- The 'A' in the name enforces loading before other Sbot components.
- Log files are in `%data_dir%\Packages\User\.SbotStore`.

## Exceptions

These are the categories of exceptions in the Sublime python implementation:
- User-handled with the standard `try/except` mechanism.
- Plugin command syntax and functional errors are intercepted and logged by a custom `sys.excepthook` in `sbot_logger.py`.
- Errors in scripts that are executed by sublime internals e.g. `load_module()` are not caught by the above hook but go straight
  to stdout. It *works* but is not as tightly integrated as preferred.

## Commands

None


## Settings

| Setting            | Description                     | Options                                       |
| :--------          | :-------                        | :------                                       |
| file_size          | Max log file before rollover    | in kbytes (0 means disabled)                  |
| ignore_cats        | Ignore these user categories    | comma separated strings                       |
| notify_cats        | Notify user if in categories    | comma separated strings                       |


# Logging in sbot_common


# Implementation here? or in a separate doc?


## General Notes

- In the code, `line` refers to editor lines and is 1-based. `row` refers to buffer contents as an array and is 0-based.
- Project collections, variables, functions, etc use:
    - `persisted` is the json compatible file format.
    - `visual` is the way ST API handles elements.
    - `internal` is the plugin format.
- Commands can't end with `<underscore numeral>` e.g. `my_cmd_1` should be `stpt_cmd1`.
- If you pass a dict as value in View.settings().set(name, value), it seems that the dict key must be a string.

## Error Handling
Because ST takes ownership of the python module loading and execution, it just dumps any load/parse and runtime exceptions
to the console. This can be annoying because it means you have to have the console open pretty much all the time.
First attempt was to hook the console stdout but it was not very cooperative. So now there are try/except around all the
ST callback functions and this works to catch runtime errors and pop up a message box. Import/parse errors still go to the
console so you have to keep an eye open there while developing but they should resolve quickly.


## Event Handling
There are some idiosyncrasies with ST event generation.

### ViewEventListener
Is instantiated once per view and:
- `on_load()` is normally called when the file is loaded. However it is not called if ST startup shows previously opened files,
  or if it is shown as a (single-click) preview.
- `on_close()` is normally called when a view is closed but it does not appear to be consistent. Perhaps if ST is closed
  without closing the views first?

Why does it matter? Highlighting and signets persist their state per file and the application needs to hook the open/close
events in order to do so. Because the two obvious events don't work as expected (by me at least), some
less-than-beautiful hacks happen:
- `on_activated()` is normally called when the view gets focus. This is reliable so is used instead of on_load(), along with
  some stuff to track if it's been initialized.
- `on_deactivated()` is used in place of `on_close()` to save the persistence file every time the view loses focus. Good enough.

### EventListener
Is instantiated once per window (ST instance):
- `on_load_project()` doesn't fire on startup (last) project load.
- `on_exit()` called once after the API has shut down, immediately before the plugin_host process exits.
- `on_pre_close_window()` seems to work.

### Global
ST says `plugin_loaded()` fires only once for all instances of sublime. However you can add this to 
each module and they all get called. Safest is to only use it once.


## Module Loading
ST doesn't load modules like plain python and can cause some surprises. The problem is that sbot_common
gets reloaded but it appears to be a different module from the one linked to by the other modules.
This makes handling globals difficult. Modules that are common cannot store meaningful state.
