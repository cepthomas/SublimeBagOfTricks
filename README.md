# Sublime Bag Of Tricks

![](felix.jpg)

Odds and ends missing from, or overly complicated in other Sublime Text plugins.
It consists of two components:
- `sbot.py` is a sandard ST plugin with a variety of commands that process text, simplify ST internals,
  interact with the OS, etc. Displays absolute text position in status bar next to row/col.
- `sbot_common_master.py` contains internal utilities and logging used by the other sbot family plugins. Probably nothing
  of interest to you. Currently it is copied to those directories rather than using git submodules.

The plugin can be installed as is but if you only want a few features it makes sense to snip the
parts of interest, as text or fork or whatever.

Built for ST4 on Windows and Linux.

## Commands

Supported menu type is <b>C</b>ontext, <b>S</b>idebar, <b>T</b>ab.

| Command                 | Menu | Description                                                    | Args          |
| :--------               | :--- | :------------                                                  | :-------      |
| sbot_split_view         | C S  | Toggle simple split view like VS, Word etc.                    |               |
| sbot_copy_name          | S T  | Copy file/dir name to clipboard.                               | *             |
| sbot_copy_path          | S T  | Copy full file/dir path to clipboard.                          | *             |
| sbot_copy_file          | S T  | Copy selected file to a new file in the same directory.        | *             |
| sbot_delete_file        | C T  | Moves the file in current view to recycle/trash bin.           |               |
| sbot_run                | C S  | Run a script file (py, lua, cmd, bat, sh) and show the output. |               |
| sbot_open               | C S  | Open file (html, py, etc) as if you double clicked it.         | *             |
| sbot_terminal           | C S  | Open a terminal here.                                          | *             |
| sbot_tree               | C S  | Run tree cmd to new view.                                      | *             |
| sbot_open_context_path  | C    | Open path under cursor like `[tag](C:\my\file.txt)`            |               |
| sbot_trim               | C    | Remove ws from Line ends.  | how: leading or trailing or both                  |
| sbot_remove_empty_lines | C    | Like it says.              | how: remove_all or normalize ( to one)            |
| sbot_remove_ws          | C    | Like it says.              | how: remove_all or keep_eol or normalize (to one) |

* S needs `"args": {"paths": []}`.

There are no default `context/tab/sidebar.sublime-menu` files in this plugin.
Add the ones you like to your own `*..sublime-menu` files. Typical entries are:
``` json
{ "caption": "Copy Name", "command": "sbot_copy_name"},
{ "caption": "Copy Path", "command": "sbot_copy_path"},
{ "caption": "Copy File", "command": "sbot_copy_file"},
{ "caption": "Delete File", "command": "sbot_delete_file" },
{ "caption": "Split View 2 Pane", "command": "sbot_split_view" },
{ "command": "sbot_open_context_path" },
{ "caption": "Run", "command": "sbot_run" },
{ "caption": "Terminal Here", "command": "sbot_terminal" },
{ "caption": "Tree", "command": "sbot_tree" },
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


## Settings
| Setting            | Description                              | Options                              |
| :--------          | :-------                                 | :------                              |
| scopes_to_show     | Scope list for sbot_all_scopes command.  |                                      |
| log_level          | Min level to log                         | CRITICAL ERROR WARNING INFO DEBUG    |

Right click stuff works best with this global setting:
```
"preview_on_click": "only_left",
```
