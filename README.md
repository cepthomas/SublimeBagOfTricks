# What It Is
A hodge-podge Sublime Text plugin containing odds and ends missing from or over-developed in other packages.
The focus is not on code development but rather general text processing.

No support as yet for PackageControl.

Built for Windows and ST4. Other OSes and ST versions will require some hacking.

![logo](felix.jpg)


# Commands and Settings

## General

| Setting                  | Description |
|:--------                 |:-------     |
| persistence_path         | Where to store signet and highlight persistence.<br/>`'local'` is sublime-project location<br/>`'store'` is package store<br/>`''` is transient |
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


| Setting                  | Description |
|:--------                 |:-------     |
| highlight_scopes         | List of scope names for marking text - index corresponds to `sbot_highlight_text` arg |


## Scopes
- Show scope stack with styles for selection or all common ones. Useful for figuring out color-schemes.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_show_scopes         | Popup that shows style for all common scopes |
| sbot_scope_info          | Like builtin show_scope_name but with style info added |


| Setting                  | Description |
|:--------                 |:-------     |
| scopes_to_show           | List of scope names for `sbot_show_scopes` command |


## Render To Html
- Simple render to html with styles, primarily for printing.
- Line wrap with optional line numbers.
- Version to render markdown file to html using [Markdeep](https://casual-effects.com/markdeep/).
- Note that relative links (like graphics) are currently broken. If it's important, you can manually copy them to the temp directory.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_render_to_html      | Render current open file including scope colors and highlights to html, arg is include line numbers |
| sbot_render_markdown     | Render current open markdown file to html |


| Setting                  | Description |
|:--------                 |:-------     |
| html_font_face           | For rendered html - usually monospace |
| html_md_font_face        | For rendered markdown - usually prettier than html_font_face |
| html_font_size           | For rendered html/markdown |
| html_background          | Color name if you need to change the bg color (not done automatically from color scheme) |
| render_output            | Where to render to.<br/>`'clipboard'`<br/>`'file'` fn/temp + .html<br/>`'show'`in browser |
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
| sbot_sidebar_copy_file   | Copy selected file to a new file in the same folder |
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
Prettify json and xml and show in a new view.
Was also going to handle html but it's easier to use external or online formatter for this very occasional need.
Also C family files using AStyle (must be in your path).

| Command                  | Description |
|:--------                 |:-------     |
| sbot_format_json         | Format json content - makes C/C++ comments into valid json elements and removes any trailing commas |
| sbot_format_xml          | Format xml content |
| sbot_format_cx_src       | Format C/C++/C# content |


## Miscellany
| Command                  | Description |
|:--------                 |:-------     |
| sbot_split_view          | Toggles simple horizontal split screen |
| sbot_cmd_line            | Simple way to run a quick command |
| sbot_show_eol            | Toggles showing EOLs |


| Setting                  | Description |
|:--------                 |:-------     |
| eol_scope                | Scope name for coloring eols |


# Implementation

## Files
Plugin directory files.

| Directory                | Description |
|:--------                 |:-------     |
| .                        | Standard plugin stuff - menus, commands, scripts, ... |
| store                    | Generated dir: `.*-hls` and `.*-sigs` files if persistence_path is `store` |
| temp                     | Generated dir: Trace files and rendered html |
| test                     | VS solution to do some basic unit testing of sbot functions |
| test\st_emul             | Stubs for the sublime api |
| test\files               | Misc files for testing |


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
ST says `plugin_loaded()` fires only once for all instances of sublime. However you can add this to each module and they all
get called. Safest is to only use it once.


## Module Loading
ST doesn't load modules like plain python and can cause some surprises.
The problem is that sbot_common gets reloaded but it appears to be a different module from the one linked to by the other modules.
This makes handling globals difficult. Modules that are common cannot store meaningful state.

Here's some startup sequence:
```
...
ST: reloading plugin Default.*
ST: reloading plugin SublimeBagOfTricks.__init__
ST: reloading plugin SublimeBagOfTricks.sbot
ST: reloading plugin SublimeBagOfTricks.__init__
ST: reloading plugin SublimeBagOfTricks.sbot
Python: load sbot_common
Python: load sbot
ST: reloading plugin SublimeBagOfTricks.sbot_clean
Python: load sbot_clean
ST: reloading plugin SublimeBagOfTricks.sbot_common
Python: load sbot_common
ST: reloading plugin SublimeBagOfTricks.sbot_format
Python: load sbot_format
ST: reloading plugin SublimeBagOfTricks.sbot_highlight
Python: load sbot_highlight
ST: reloading plugin SublimeBagOfTricks.sbot_misc
Python: load sbot_misc
ST: reloading plugin SublimeBagOfTricks.sbot_render
Python: load sbot_render
ST: reloading plugin SublimeBagOfTricks.sbot_scope
Python: load sbot_scope
ST: reloading plugin SublimeBagOfTricks.sbot_sidebar
Python: load sbot_sidebar
ST: reloading plugin SublimeBagOfTricks.sbot_signet
Python: load sbot_signet
ST: reloading python 3.X plugin my-other-plugins
>>>>>>>>> Manually re-saved sbot_common.py
ST: reloading plugin SublimeBagOfTricks.sbot_common
Python: load sbot_common
...
```
