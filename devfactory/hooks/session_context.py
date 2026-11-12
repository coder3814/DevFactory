#!/usr/bin/env python3
"""SessionStart: in a project with a DevFactory profile (at the repository root of cwd), prints
the profile path, the event hooks in .devfactory/hooks/, every skill by its full name
(devfactory:<name>) with what it is for, the decision
line, the active markers and any stale ones, in under 25 lines. Silent on a missing profile,
on "Session context: off", and on any error.
"""

import os
import re
import sys

sys.dont_write_bytecode = True

try:
    import hooks_lib as lib
except Exception:
    sys.exit(0)

MAX_LINES = 24


def main():
    try:
        data = lib.read_input()
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    root = lib.project_root(lib.input_cwd(data))
    if not lib.has_profile(root):
        return  # no profile: silence
    if lib.hook_off(root, 'Session context'):
        return

    out = ['DevFactory profile: %s' % os.path.join(root, '.devfactory', 'profile.md')]

    hooks_dir = os.path.join(root, '.devfactory', 'hooks')
    events = {'request-met', 'ready', 'approved', 'work-started', 'development-started', 'readiness-lost',
              'done', 'refused', 'accepted', 'released'}
    found = sorted(f for f in (os.listdir(hooks_dir) if os.path.isdir(hooks_dir) else [])
                   if os.path.splitext(f)[0].lower() in events)
    out.append('Event hooks in .devfactory/hooks/: %s.' % ', '.join(found) if found
               else 'Event hooks: none in .devfactory/hooks/; the plugin moves no card on the board.')

    out.append('Skills: devfactory:start to start work on a card (it hands a parent issue to '
               'devfactory:coordinate and a standalone card to devfactory:build); '
               'devfactory:create-card / devfactory:add-to-card / devfactory:re-evaluate-card '
               'for cards; devfactory:grill for specs; devfactory:check-ready for readiness; '
               'devfactory:accept; devfactory:release; devfactory:curate after a release; '
               'devfactory:configure-project for the profile.')
    out.append('Decision line: the requester decides what an observer sees or can do, what '
               'persisted data ends up as, and scope; the developer decides internal structure, '
               'anything a recorded decision, the profile or existing code already answers, and '
               'anything the spec delegates.')

    markers = lib.markers(root)

    def label(m):
        a = re.search(r'\((\S+) ago', m['line'])
        return '%s (%s)' % (m['name'], a.group(1)) if a else m['name']
    active = [m for m in markers if not m['stale']]
    stale = [m for m in markers if m['stale']]
    out.append('Active card skill markers: %s.' % ', '.join(label(m) for m in active) if active
               else 'No card skill is running (no fresh marker in .devfactory/.active/).')
    if stale:
        out.append('Stale markers, which the guards ignore: %s; '
                   'clear them with the script\'s "markers --clear-stale".' % ', '.join(label(m) for m in stale))

    lib.emit('\n'.join(out[:MAX_LINES]) + '\n')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass  # silence on any error
    sys.exit(0)
