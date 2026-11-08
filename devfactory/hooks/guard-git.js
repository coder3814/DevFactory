#!/usr/bin/env node
// PreToolUse (Bash): keeps the integration branch and parent branches from being changed
// outside the skills that own them, and refuses every push outside release and coordinate.
//
// Refused: `git push`; and `git merge`, `git rebase`, `git reset --hard` and
// `git commit --amend` when the branch they change (HEAD in the effective directory, `cwd`
// after any `cd <dir>` and `git -C <dir>`, or the branch a rebase names) is protected.
// Merging or rebasing a protected branch into an unprotected one is never refused.
// Allowed: everything while a `release` or `coordinate` marker is fresh; under `build`, a
// `git merge --ff-only` onto a parent branch; under `grill`, a commit, merge or
// fast-forward onto the integration branch. Markers older than the profile's marker
// lifetime are ignored. Silent (allow) on a missing profile, on "Git guard: off", and on
// any error. Never throws; always exits 0.
'use strict';

const path = require('path');
const { execFileSync } = require('child_process');
const lib = require('./lib');

const GLOBAL_WITH_VALUE = new Set(['-C', '-c', '--git-dir', '--work-tree', '--namespace',
  '--exec-path', '--config-env']);
const VALUE_OPTIONS = {
  merge: new Set(['-m', '-s', '-X', '-F', '--strategy', '--strategy-option', '--file',
    '--message', '--into-name', '--cleanup']),
  rebase: new Set(['-s', '-X', '-x', '--exec', '--strategy', '--strategy-option', '--onto']),
  reset: new Set([]),
  commit: new Set(['-m', '-F', '-C', '-c', '-t', '--message', '--file', '--reuse-message',
    '--reedit-message', '--template', '--author', '--date', '--fixup', '--squash',
    '--cleanup', '--trailer']),
};

// Parses one segment's command words into { sub, args, flags, dir } when it runs git.
function parseGit(words, dir) {
  if (!lib.isProgram(words[0], 'git')) return null;
  let i = 1;
  let gitDir = dir;
  while (i < words.length && words[i].startsWith('-')) {
    const opt = words[i];
    if (opt === '-C' && i + 1 < words.length) {
      gitDir = path.resolve(gitDir, words[i + 1]);
      i += 2;
    } else if (GLOBAL_WITH_VALUE.has(opt)) {
      i += 2;
    } else {
      i += 1;
    }
  }
  const sub = words[i];
  if (!sub) return null;
  const takesValue = VALUE_OPTIONS[sub] || new Set();
  const args = [];
  const flags = [];
  for (let j = i + 1; j < words.length; j++) {
    const w = words[j];
    if (w === '--') continue;
    if (w.startsWith('-')) {
      flags.push(w.split('=')[0]);
      if (takesValue.has(w)) j++;
    } else {
      args.push(w);
    }
  }
  return { sub, args, flags, dir: gitDir };
}

// What a git invocation would do to a branch: { kind, dir, branch|null } or null when it
// changes no branch the guard cares about. A null branch means HEAD in dir.
function classify(git) {
  const has = (f) => git.flags.includes(f);
  switch (git.sub) {
    case 'push':
      return { kind: 'push', dir: git.dir, branch: null };
    case 'merge':
      if (has('--abort') || has('--quit')) return null;
      return { kind: has('--ff-only') ? 'fast-forward' : 'merge', dir: git.dir, branch: null };
    case 'rebase': {
      if (['--abort', '--quit', '--edit-todo', '--show-current-patch'].some(has)) return null;
      // `git rebase <upstream> <branch>` (or `--root <branch>`) rebases the branch it names.
      const named = has('--root') ? git.args[0] : git.args[1];
      return { kind: 'rebase', dir: git.dir, branch: named || null };
    }
    case 'reset':
      return has('--hard') ? { kind: 'reset --hard', dir: git.dir, branch: null } : null;
    case 'commit':
      return has('--amend') ? { kind: 'commit --amend', dir: git.dir, branch: null } : null;
    default:
      return null;
  }
}

function currentBranch(dir) {
  try {
    const b = execFileSync('git', ['rev-parse', '--abbrev-ref', 'HEAD'], {
      cwd: dir,
      encoding: 'utf8',
      timeout: 5000,
      stdio: ['ignore', 'pipe', 'ignore'],
      windowsHide: true,
    }).trim();
    return b === 'HEAD' ? '' : b;
  } catch (e) {
    return '';
  }
}

