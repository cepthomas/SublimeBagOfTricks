# Sublime Bag Of Tricks

TODO1 clean up.

A hodge-podge Sublime Text plugin containing odds and ends missing from or over-developed in other packages.

![logo](felix.jpg)

Built for ST4 on Windows and Linux. Caveats:
- For the tree command, Linux needs something like: `sudo apt-get install tree`

`sbot_common.py` contains utilities used by the other sbot plugins. It is copied to those directories rather
than using git submodules. That could change in the future.


Sublime Text plugin to perform some common text clean up: removing white space in different ways.



Also:
- Display absolute text position in status bar next to row/col.



## logging
A simple logger for use by the sbot family of plugins. It works in conjunction with `def slog(str, message)` in
`sbot_common.py`. If this plugin is imported, slog() uses it otherwise slog() writes to stdout.

- Intercepts the ST console write and copies to a file.
- Adds timestamp and (three letter) category.
- If the category appear in `notify_cats`, a dialog is presented. Those in `ignore_cats` are ignored.
- The 'A' in the name enforces loading before other Sbot components.
- Log files are in `.../Packages/User/.SbotStore`.

import logging
`_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)`


## Commands
| Command                 | Menu Type           | Description                                                           | Args     |
| :--------               | :-----------        | :------------                                                         | :------- |
| sbot_split_view         | Context or Sidebar  | Toggle simple split view like VS, Word etc                            |          |
| sbot_copy_name          | Tab or Sidebar      | Copy file/dir name to clipboard                                       |          |
| sbot_copy_path          | Tab or Sidebar      | Copy full file/dir path to clipboard                                  |          |
| sbot_copy_file          | Tab or Sidebar      | Copy selected file to a new file in the same directory                |          |
| sbot_delete_file        | Tab or Context      | Moves the file in current view to recycle/trash bin.                  |          |
| sbot_run                | Context or Sidebar  | Run a script file (py, lua, cmd, bat, sh) and show the output         |          |
| sbot_open               | Context or Sidebar  | Open file (html, py, etc) as if you double clicked it in explorer     |          |
| sbot_terminal           | Context or Sidebar  | Open a terminal here                                                  |          |
| sbot_tree               | Context or Sidebar  | Run tree cmd to new view (win only)                                   |          |
| sbot_open_context_path  | Context             | Open path under cursor if formatted like `[tag](C:\my\best\file.txt)` |          |
| sbot_trim               | Context             | Remove ws from Line ends                                              | how: "leading" OR "trailing" OR "both"                                       |
| sbot_remove_empty_lines | Context             | Like it says                                                          | how: "remove_all" (all lines) OR "normalize" (compact to one)                |
| sbot_remove_ws          | Context             | Like it says                                                          | how: "remove_all" (all ws) OR "keep_eol" OR "normalize" (compact to one ws   |


There are no default context/tab/sidebar menu items. Add the ones you like to your own `*..sublime-menu` files.

context/tab:
```
    { "caption": "Copy Name", "command": "sbot_copy_name"},
    { "caption": "Copy Path", "command": "sbot_copy_path"},
    { "caption": "Copy File", "command": "sbot_copy_file"},
    { "caption": "Delete File", "command": "sbot_delete_file" },

    { "caption": "Trim Leading WS", "command": "sbot_trim", "args" : {"how" : "leading"}  },
    { "caption": "Trim Trailing WS", "command": "sbot_trim", "args" : {"how" : "trailing"}  },
    { "caption": "Trim WS", "command": "sbot_trim", "args" : {"how" : "both"}  },
    { "caption": "Remove Empty Lines", "command": "sbot_remove_empty_lines", "args" : { "how" : "remove_all" } },
    { "caption": "Collapse Empty Lines", "command": "sbot_remove_empty_lines", "args" : { "how" : "normalize" } },
    { "caption": "Remove WS", "command": "sbot_remove_ws", "args" : { "how" : "remove_all" } },
    { "caption": "Remove WS Except EOL", "command": "sbot_remove_ws", "args" : { "how" : "keep_eol" } },
    { "caption": "Collapse WS", "command": "sbot_remove_ws", "args" : { "how" : "normalize" } },
    { "caption": "Insert Line Indexes", "command": "sbot_insert_line_indexes" },
    { "caption": "Scope Info", "command": "sbot_scope_info" },
    { "caption": "All Scopes", "command": "sbot_all_scopes" },
```

Sidebar:
```
    { "caption": "Copy Name", "command": "sbot_copy_name", "args": {"paths": []} },
    { "caption": "Copy Path", "command": "sbot_copy_path", "args": {"paths": []} },
    { "caption": "Copy File", "command": "sbot_copy_file", "args": {"paths": []} },
    { "caption": "Run", "command": "sbot_run", "args": {"paths": []} },
    { "caption": "Terminal Here", "command": "sbot_terminal", "args": {"paths": []} },
    { "caption": "Tree", "command": "sbot_tree", "args": {"paths": []} },
```


## Settings
| Setting            | Description                              | Options                              |
| :--------          | :-------                                 | :------                              |
| scopes_to_show     | Scope list for sbot_all_scopes command.  |                                      |
| log_level          | Min level to log                         | CRITICAL ERROR WARNING INFO DEBUG    |

Right click stuff works better with this global setting:
```
"preview_on_click": "only_left",
```
