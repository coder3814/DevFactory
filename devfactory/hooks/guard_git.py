#!/usr/bin/env python3
"""PreToolUse (Bash): keeps the integration branch and parent branches from being changed
outside the skills that own them, and refuses every push outside release and coordinate.

Refused: `git push`; and `git merge`, `git pull`, `git rebase`, `git cherry-pick`,
`git reset --hard`, `git commit --amend` and `git branch -f` when the branch they change
(HEAD in the effective directory, `cwd` after any `cd <dir>` and `git -C <dir>`, the branch a
rebase names, or the branch `git branch -f` moves) is protected. Merging, pulling or rebasing
a protected branch into an unprotected one is never refused. Allowed: everything while a
`release` or `coordinate` marker is fresh; under `build`, a `git merge --ff-only` onto a
parent branch; under `grill`, a `git merge --ff-only` onto the integration branch (a plain
`git commit` is never refused). Markers older than the profile's marker lifetime are ignored.
Silent (allow) on a missing profile, on "Git guard: off", and on any error. Never raises;
always exits 0.
"""

import os
import re
import sys

sys.dont_write_bytecode = True

try:
    import hooks_lib as lib
except Exception:
    sys.exit(0)

GLOBAL_WITH_VALUE = {'-C', '-c', '--git-dir', '--work-tree', '--namespace', '--exec-path', '--config-env'}
VALUE_OPTIONS = {
    'merge': {'-m', '-s', '-X', '-F', '--strategy', '--strategy-option', '--file',
              '--message', '--into-name', '--cleanup'},
    'rebase': {'-s', '-X', '-x', '--exec', '--strategy', '--strategy-option', '--onto'},
    'pull': {'-s', '-X', '-j', '-o', '--strategy', '--strategy-option', '--depth',
             '--deepen', '--shallow-since', '--shallow-exclude', '--jobs', '--upload-pack',
             '--server-option', '--negotiation-tip'},
    'cherry-pick': {'-m', '-X', '-s', '--mainline', '--strategy', '--strategy-option', '--cleanup'},
    'branch': {'-u', '--set-upstream-to', '--sort', '--format', '--points-at',
               '--contains', '--no-contains', '--merged', '--no-merged'},
    'reset': set(),
    'commit': {'-m', '-F', '-C', '-c', '-t', '--message', '--file', '--reuse-message',
               '--reedit-message', '--template', '--author', '--date', '--fixup', '--squash',
               '--cleanup', '--trailer'},
}


def resolve(base, p):
    return os.path.abspath(os.path.join(base, p))


def parse_git(words, d):
    """Parses one segment's command words into {sub, args, flags, raw, dir} when it runs git."""
    if not lib.is_program(lib.word(words, 0), 'git'):
        return None
    i = 1
    git_dir = d
    while i < len(words) and words[i].startswith('-'):
        opt = words[i]
        if opt == '-C' and i + 1 < len(words):
            git_dir = resolve(git_dir, words[i + 1])
            i += 2
        elif opt in GLOBAL_WITH_VALUE:
            i += 2
        else:
            i += 1
    sub = lib.word(words, i)
    if not sub:
        return None
    takes_value = VALUE_OPTIONS.get(sub, set())
    args = []
    flags = []
    raw = []
    j = i + 1
    while j < len(words):
        w = words[j]
        if w == '--':
            pass
        elif w.startswith('-'):
            flags.append(w.split('=')[0])
            raw.append(w)
            if w in takes_value:
                j += 1
        else:
            args.append(w)
        j += 1
    return {'sub': sub, 'args': args, 'flags': flags, 'raw': raw, 'dir': git_dir}


def has_short(git, letter):
    """Whether a short-option word such as -f or -fq carries the letter."""
    return any(lib.rx(r'^-[A-Za-z]+\Z').search(w) and letter in w for w in git['raw'])


def pull_rebases(git):
    """Whether a pull rebases: -r or --rebase[=<mode>], unless the last word says otherwise."""
    rebase = False
    for w in git['raw']:
        if w in ('-r', '--rebase'):
            rebase = True
        elif w.startswith('--rebase='):
            rebase = not re.search(r'^--rebase=(false|no|off|0)\Z', w, re.I)
        elif w == '--no-rebase':
            rebase = False
    return rebase


def op(kind, d, branch=None):
    return {'kind': kind, 'dir': d, 'branch': branch}


