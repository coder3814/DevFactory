'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const HOOK = path.resolve(__dirname, '..', 'guard-git.js');

const PROFILE = [
  '# Project profile: Example',
  '',
  '## Branches and merging',
  '- Integration branch: `main`',
  '- Worktree layout: `.worktrees/<branch>`',
  '- Parent branch: `parent-<N>`, cut from main',
  '- Sub-issue branch: `card-<N>`',
  '',
  '## Hooks',
  '- Git guard: on',
  '',
].join('\n');

function project({ profile = PROFILE, markers = [] } = {}) {
  const cwd = fs.mkdtempSync(path.join(os.tmpdir(), 'devfactory-git-'));
  fs.mkdirSync(path.join(cwd, '.devfactory', '.active'), { recursive: true });
  fs.writeFileSync(path.join(cwd, '.devfactory', 'profile.md'), profile);
  for (const m of markers) {
    fs.writeFileSync(path.join(cwd, '.devfactory', '.active', m), new Date().toISOString());
  }
  return cwd;
}

function gitRepoOn(cwd, branch) {
  const git = (...args) => spawnSync('git', args, { cwd, encoding: 'utf8' });
  git('init', '-q', '-b', branch);
  git('-c', 'user.name=t', '-c', 'user.email=t@example.com', 'commit', '-q', '--allow-empty', '-m', 'init');
}

function run(cwd, command) {
  const input = {
    session_id: 'test',
    cwd,
    hook_event_name: 'PreToolUse',
    tool_name: 'Bash',
    tool_input: { command },
  };
  const r = spawnSync(process.execPath, [HOOK], { input: JSON.stringify(input), encoding: 'utf8' });
  assert.strictEqual(r.status, 0, r.stderr);
  return r.stdout;
}

function assertDeny(out) {
  const parsed = JSON.parse(out);
  assert.strictEqual(parsed.hookSpecificOutput.hookEventName, 'PreToolUse');
  assert.strictEqual(parsed.hookSpecificOutput.permissionDecision, 'deny');
  assert.match(parsed.hookSpecificOutput.permissionDecisionReason, /^DevFactory: /);
}

test('git push without a marker is denied', () => {
  assertDeny(run(project(), 'git push origin main'));
});

test('git push with a release marker is allowed silently', () => {
  assert.strictEqual(run(project({ markers: ['release'] }), 'git push origin main'), '');
});

test('git push with only a build marker is denied', () => {
  assertDeny(run(project({ markers: ['build'] }), 'git -C ../x push'));
});

test('git merge --ff-only parent-12 with a build marker is allowed silently', () => {
  assert.strictEqual(run(project({ markers: ['build'] }), 'git merge --ff-only parent-12'), '');
});

test('git merge main without a marker is denied', () => {
  assertDeny(run(project(), 'git merge main'));
});

test('a merge run on the integration branch without a marker is denied', () => {
  const cwd = project();
  gitRepoOn(cwd, 'main');
  assertDeny(run(cwd, 'git merge card-7'));
});

test('a merge of an unprotected branch elsewhere is allowed silently', () => {
  const cwd = project();
  gitRepoOn(cwd, 'card-7');
  assert.strictEqual(run(cwd, 'git merge feature-x'), '');
});

test('no profile means silence', () => {
  const cwd = fs.mkdtempSync(path.join(os.tmpdir(), 'devfactory-git-'));
  assert.strictEqual(run(cwd, 'git push'), '');
});
