#!/usr/bin/env python3
"""PreToolUse (Bash, PowerShell): refuses a tracker write while no skill that writes cards is
running.

A gh issue, gh project, gh label or az boards work-item command is a write unless it is a
known read: gh issue view, list or status; gh project view, list, item-list or field-list;
gh label list; az boards work-item show, and az boards work-item relation show or list-type;
any of them asking for --help. A gh api call is a write unless it is a GET: a graphql call
carrying a mutation or taking its query or variables from a file (--input, or -f/-F
<key>=@<file>, whose content cannot be seen), an -X or --method other than GET, or a field
(-f, -F, --raw-field, --field) or --input with no method, which gh sends as POST. An az rest
call is a write when its method (--method or -m, GET by default) is not GET and its URL names
a work-item API (`_apis/wit`) or cannot be seen (missing, or holding a $ variable). Every
other gh and az command passes. The commands are found in each part of the command line,
also inside `bash -c`, `sh -c` and `powershell -Command`.

Only a fresh marker of a skill that writes cards (create-card, add-to-card, re-evaluate-card,
grill, check-ready, build, coordinate, accept, release or configure-project) allows a write,
in the project's root or begun earlier in the same command line (`devfactory begin <skill>`,
joined by &&, ; or a newline); markers older than the profile's marker lifetime do not count.
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

REASON = ('DevFactory: tracker writes go through the card skills (create-card, add-to-card, '
          're-evaluate-card) or grill, check-ready, build, coordinate, accept, release or '
          'configure-project; none is running. The known reads need none: gh issue '
          'view|list|status, gh project view|list|item-list|field-list, gh label list, a GET '
          'gh api or az rest call, az boards work-item show.')

CARD_WRITERS = {'create-card', 'add-to-card', 're-evaluate-card', 'grill', 'check-ready',
                'build', 'coordinate', 'accept', 'release', 'configure-project'}

GH_READS = {
    'issue': {'view', 'list', 'status'},
    'project': {'view', 'list', 'item-list', 'field-list'},
    'label': {'list'},
}
AZ_WORK_ITEM_READS = {'show'}
AZ_RELATION_READS = {'show', 'list-type'}
HELP = {'--help', '-h'}

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


def gh_subcommand(args):
    """The first word after a gh area that is not a flag, skipping the -R/--repo value."""
    i = 0
    while i < len(args):
        a = args[i]
        if a in ('-R', '--repo'):
            i += 2
            continue
        if not a.startswith('-'):
            return a
        i += 1
    return None


def is_az_rest_write(args):
    method = 'GET'
    url = None
    for i, a in enumerate(args):
        name, eq, value = a.partition('=')
        if name in ('--method', '-m'):
            method = (value if eq else lib.word(args, i + 1) or '').upper()
        elif name in ('--url', '--uri', '-u'):
            url = value if eq else lib.word(args, i + 1)
    if method == 'GET':
        return False
    return url is None or '$' in url or '_apis/wit' in url.lower()


def is_tracker_write(words):
    prog = lib.word(words, 0)
    if lib.is_program(prog, 'gh'):
        area = lib.word(words, 1)
        if area in GH_READS:
            sub = gh_subcommand(words[2:])
            if sub is None or HELP & set(words):
                return False
            return sub not in GH_READS[area]
        if area == 'api':
            return is_gh_api_write(words[2:])
        return False
    if lib.is_program(prog, 'az'):
        a, b, c, d = (lib.word(words, i) for i in range(1, 5))
        if a == 'boards' and b == 'work-item':
            if c is None or HELP & set(words):
                return False
            if c == 'relation':
                return d is not None and d not in AZ_RELATION_READS
            return c not in AZ_WORK_ITEM_READS
        if a == 'rest':
            return not (HELP & set(words)) and is_az_rest_write(words[2:])
    return False


def unmarked_write(command, shell):
    """Whether a part of the command writes the tracker with no card-writing skill begun
    earlier in the same command."""
    begun = set()
    for item in lib.flatten(lib.commands(command, shell)):
        skill = lib.begun_skill(item['words'])
        if skill:
            if item['join'] not in lib.BROKEN_JOINS:
                begun.add(skill)
        elif is_tracker_write(item['words']) and not (begun & CARD_WRITERS):
            return True
    return False


def main():
    data = lib.read_input()
    if not isinstance(data, dict) or data.get('tool_name') not in lib.SHELL_TOOLS:
        return
    tool_input = data.get('tool_input')
    command = tool_input.get('command') if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not lib.might_run(command, r'\b(gh|az)\b'):
        return
    if not unmarked_write(command, lib.shell_of(data)):
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
