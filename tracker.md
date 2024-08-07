# Tracker

![](felix.jpg)

Odds and ends missing from, or overly complicated in other Sublime Text plugins.
`sbot.py` is a sandard ST plugin with a variety of commands that process text, simplify ST internals,
interact with the OS, etc. Displays absolute text position in status bar next to row/col.

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
