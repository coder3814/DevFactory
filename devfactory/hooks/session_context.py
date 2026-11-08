#!/usr/bin/env python3
"""SessionStart: in a project with a DevFactory profile (at the repository root of cwd), prints
the profile path, the lifecycle stages and their columns, the skills to use, the decision
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

    stages = lib.profile_section(root, 'Stages')
    if stages is not None:
        column_field = lib.profile_field(root, 'Stages', 'Column field')
        out.append('Stages (column field: %s):' % column_field if column_field else 'Stages:')
        for line in [l for l in stages if re.search(r'^\s*\|', l)][:9]:
            out.append(line.strip())
    else:
        out.append('Stages: the profile has no Stages section.')

    out.append('Skills: use create-card / add-to-card / re-evaluate-card for cards, grill for '
               'specs, coordinate for a parent issue, build for one card, accept, release.')
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