def classify(git):
    """What a git invocation would do to a branch: {kind, dir, branch} or None when it changes
    no branch the guard cares about. A None branch means HEAD in dir."""
    def has(f):
        return f in git['flags']
    sub = git['sub']
    d = git['dir']
    if sub == 'push':
        return op('push', d)
    if sub == 'merge':
        if has('--abort') or has('--quit'):
            return None
        return op('fast-forward' if has('--ff-only') else 'merge', d)
    if sub == 'pull':
        # A pull merges, fast-forwards or rebases onto HEAD; it is never the plain fast-forward
        # a build or grill marker allows, which is `git merge --ff-only`.
        kind = 'pull'
        if pull_rebases(git):
            kind = 'pull --rebase'
        elif has('--ff-only'):
            kind = 'pull --ff-only'
        return op(kind, d)
    if sub == 'cherry-pick':
        if has('--abort') or has('--quit'):
            return None
        return op('cherry-pick', d)
    if sub == 'branch':
        # `git branch -f <name> [<start>]` moves the branch it names.
        if not (has('--force') or has_short(git, 'f')) or not lib.word(git['args'], 0):
            return None
        return op('branch -f', d, git['args'][0])
    if sub == 'rebase':
        if any(has(f) for f in ('--abort', '--quit', '--edit-todo', '--show-current-patch')):
            return None
        # `git rebase <upstream> <branch>` (or `--root <branch>`) rebases the branch it names.
        named = lib.word(git['args'], 0) if has('--root') else lib.word(git['args'], 1)
        return op('rebase', d, named or None)
    if sub == 'reset':
        return op('reset --hard', d) if has('--hard') else None
    if sub == 'commit':
        return op('commit --amend', d) if has('--amend') else None
    return None


def current_branch(d):
    r = lib.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=d, timeout=5)
    if r.error is not None or r.status != 0:
        return ''
    b = r.stdout.strip()
    return '' if b == 'HEAD' else b


def pattern_regex(pattern):
    """A parent-branch pattern such as parent-<N>: <N> is digits, any other <placeholder> is a
    run of branch-name characters, everything else is literal."""
    if not pattern:
        return None
    source = ''
    for part in re.split(r'(<[^>]+>)', pattern):
        if not part:
            continue
        if re.fullmatch(r'<n>', part, re.I):
            source += '[0-9]+'
        elif re.fullmatch(r'<[^>]+>', part):
            source += '[A-Za-z0-9._/-]+'
        else:
            source += re.escape(part)
    return re.compile(source)


def normalise_branch(name):
    s = re.sub(r'^refs/heads/', '', str(name), count=1)
    s = re.sub(r'^refs/remotes/', '', s, count=1)
    return re.sub(r'^origin/', '', s, count=1)


def guard_for(root, cache):
    """The guard's view of one project root: whether it is on, and its protected branches."""
    if root in cache:
        return cache[root]
    guard = None
    if lib.has_profile(root) and not lib.hook_off(root, 'Git guard'):
        integration = lib.first_token(lib.profile_field(root, 'Branches and merging', 'Integration branch'))
        parent_re = pattern_regex(lib.first_token(lib.profile_field(root, 'Branches and merging', 'Parent branch')))
        guard = {
            'is_integration': lambda b: bool(integration) and bool(b) and normalise_branch(b) == integration,
            'is_parent': lambda b: parent_re is not None and bool(b) and parent_re.fullmatch(normalise_branch(b)) is not None,
        }
    cache[root] = guard
    return guard


def fresh_markers(roots, cache):
    names = set()
    for root in roots:
        if root not in cache:
            cache[root] = [m['name'] for m in lib.markers(root) if not m['stale']]
        names.update(cache[root])
    return names


def decide(o, guard, active):
    if 'release' in active or 'coordinate' in active:
        return None
    if o['kind'] == 'push':
        if 'build' in active:
            return ('DevFactory: a build session never pushes; a push is the release, which goes through '
                    'the release skill.')
        return ('DevFactory: a push goes through the release skill, or coordinate for a parent issue; '
                'neither is running.')
    branch = normalise_branch(o['branch']) if o['branch'] else current_branch(o['dir'])
    integration = guard['is_integration'](branch)
    parent = not integration and guard['is_parent'](branch)
    if not integration and not parent:
        return None
    if 'build' in active and parent and o['kind'] == 'fast-forward':
        return None
    if 'grill' in active and integration and o['kind'] == 'fast-forward':
        return None
    which = 'the integration branch' if integration else 'a parent branch'
    return ('DevFactory: this git %s changes %s, %s, which only release or '
            'coordinate may change; a build session may only fast-forward a parent branch '
            '(git merge --ff-only), and grill may only commit its spec (git commit, without '
            '--amend) or fast-forward it (git merge --ff-only) onto the integration branch.' % (o['kind'], branch, which))


def main():
    data = lib.read_input()
    if not isinstance(data, dict) or data.get('tool_name') != 'Bash':
        return
    tool_input = data.get('tool_input')
    command = tool_input.get('command') if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not lib.rx(r'\bgit\b').search(command):
        return
    cwd = lib.input_cwd(data)

    ops = []
    d = cwd
    for segment in lib.segments(command):
        words = lib.command_words(segment)
        if lib.word(words, 0) in ('cd', 'pushd') and lib.word(words, 1):
            d = resolve(d, words[1])
            continue
        git = parse_git(words, d)
        o = git and classify(git)
        if o:
            ops.append(o)
    if not ops:
        return

    session_root = lib.project_root(cwd)
    guards = {}
    marker_cache = {}
    for o in ops:
        root = lib.project_root(o['dir'])
        guard = guard_for(root, guards)
        if not guard:
            continue
        # A marker counts in the target's root or the session's own (a build session's marker
        # lives in its worktree while it fast-forwards the parent's).
        reason = decide(o, guard, fresh_markers([root, session_root], marker_cache))
        if reason:
            lib.deny(reason)
            return


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass  # silence on any error
    sys.exit(0)