// A parent-branch pattern such as parent-<N>: <N> is digits, any other <placeholder> is a
// run of branch-name characters, everything else is literal.
function patternRegex(pattern) {
  if (!pattern) return null;
  let source = '';
  for (const part of pattern.split(/(<[^>]+>)/)) {
    if (!part) continue;
    if (/^<n>$/i.test(part)) source += '\\d+';
    else if (/^<[^>]+>$/.test(part)) source += '[A-Za-z0-9._/-]+';
    else source += part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  return new RegExp('^' + source + '$');
}

function normaliseBranch(name) {
  return String(name)
    .replace(/^refs\/heads\//, '')
    .replace(/^refs\/remotes\//, '')
    .replace(/^origin\//, '');
}

// The guard's view of one project root: whether it is on, and its protected branches.
function guardFor(root, cache) {
  if (cache.has(root)) return cache.get(root);
  let guard = null;
  if (lib.hasProfile(root) && !lib.hookOff(root, 'Git guard')) {
    const integration = lib.firstToken(lib.profileField(root, 'Branches and merging', 'Integration branch'));
    const parentRe = patternRegex(lib.firstToken(lib.profileField(root, 'Branches and merging', 'Parent branch')));
    guard = {
      integration,
      isIntegration: (b) => !!integration && !!b && normaliseBranch(b) === integration,
      isParent: (b) => !!parentRe && !!b && parentRe.test(normaliseBranch(b)),
    };
  }
  cache.set(root, guard);
  return guard;
}

function freshMarkers(roots, cache) {
  const names = new Set();
  for (const root of roots) {
    if (!cache.has(root)) cache.set(root, lib.markers(root).filter((m) => !m.stale).map((m) => m.name));
    for (const n of cache.get(root)) names.add(n);
  }
  return names;
}

function decide(op, guard, active) {
  if (active.has('release') || active.has('coordinate')) return null;
  if (op.kind === 'push') {
    return active.has('build')
      ? 'DevFactory: a build session never pushes; a push is the release, which goes through ' +
        'the release skill.'
      : 'DevFactory: a push goes through the release skill, or coordinate for a parent issue; ' +
        'neither is running.';
  }
  const branch = op.branch ? normaliseBranch(op.branch) : currentBranch(op.dir);
  const integration = guard.isIntegration(branch);
  const parent = !integration && guard.isParent(branch);
  if (!integration && !parent) return null;
  if (active.has('build') && parent && op.kind === 'fast-forward') return null;
  if (active.has('grill') && integration &&
    ['merge', 'fast-forward', 'commit --amend'].includes(op.kind)) return null;
  const which = integration ? 'the integration branch' : 'a parent branch';
  return `DevFactory: this git ${op.kind} changes ${branch}, ${which}, which only release or ` +
    'coordinate may change; a build session may only fast-forward a parent branch ' +
    '(git merge --ff-only), and grill may only commit or merge its spec onto the ' +
    'integration branch.';
}

function main() {
  const input = lib.readInput();
  if (input.tool_name !== 'Bash') return;
  const command = input.tool_input && input.tool_input.command;
  if (typeof command !== 'string' || !/\bgit\b/.test(command)) return;
  const cwd = lib.inputCwd(input);

  const ops = [];
  let dir = cwd;
  for (const segment of lib.segments(command)) {
    const words = lib.commandWords(segment);
    if ((words[0] === 'cd' || words[0] === 'pushd') && words[1]) {
      dir = path.resolve(dir, words[1]);
      continue;
    }
    const git = parseGit(words, dir);
    const op = git && classify(git);
    if (op) ops.push(op);
  }
  if (ops.length === 0) return;

  const sessionRoot = lib.projectRoot(cwd);
  const guards = new Map();
  const markerCache = new Map();
  for (const op of ops) {
    const root = lib.projectRoot(op.dir);
    const guard = guardFor(root, guards);
    if (!guard) continue;
    // A marker counts in the target's root or the session's own (a build session's marker
    // lives in its worktree while it fast-forwards the parent's).
    const reason = decide(op, guard, freshMarkers([root, sessionRoot], markerCache));
    if (reason) {
      lib.deny(reason);
      return;
    }
  }
}

try {
  main();
} catch (e) {
  // silence on any error
}
process.exitCode = 0;
