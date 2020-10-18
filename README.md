# SublimeBagOfTricks
A work-in-progress Sublime Text plugin containing odds and ends missing from other packages.
The focus is not on code development but rather text processing. It's also an excuse to brush up on my python.

Built for Windows and ST3 but most should work for other OSes and ST2.

# Features

## Colorizing
Word colorizing similar to StyleToken but simpler. Also a handy scope popup that shows you the style
associated with each scope.


| Command                  | Description |
|:--------                 |:-------     |
| sbot_highlight_text      | Highlight text using next in mark_scopes |
| sbot_clear_highlight     | Remove highlight in selection |
| sbot_clear_all_highlights| Remove all highlights |
| sbot_show_scopes         | Popup that shows style for scopes |

| Setting                  | Description |
|:--------                 |:-------     |
| mark_scopes              | List of scopes for marking text |


## Render To Html
Simple render to html with styles, primarily for printing.

| Command                  | Description |
|:--------                 |:-------     |
| sbot_render_html         | Render current file to html |
| sbot_render_markdown     | Render current markdown file to html |

| Setting                  | Description |
|:--------                 |:-------     |
| html_font_face           | For rendered html |
| html_font_size           | For rendered html |
| html_plain_text          | If you need to change the fg for plain (unstyled) text |
| html_background          | If you need to change the bg color (not done automatically from color scheme) |
| html_output              | One of: clipboard, new_file (view), default_file (original filename + .html), default_file_open (default_file + show) |
| html_line_numbers        | Optionally add line numbers |
| md_font_face             | For rendered markdown |
| md_font_size             | For rendered markdown |
| md_background            | If you need to change the markdown bg color (not done automatically from color scheme) |


## Signets (bookmarks)
Enhanced bookmarks:
- Persisted per ST project.
- Next/previous traverses files in project - like VS.
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

## Miscellany

| Command                  | Description |
|:--------                 |:-------     |
| sbot_split_view          | Toggles simple horizontal split screen, like MS products |

## SideBar
Commands added to the sidebar.

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

