#!/usr/bin/env python3
"""PreToolUse (Bash): refuses a tracker write while no card skill is running.

A write is a gh issue edit, comment or create, a gh project item-edit or item-add, an az
boards work-item update, create or relation change, a gh api graphql call carrying a mutation
or taking its query or variables from a file (--input, or -f/-F <key>=@<file>, whose content
cannot be seen), and any other gh api call whose method is not GET: an -X or --method other
than GET, or a field (-f, -F, --raw-field, --field) or --input with no method, which gh sends
as POST. Plain reads pass. Only a live marker of a card-writing skill (create-card, add-to-card,
re-evaluate-card, grill, check-ready, build, coordinate, accept or release) allows a write;
a configure-project or curate marker does not, and markers older than the profile's marker
lifetime do not count.
Silent (allow) on anything else, on a missing profile, on "Tracker guard: off", and on any
error. Never raises; always exits 0.
"""

import re
import sys

sys.dont_write_bytecode = True

try:
    import hooks_lib as lib
except Exception:
    sys.exit(0)

REASON = ('DevFactory: card writes go through the card skills (create-card, add-to-card, '
          're-evaluate-card, grill); none is running.')

CARD_WRITERS = {'create-card', 'add-to-card', 're-evaluate-card', 'grill', 'check-ready',
                'build', 'coordinate', 'accept', 'release'}

FIELD_FLAGS = ['-f', '-F', '--field', '--raw-field', '--input']


def flag_value(words, i):
    w = words[i]
    eq = w.find('=')
    if w.startswith('--'):
        return w[eq + 1:] if eq > 0 else lib.word(words, i + 1)
    # -XPATCH or -X PATCH
    return re.sub(r'^=', '', w[2:], count=1) if len(w) > 2 else lib.word(words, i + 1)


def field_value(args, i):
    """The key=value of a field flag at args[i] (-f, -F, --field, --raw-field, in the
    -fkey=v, -f key=v, --field=key=v and --field key=v forms), or None when it is not one."""
    a = args[i]
    for f in ['-f', '-F']:
        if a == f:
            return lib.word(args, i + 1) or ''
        if a.startswith(f):
            return a[2:]
    for f in ['--field', '--raw-field']:
        if a == f:
            return lib.word(args, i + 1) or ''
        if a.startswith(f + '='):
            return a[len(f) + 1:]
    return None


def is_graphql_write(args):
    """A GraphQL call is a write when it carries a mutation, or when its query or variables come
    from a file or stdin (--input, or a field whose value is @<file>): that content cannot be
    seen, so it may be a mutation."""
    if any(lib.rx(r'\bmutation\b').search(a) for a in args):
        return True
    for i, a in enumerate(args):
        if a == '--input' or a.startswith('--input='):
            return True
        v = field_value(args, i)
        if v is not None and re.search(r'^[^=]*=@', v):
            return True
    return False


def is_gh_api_write(args):
    if lib.word(args, 0) == 'graphql' or 'graphql' in args:
        return is_graphql_write(args)
    method = None
    fields = False
    for i, a in enumerate(args):
        if a == '-X' or a.startswith('-X') or a == '--method' or a.startswith('--method='):
            method = (flag_value(args, i) or '').upper()
        elif any(a == f or a.startswith(f + '=') or (len(f) == 2 and a.startswith(f) and len(a) > 2)
                 for f in FIELD_FLAGS):
            fields = True
    if method is None:
        return fields
    return method != 'GET'


def is_tracker_write(words):
    prog, a, b, c, d = (lib.word(words, i) for i in range(5))
    if lib.is_program(prog, 'gh'):
        if a == 'issue' and b in ('edit', 'comment', 'create'):
            return True
        if a == 'project' and b in ('item-edit', 'item-add'):
            return True
        if a == 'api':
            return is_gh_api_write(words[2:])
        return False
    if lib.is_program(prog, 'az') and a == 'boards' and b == 'work-item':
        if c in ('update', 'create'):
            return True
        if c == 'relation' and d in ('add', 'remove'):
            return True
    return False


def main():
    data = lib.read_input()
    if not isinstance(data, dict) or data.get('tool_name') != 'Bash':
        return
    tool_input = data.get('tool_input')
    command = tool_input.get('command') if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not lib.rx(r'\b(gh|az)\b').search(command):
        return
    if not any(is_tracker_write(lib.command_words(s)) for s in lib.segments(command)):
        return
    root = lib.project_root(lib.input_cwd(data))
    if not lib.has_profile(root):
        return  # no profile: silence
    if lib.hook_off(root, 'Tracker guard'):
        return
    if any(not m['stale'] and m['name'] in CARD_WRITERS for m in lib.markers(root)):
        return
    lib.deny(REASON)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass  # silence on any error
    sys.exit(0)
