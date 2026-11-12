#!/usr/bin/env python3
"""PreToolUse (Bash, PowerShell): keeps the integration branch and parent branches from being
changed outside the skills that own them, and refuses every push outside release and
coordinate.

Refused: `git push`; and, when the branch they change is protected, `git merge`, `git pull`,
`git rebase`, `git cherry-pick`, `git reset --hard`, a `git reset` to a revision other than
the one the branch is at (in any mode), `git commit --amend`, `git branch -f`, `git branch
-m|-M` of it (and -M or -C onto it), `git branch -d|-D` of it, `git update-ref` of
`refs/heads/<branch>` (or of HEAD), and `git checkout -B` or `git switch -C` of it. The branch
changed is HEAD in the effective directory (`cwd` after any `cd <dir>` and `git -C <dir>`),
or the branch the command names (the branch a rebase names, the one `git branch` moves,
renames or deletes, the ref update-ref writes, the one checkout -B or switch -C resets). A
`git checkout <branch>` or `git switch <branch>` earlier in the same command line sets the
branch later parts are judged against. A `git reset` with no revision, to the revision the
branch is at (`git reset HEAD`), or of paths (`git reset -- <path>`, `git reset <rev>
<path>`) moves no branch and is allowed. Every directory a command targets (`cd`, `-C`,
`--git-dir`, `--work-tree`, the session's cwd) is resolved to one canonical form first, so a
drive path with either slash, `/c/x` and `/cygdrive/c/x` are one place. A target the guard
cannot resolve to a repository, a `git -c alias.<name>=...` invocation and `git update-ref
--stdin` are refused in a guarded session. The commands are found in each part of the
command line, also inside `bash -c`, `sh -c` and `powershell -Command`. Merging, pulling or
rebasing a protected branch into an unprotected one is never refused.

Allowed: everything while a `release` or `coordinate` marker is fresh; under `build`, a `git
merge --ff-only` onto a parent branch; under `grill`, `create-card`, `re-evaluate-card`,
`check-ready` or `curate`, a `git merge --ff-only` onto the integration branch, which lands a
spec, a receipt or a profile change (a plain `git commit` is never refused). A marker counts in the target's
root or the session's own, except that a session whose own root holds a fresh `build` marker
gains nothing from a `release` or `coordinate` marker in another root. A `devfactory begin
<skill>` earlier in the same command line (joined by &&, ; or a newline) counts as that
skill's fresh marker for the rest of it. Markers older than the profile's marker lifetime
are ignored. Silent (allow) on a missing profile, on "Git guard: off", and on any error.
Never raises; always exits 0.
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
    'update-ref': {'-m'},
}
CREATE_FLAGS = {
    'checkout': {'-b': False, '-B': True, '--orphan': False},
    'switch': {'-c': False, '-C': True, '--create': False, '--force-create': True, '--orphan': False},
}
CD_COMMANDS = {'cd', 'pushd', 'chdir', 'sl', 'set-location', 'push-location'}
OWNERS = {'release', 'coordinate'}
FAST_FORWARD_ONTO_INTEGRATION = {'grill', 'create-card', 're-evaluate-card', 'check-ready', 'curate'}


def resolve(base, p):
    return lib.canonical(base, p)


def parse_git(words, d):
    """Parses one segment's command words into {sub, args, dashdash, flags, raw, rest, dir,
    options, alias} when it runs git: args are the positional words, dashdash whether a `--`
    came among them, rest every word after the subcommand, and alias whether a -c or
    --config-env option defines an alias."""
    if not lib.is_program(lib.word(words, 0), 'git'):
        return None
    i = 1
    git_dir = d
    options = []
    alias = False
    while i < len(words) and words[i].startswith('-'):
        opt = words[i]
        name, eq, value = opt.partition('=')
        if opt == '-C' and i + 1 < len(words):
            git_dir = resolve(git_dir, words[i + 1])
            i += 2
        elif name in ('--git-dir', '--work-tree'):
            if not eq:
                value = lib.word(words, i + 1) or ''
                i += 1
            # Resolved against the -C directory before it, as git does.
            options += [name, resolve(git_dir, value)]
            i += 1
        elif opt == '-c' or name == '--config-env':
            if not eq:
                value = lib.word(words, i + 1) or ''
                i += 1
            alias = alias or value.lower().startswith('alias.')
            i += 1
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
    dashdash = False
    j = i + 1
    while j < len(words):
        w = words[j]
        if w == '--':
            dashdash = True
        elif w.startswith('-'):
            flags.append(w.split('=')[0])
            raw.append(w)
            if w in takes_value:
                j += 1
        else:
            args.append(w)
        j += 1
    return {'sub': sub, 'args': args, 'dashdash': dashdash, 'flags': flags, 'raw': raw,
            'rest': words[i + 1:], 'dir': git_dir, 'options': options, 'alias': alias}


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


def op(kind, d, branch=None, **more):
    o = {'kind': kind, 'dir': d, 'branch': branch}
    o.update(more)
    return o


def head_change(git):
    """What a checkout or switch does to branches, as (ops, head): ops for a branch it resets
    (checkout -B, switch -C), and head the HEAD it leaves, as ('branch', name) for a branch it
    creates, ('detach', None), ('name', name) for a name to resolve, or None when it moves no
    HEAD (a path checkout, a patch, or no target)."""
    sub = git['sub']
    create_flags = CREATE_FLAGS[sub]
    created = None
    detach = False
    dashdash = False
    positional = []
    rest = git['rest']
    i = 0
    while i < len(rest):
        w = rest[i]
        name, eq, value = w.partition('=')
        if dashdash:
            positional.append(w)
        elif w == '--':
            dashdash = True
        elif name in create_flags and name.startswith('--') and eq:
            created = (value, create_flags[name], name)
        elif w in create_flags:
            created = (lib.word(rest, i + 1) or '', create_flags[w], w)
            i += 1
        elif w == '--detach' or (sub == 'switch' and w == '-d'):
            detach = True
        elif w in ('-p', '--patch') or name == '--pathspec-from-file':
            return [], None
        elif w == '-' or not w.startswith('-'):
            positional.append(w)
        i += 1
    if created and created[0]:
        new, forced, flag = created
        ops = [op('%s %s' % (sub, flag), git['dir'], new)] if forced else []
        return ops, ('branch', new)
    if detach:
        return [], ('detach', None)
    if sub == 'checkout' and (dashdash or len(positional) != 1):
        return [], None
    return [], ('name', positional[0]) if positional else None


def classify(git):
    """What a git invocation would do to branches: a list of {kind, dir, branch} (a None branch
    means HEAD in dir), empty when it changes no branch the guard cares about. An op carrying
    `unresolvable` is one the guard cannot judge; one carrying `rev` is a reset to that
    revision, which changes the branch only when the revision is another commit."""
    def has(f):
        return f in git['flags']
    sub = git['sub']
    d = git['dir']
    args = git['args']
    if git['alias']:
        return [op('-c alias', d, unresolvable='defines an alias with -c alias.<name>=..., which '
                   'the guard cannot resolve')]
    if sub == 'push':
        return [op('push', d)]
    if sub == 'merge':
        if has('--abort') or has('--quit'):
            return []
        return [op('fast-forward' if has('--ff-only') else 'merge', d)]
    if sub == 'pull':
        # A pull merges, fast-forwards or rebases onto HEAD; it is never the plain fast-forward
        # a build or grill marker allows, which is `git merge --ff-only`.
        kind = 'pull'
        if pull_rebases(git):
            kind = 'pull --rebase'
        elif has('--ff-only'):
            kind = 'pull --ff-only'
        return [op(kind, d)]
    if sub == 'cherry-pick':
        if has('--abort') or has('--quit'):
            return []
        return [op('cherry-pick', d)]
    if sub == 'branch':
        forced = has('--force') or has_short(git, 'f')
        if has('--delete') or has_short(git, 'd') or has_short(git, 'D'):
            return [op('branch -d', d, a) for a in args]
        if has('--move') or has_short(git, 'm') or has_short(git, 'M'):
            # `git branch -m <new>` renames HEAD's branch; -M (or --force) may overwrite <new>.
            ops = [op('branch -m', d, args[0] if len(args) >= 2 else None)]
            if args and (forced or has_short(git, 'M')):
                ops.append(op('branch -M', d, args[-1]))
            return ops
        if has('--copy') or has_short(git, 'c') or has_short(git, 'C'):
            # A forced copy overwrites the branch it names last, as `git branch -f` would.
            return [op('branch -C', d, args[-1])] if args and (forced or has_short(git, 'C')) else []
        # `git branch -f <name> [<start>]` moves the branch it names.
        if not forced or not lib.word(args, 0):
            return []
        return [op('branch -f', d, args[0])]
    if sub == 'rebase':
        if any(has(f) for f in ('--abort', '--quit', '--edit-todo', '--show-current-patch')):
            return []
        # `git rebase <upstream> <branch>` (or `--root <branch>`) rebases the branch it names.
        named = lib.word(args, 0) if has('--root') else lib.word(args, 1)
        return [op('rebase', d, named or None)]
    if sub == 'reset':
        if has('--hard'):
            return [op('reset --hard', d)]
        if git['dashdash'] or len(args) != 1 or has('--patch') or has_short(git, 'p') \
                or has('--pathspec-from-file'):
            return []  # no revision, or a reset of paths: no branch moves
        mode = next((f for f in git['flags'] if f in ('--soft', '--mixed', '--merge', '--keep')), '')
        return [op(('reset ' + mode).strip(), d, rev=args[0])]
    if sub == 'commit':
        return [op('commit --amend', d)] if has('--amend') else []
    if sub == 'update-ref':
        if has('--stdin'):
            return [op('update-ref --stdin', d, unresolvable='reads the refs it updates from '
                       'stdin, which the guard cannot see')]
        ref = lib.word(args, 0) or ''
        if ref.startswith('refs/heads/'):
            return [op('update-ref', d, ref)]
        if ref == 'HEAD' and not has('--no-deref'):
            return [op('update-ref', d)]
        return []
    if sub in CREATE_FLAGS:
        return head_change(git)[0]
    return []


def current_branch(d, options=()):
    r = lib.run(['git'] + list(options) + ['rev-parse', '--abbrev-ref', 'HEAD'], cwd=d, timeout=5)
    if r.error is not None or r.status != 0:
        return ''
    b = r.stdout.strip()
    return '' if b == 'HEAD' else b


def rev_parse(o, *args):
    r = lib.run(['git'] + list(o.get('options', ())) + ['rev-parse'] + list(args),
                cwd=o['dir'] if os.path.isdir(o['dir']) else None, timeout=5)
    return (r.stdout or '').strip() if r.error is None and r.status == 0 else ''


def resolve_head(o, name):
    """The branch a checkout or switch of name leaves HEAD on: the local branch it names, the
    one git creates from a remote-tracking branch of that name, '' for a detached HEAD (a
    commit or tag), or None when name is none of these (a path)."""
    if name in ('HEAD', '@'):
        return None  # HEAD stays where it is
    name = '@{-1}' if name == '-' else name
    full = rev_parse(o, '--symbolic-full-name', name)
    if full.startswith('refs/heads/'):
        return full[len('refs/heads/'):]
    if rev_parse(o, '--verify', '--quiet', name + '^{commit}'):
        return ''
    r = lib.run(['git'] + list(o.get('options', ())) + ['for-each-ref', '--format=%(refname)',
                                                         'refs/remotes/*/' + name],
                cwd=o['dir'] if os.path.isdir(o['dir']) else None, timeout=5)
    if r.error is None and r.status == 0 and r.stdout.strip():
        return name
    return None


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


def target_root(o):
    """The project root a git invocation acts on, in canonical form, or '' when its
    directory and --git-dir or --work-tree options name no repository."""
    options = o.get('options') or []
    named = dict(zip(options[::2], options[1::2]))
    if '--git-dir' in named and '--work-tree' not in named:
        r = lib.run(['git', '--git-dir', named['--git-dir'], 'rev-parse', '--path-format=absolute',
                     '--git-common-dir'], cwd=o['dir'] if os.path.isdir(o['dir']) else None, timeout=5)
        common = (r.stdout or '').strip() if r.error is None and r.status == 0 else ''
        return lib.canonical(os.path.dirname(lib.canonical(common))) if common else ''
    return lib.git_toplevel(o['dir'], options)


def cd_target(words):
    """The directory a cd, pushd or Set-Location segment changes to, else None."""
    if (lib.word(words, 0) or '').lower() not in CD_COMMANDS:
        return None
    rest = words[1:]
    for i, w in enumerate(rest):
        if w.lower() in ('-path', '-literalpath', '-lp'):
            return lib.word(rest, i + 1)
        if w == '-' or not w.startswith('-'):
            return w
    return None


class Session:
    """What the guard knows while it reads one command line: the session's root, each root's
    guard and fresh markers, the skills begun earlier in the line, and the branch a checkout
    or switch earlier in the line left HEAD on, by root."""

    def __init__(self, cwd):
        self.cwd = cwd
        self._root = None
        self.guards = {}
        self.marker_cache = {}
        self.begun = {}
        self.heads = {}

    @property
    def root(self):
        if self._root is None:
            self._root = lib.project_root(self.cwd)
        return self._root

    def guard_for(self, root):
        """The guard's view of one project root: whether it is on, and its protected branches."""
        if root in self.guards:
            return self.guards[root]
        guard = None
        if lib.has_profile(root) and not lib.hook_off(root, 'Git guard'):
            integration = lib.first_token(lib.profile_field(root, 'Branches and merging', 'Integration branch'))
            parent_re = pattern_regex(lib.first_token(lib.profile_field(root, 'Branches and merging', 'Parent branch')))
            guard = {
                'is_integration': lambda b: bool(integration) and bool(b) and normalise_branch(b) == integration,
                'is_parent': lambda b: parent_re is not None and bool(b) and parent_re.fullmatch(normalise_branch(b)) is not None,
            }
        self.guards[root] = guard
        return guard

    def fresh(self, root):
        if root not in self.marker_cache:
            self.marker_cache[root] = {m['name'] for m in lib.markers(root) if not m['stale']}
        return self.marker_cache[root] | self.begun.get(root, set())

    def active(self, root):
        """The markers that count for a change in root: the session's own and the target's
        (a build session's marker lives in its worktree while it fast-forwards the parent's),
        except that a build session gains nothing from release or coordinate in another root."""
        own = self.fresh(self.root)
        if not root or root == self.root:
            return own
        target = self.fresh(root)
        if 'build' in own:
            target = target - OWNERS
        return own | target

    def begin(self, d, skill):
        self.begun.setdefault(lib.project_root(d), set()).add(skill)

    def note_head(self, git):
        if git['sub'] not in CREATE_FLAGS:
            return
        head = head_change(git)[1]
        if head is None:
            return
        o = op('checkout', git['dir'], options=git['options'])
        root = target_root(o)
        if not root:
            return
        if head[0] == 'branch':
            self.heads[root] = head[1]
        elif head[0] == 'detach':
            self.heads[root] = ''
        else:
            branch = resolve_head(o, head[1])
            if branch is not None:
                self.heads[root] = branch

    def judge(self, o):
        """The reason to refuse one op, or None."""
        root = target_root(o)
        if not root or o.get('unresolvable'):
            # The guard cannot tell which repository and branch this changes, so it fails
            # closed wherever the session itself, or the repository it names, is guarded.
            if not (self.guard_for(root) if root else None) and not self.guard_for(self.root):
                return None
            if self.active(root) & OWNERS:
                return None
            if not root:
                return ('DevFactory: this git %s targets %s, which the guard cannot resolve to a '
                        'repository, so it cannot tell whether a protected branch changes; give the '
                        'directory as an existing path (C:/..., /c/... or relative), or run it under '
                        'release or coordinate.' % (o['kind'], o['dir']))
            return ('DevFactory: this git %s %s, so it cannot tell whether a protected branch '
                    'changes; run the git command itself, or run it under release or '
                    'coordinate.' % (o['kind'], o['unresolvable']))
        guard = self.guard_for(root)
        if not guard:
            return None
        return self.decide(o, root, guard, self.active(root))

    def branch_of(self, o, root):
        if o['branch']:
            return normalise_branch(o['branch'])
        if root in self.heads:
            return self.heads[root]
        return current_branch(o['dir'], o.get('options', ()))

    def moves(self, o, root):
        """Whether a reset to o's revision moves the branch: the revision is a commit other
        than the one the branch is at. A word that is no revision is a path."""
        rev = rev_parse(o, '--verify', '--quiet', o['rev'] + '^{commit}')
        if not rev:
            return False
        head = self.heads.get(root) or 'HEAD'
        return rev != rev_parse(o, '--verify', '--quiet', head + '^{commit}')

    def decide(self, o, root, guard, active):
        if active & OWNERS:
            return None
        if o['kind'] == 'push':
            if 'build' in active:
                return ('DevFactory: a build session never pushes; a push is the release, which goes through '
                        'the release skill.')
            return ('DevFactory: a push goes through the release skill, or coordinate for a parent issue; '
                    'neither is running.')
        branch = self.branch_of(o, root)
        integration = guard['is_integration'](branch)
        parent = not integration and guard['is_parent'](branch)
        if not integration and not parent:
            return None
        if 'rev' in o and not self.moves(o, root):
            return None
        if 'build' in active and parent and o['kind'] == 'fast-forward':
            return None
        if active & FAST_FORWARD_ONTO_INTEGRATION and integration and o['kind'] == 'fast-forward':
            return None
        which = 'the integration branch' if integration else 'a parent branch'
        return ('DevFactory: this git %s changes %s, %s, which only release or '
                'coordinate may change; a build session may only fast-forward a parent branch '
                '(git merge --ff-only), and grill may only commit its spec (git commit, without '
                '--amend) or fast-forward it (git merge --ff-only) onto the integration branch, as '
                'create-card and re-evaluate-card may their receipt, check-ready its re-stamped '
                'specs and curate its profile change.' % (o['kind'], branch, which))

    def walk(self, items, d):
        """Judges each part of a command line in order; returns the first refusal, or None."""
        for item in items:
            words = item['words']
            target = cd_target(words)
            if target is not None:
                d = resolve(d, target)
                continue
            if item['inner'] is not None:
                reason = self.walk(item['inner'], d)
                if reason:
                    return reason
                continue
            skill = lib.begun_skill(words)
            if skill:
                if item['join'] not in lib.BROKEN_JOINS:
                    self.begin(d, skill)
                continue
            git = parse_git(words, d)
            if not git:
                continue
            for o in classify(git):
                o['options'] = git['options']
                reason = self.judge(o)
                if reason:
                    return reason
            self.note_head(git)
        return None


def main():
    data = lib.read_input()
    if not isinstance(data, dict) or data.get('tool_name') not in lib.SHELL_TOOLS:
        return
    tool_input = data.get('tool_input')
    command = tool_input.get('command') if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not lib.might_run(command, r'\bgit\b'):
        return
    cwd = lib.input_cwd(data)
    reason = Session(cwd).walk(lib.commands(command, lib.shell_of(data)), cwd)
    if reason:
        lib.deny(reason)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass  # silence on any error
    sys.exit(0)
