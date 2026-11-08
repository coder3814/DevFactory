'use strict';

// Shared helpers for the hook tests. Holds no tests itself.

const assert = require('node:assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const HOOKS = path.resolve(__dirname, '..');

function tempDir(t, prefix = 'devfactory-hook-') {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
  if (t) t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
}

function git(cwd, ...args) {
  const r = spawnSync('git', ['-c', 'user.name=t', '-c', 'user.email=t@example.com',
    '-c', 'commit.gpgsign=false', ...args], { cwd, encoding: 'utf8' });
  if (r.status !== 0) throw new Error(`git ${args.join(' ')} failed: ${r.stderr}`);
  return r.stdout.trim();
}

// A repository on the branch with one commit.
function gitRepoOn(cwd, branch) {
  git(cwd, 'init', '-q', '-b', branch);
  git(cwd, 'commit', '-q', '--allow-empty', '-m', 'init');
}

// Writes a marker whose timestamp is ageHours old.
function writeMarker(root, name, ageHours = 0) {
  const dir = path.join(root, '.devfactory', '.active');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, name), new Date(Date.now() - ageHours * 3600000).toISOString() + '\n');
}

// A project folder with the profile and markers (names, or [name, ageHours] pairs);
// branch makes it a git repository on that branch.
function project(t, { profile, markers = [], branch } = {}) {
  const cwd = tempDir(t);
  if (branch) gitRepoOn(cwd, branch);
  if (profile !== null && profile !== undefined) {
    fs.mkdirSync(path.join(cwd, '.devfactory', '.active'), { recursive: true });
    fs.writeFileSync(path.join(cwd, '.devfactory', 'profile.md'), profile);
  }
  for (const m of markers) {
    const [name, age] = Array.isArray(m) ? m : [m, 0];
    writeMarker(cwd, name, age);
  }
  return cwd;
}

function runHook(hook, input, env = {}) {
  const r = spawnSync(process.execPath, [path.join(HOOKS, hook)], {
    input: typeof input === 'string' ? input : JSON.stringify(input),
    encoding: 'utf8',
    env: { ...process.env, ...env },
  });
  assert.strictEqual(r.status, 0, r.stderr);
  return r.stdout;
}

function bash(hook, cwd, command) {
  return runHook(hook, {
    session_id: 'test',
    cwd,
    hook_event_name: 'PreToolUse',
    tool_name: 'Bash',
    tool_input: { command },
  });
}

function assertDeny(out, pattern = /^DevFactory: /) {
  assert.notStrictEqual(out, '', 'expected a deny, got silence');
  const parsed = JSON.parse(out);
  assert.strictEqual(parsed.hookSpecificOutput.hookEventName, 'PreToolUse');
  assert.strictEqual(parsed.hookSpecificOutput.permissionDecision, 'deny');
  assert.match(parsed.hookSpecificOutput.permissionDecisionReason, pattern);
}

module.exports = { tempDir, git, gitRepoOn, writeMarker, project, runHook, bash, assertDeny };
