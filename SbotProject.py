import os
import sys
import traceback
import sublime
import sublime_plugin
import SbotCommon


# All the projects.
sbot_projects = {} # {k:window_id v:SbotProject}

SBOT_PROJECT_EXT = '.sbot-project'


#-----------------------------------------------------------------------------------
class SbotProject(object):
    ''' Container for project (sbot, not st) info. Converts persisted to/from internal. '''

    def __init__(self, project_fn):
        self.fn = project_fn.replace('.sublime-project', SBOT_PROJECT_EXT)

        # Need this because ST window/view lifecycle is unreliable.
        self.views_inited = set()

        # If enabled, unpack persisted data into our internal convenience collections. Otherwise create empties.
        self.signets = {} # k:filename v:[rows]
        self.highlights = {} # k:filename v:[tokens]  tokens={"token": "abc", "whole_word": true, "scope": "comment"}

        if SbotCommon.settings.get('enable_persistence', True):
            try:
                with open(self.fn, 'r') as fp:
                    values = json.load(fp)

                    if 'signets' in values:
                        for sig in values['signets']:
                            if os.path.exists(sig['filename']): # sanity check
                                self.signets[sig['filename']] = sig['rows']

                    if 'highlights' in values:
                        for hl in values['highlights']:
                            if os.path.exists(hl['filename']): # sanity check
                                self.highlights[hl['filename']] = hl['tokens']

            except FileNotFoundError as e:
                # Assumes new file.
                sublime.status_message('Creating new sbot project file')

            except:
                s = 'bad thing!' + traceback.format_exc()
                sublime.error_message(s)

    def save(self):
        if SbotCommon.settings.get('enable_persistence', True):
            try:
                sigs = []
                hls = []
                values = {}

                # Persist our internal convenience collections as json.
                for filename, rows in self.signets.items():
                    if len(rows) > 0:
                        if filename is not None and os.path.exists(filename): # sanity check
                            sigs.append({'filename': filename, 'rows': rows})
                    values['signets'] = sigs

                for filename, tokens in self.highlights.items():
                    if len(tokens) > 0:
                        if filename is not None and os.path.exists(filename): # sanity check
                            hls.append({'filename': filename, 'tokens': tokens})
                    values['highlights'] = hls

                with open(self.fn, 'w') as fp:
                    json.dump(values, fp, indent=4)

            except:
                s = 'bad thing!' + traceback.format_exc()
                sublime.error_message(s)


#-----------------------------------------------------------------------------------
def get_project(view):
    ''' Get the sbot project for the view. None if invalid. '''
    sproj = None
    id = view.window().id()
    if id in sbot_projects:
        sproj = sbot_projects[id]
    return sproj


#-----------------------------------------------------------------------------------
def load_project_maybe(v):
    ''' This is kind of crude but there is no project loaded event (ST4 has on_load_project() though...) '''
    sproj = None
    global sbot_projects
    winid = v.window().id()

    # Persisted to internal. Check for already loaded.
    if winid not in sbot_projects:
        fn = v.window().project_file_name()
        if fn is not None:
            # Load the project file.
            sproj = SbotProject(fn)
            sbot_projects[winid] = sproj
    else:
        sproj = sbot_projects[winid]

    # If this is the first time through and project has signets and/or highlights for this file, get them all.
    if sproj is not None and v.id() not in sproj.views_inited:
        sproj.views_inited.add(v.id())

        # Process signets internal to visual.
        if v.file_name() in sproj.signets:
            _toggle_signet(v, sproj.signets.get(v.file_name(), []))

        # Process highlights internal to visual.
        if v.file_name() in sproj.highlights:
            for tok in sproj.highlights.get(v.file_name(), {}):
                highlight_view(v, tok['token'], tok['whole_word'], tok['scope'])

