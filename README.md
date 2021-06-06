# What It Is
A hodge-podge Sublime Text plugin containing odds and ends missing from or over-developed in other packages.
The focus is not on code development but rather general text processing.

No support as yet for PackageControl.

Built for Windows and ST3. Seems to be happy with ST4. Other OSes and ST2 might require some hacking.

![logo](felix.jpg)


# Commands and Settings

## General

| Setting                  | Description |
|:--------                 |:-------     |
| persistence_path         | Where to store signet and highlight persistence.<br/>`'local'` is sublime-project location<br/>`'store'` is package store<br/>`''` is none
| sel_all                  | Option for selection defaults: if true and no user selection, assumes the whole document (like ST) |


## Highlighting
- Word colorizing similar to [StyleToken](https://github.com/vcharnahrebel/style-token).
- Persists to sbot project file.
- Also a handy scope popup that shows you the style associated with each scope.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_highlight_text      | Highlight text 1 through 6 from `highlight_scopes` |
| sbot_clear_highlight     | Remove highlight in selection |
| sbot_clear_all_highlights| Remove all highlights |
| sbot_show_scopes         | Popup that shows style for scopes |
| sbot_show_eol            | Toggles showing EOLs |


| Setting                  | Description |
|:--------                 |:-------     |
| highlight_scopes         | List of scope names for marking text - index corresponds to `sbot_highlight_text` arg |
| highlight_scopes_to_show | List of scope names for `sbot_show_scopes` command |
| highlight_eol_scope      | Scope name for coloring eols |


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
| html_background          | Color name if you need to change the bg color (not done automatically from color scheme) |
| html_line_numbers        | Optionally add line numbers |
| md_font_face             | For rendered markdown |
| md_font_size             | For rendered markdown |
| md_background            | If you need to change the markdown bg color (not done automatically from color scheme) |
| render_output            | Where to render to.<br/>`'clipboard'`<br/>`'file'` original fn or temp + .html<br/>`'show'`in browser |
| render_max_file          | Max file size in Mb to render |


## Signets (bookmarks)
Enhanced bookmarks:
- `Bookmark` and `mark` are already taken so I shall use `signet` which means in French:
> "Petit ruban ou filet qu'on insère entre les feuillets d'un livre pour marquer l'endroit que l'on veut retrouver."
- Persists to sbot-sigs file.
- Next/previous (optionally) traverses files in project - like VS.
- Bookmark key mappings have been stolen:
    - `ctrl+f2`: sbot_toggle_signet
    - `f2`: sbot_next_signet
    - `shift+f2`: sbot_previous_signet
    - `ctrl+shift+f2`: sbot_clear_signets

| Command                  | Description |
|:--------                 |:-------     |
| sbot_toggle_signet       | Toggle at row |
| sbot_next_signet         | Goto next |
| sbot_previous_signet     | Goto previous |
| sbot_clear_signets       | Clear all |
  
| Setting                  | Description |
|:--------                 |:-------     |
| signet_scope             | Scope name for gutter icon color |
| signet_nav_files         | Next/prev traverses all files otherwise just current file |


## SideBar
Commands added to the sidebar. Like SideBarEnhancements but just the stuff I want.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_sidebar_copy_name   | Copy file/dir name to clipboard |
| sbot_sidebar_copy_path   | Copy full file/dir path to clipboard |
| sbot_sidebar_terminal    | Open a Windows Terminal here |
| sbot_sidebar_open_folder | Open a Windows Explorer here |
| sbot_sidebar_open_browser| Open html file in your browser |
| sbot_sidebar_tree        | Run tree cmd to new view |
| sbot_sidebar_exec        | Run selected executable to new view |
| sbot_sidebar_exclude     | Hide selected file/dir in project |


## Cleaning
Trimming etc.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_trim                | Line ends ws trim, arg `'how'`:<br/>`'leading'`<br/>`'trailing'`<br/>`'both'` |
| sbot_remove_empty_lines  | Like it says, arg `'how'`:<br/>`'remove_all'`all lines<br/>`'normalize' `compact to one |
| sbot_remove_ws           | Like it says, arg `'how'`:<br/>`'remove_all'`all ws<br/>`'keep_eol'`keep eols<br/>`'normalize' `compact to one ws |


## Format
Prettify json and xml. Was also going to handle html but it's easier to just to used an online formatter for this very occasional need.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_format_json         | Format json content and show in new view - makes C++ (not C!) comments into valid json elements and removes any trailing commas |
| sbot_format_xml          | Format xml content and show in new view |


## Miscellany
| Command                  | Description |
|:--------                 |:-------     |
| sbot_split_view          | Toggles simple horizontal split screen |
| sbot_cmd_line            | Simple way to run a quick command |


# Files
Plugin files.

| Directory                | Description |
|:--------                 |:-------     |
| .                        | Standard plugin stuff - menus, commands, scripts, ... |
| store                    | `.*-hls` and `.*-sigs` files if persistence_path is `store` |
| temp                     | Trace files and rendered html |
| test                     | VS solution to do some basic unit testing of sbot functions |
| test\st_emul             | Stubs for the sublime api |
| test\files               | Misc files for testing |


# Notes

Accumulated notes and discoveries. These pertain to ST3, ST4 may have changed.
- In general, `line` refers to editor lines and is 1-based. `row` refers to buffer contents as an array and is 0-based.
- Project collections, variables, functions, etc use:
  - `persisted` is the json compatible file format.
  - `visual` is the way ST API handles elements.
  - `internal` is the plugin format.
- Commands can't end with `<underscore numeral>` e.g. `my_cmd_1` should be `stpt_cmd1`.
- `package-metadata.json` is used for package management so remove it while developing/debugging plugins because PackageControl
  will delete the entire package.
- If you pass a dict as value in View.settings().set(name, value), it seems that the dict key must be a string.
