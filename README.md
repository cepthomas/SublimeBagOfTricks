
# What It Is
A hodge-podge Sublime Text plugin containing odds and ends missing from or over-developed in other packages.
The focus is not on code development but rather general text processing.

No support as yet for PackageControl.

Built for Windows and ST4. Other OSes and ST versions will require some hacking.

![logo](felix.jpg)


# Commands and Settings



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
ST says `plugin_loaded()` fires only once for all instances of sublime. However you can add this to 
each module and they all get called. Safest is to only use it once.


## Module Loading
ST doesn't load modules like plain python and can cause some surprises. The problem is that sbot_common
gets reloaded but it appears to be a different module from the one linked to by the other modules.
This makes handling globals difficult. Modules that are common cannot store meaningful state.
