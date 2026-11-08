'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const path = require('path');
const { project, bash, assertDeny, git } = require('./helpers');

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

const run = (cwd, command) => bash('guard-git.js', cwd, command);
const on = (t, branch, markers = [], profile = PROFILE) => project(t, { profile, markers, branch });

test('git push without a marker is denied', (t) => {
  assertDeny(run(on(t, 'card-7'), 'git push origin card-7'), /release skill/);
});

test('git push with a release or coordinate marker is allowed silently', (t) => {
  assert.strictEqual(run(on(t, 'main', ['release']), 'git push origin main'), '');
  assert.strictEqual(run(on(t, 'main', ['coordinate']), 'git push origin main'), '');
});

test('git push under build or grill is denied', (t) => {
  assertDeny(run(on(t, 'card-7', ['build']), 'git -C . push'), /never pushes/);
  assertDeny(run(on(t, 'main', ['grill']), 'git push'));
});

test('push only counts as the command token, not as a word in another argument', (t) => {
  const cwd = on(t, 'card-7');
  assert.strictEqual(run(cwd, 'git log --grep=push && echo git push'), '');
  assert.strictEqual(run(cwd, 'git commit -m "then git push; done"'), '');
  assertDeny(run(cwd, 'git status && git push'));
  assertDeny(run(cwd, 'FOO=1 git -c core.x=y push'));
});

test('merging or rebasing a protected branch into a feature branch is allowed', (t) => {
  const cwd = on(t, 'card-7');
  assert.strictEqual(run(cwd, 'git merge main'), '');
  assert.strictEqual(run(cwd, 'git rebase main'), '');
  assert.strictEqual(run(cwd, 'git rebase --onto parent-12 main'), '');
  assert.strictEqual(run(cwd, 'git reset --hard origin/main'), '');
});

test('merge, rebase, reset --hard and commit --amend on the integration branch are denied', (t) => {
  const cwd = on(t, 'main');
  for (const c of ['git merge card-7', 'git merge --ff-only card-7', 'git rebase card-7',
    'git reset --hard HEAD~1', 'git commit --amend --no-edit']) {
    assertDeny(run(cwd, c), /integration branch/);
  }
  assert.strictEqual(run(cwd, 'git commit -m "a commit"'), '');
  assert.strictEqual(run(cwd, 'git reset --soft HEAD'), '');
  assert.strictEqual(run(cwd, 'git merge --abort'), '');
});

test('a rebase that names a protected branch to rebase is denied', (t) => {
  assertDeny(run(on(t, 'card-7'), 'git rebase card-7 main'));
});

test('the effective directory is followed through git -C and cd', (t) => {
  const session = on(t, 'card-7');
  const target = on(t, 'parent-12');
  assertDeny(run(session, `git -C "${target}" merge card-7`), /parent branch/);
  assertDeny(run(session, `cd "${target}" && git merge card-7`), /parent branch/);
  assert.strictEqual(run(target, `git -C "${session}" merge parent-12`), '');
});

test('build may fast-forward a parent branch, also from its own worktree, but nothing else', (t) => {
  const session = on(t, 'card-7', ['build']);
  const parent = on(t, 'parent-12');
  assert.strictEqual(run(session, `git -C "${parent}" merge --ff-only card-7`), '');
  assert.strictEqual(run(on(t, 'parent-12', ['build']), 'git merge --ff-only card-7'), '');
  assertDeny(run(session, `git -C "${parent}" merge card-7`));
  assertDeny(run(on(t, 'main', ['build']), 'git merge --ff-only card-7'));
  assertDeny(run(on(t, 'parent-12', ['build']), 'git reset --hard HEAD'));
});

test('grill may commit, merge or fast-forward onto the integration branch, nothing else', (t) => {
  const cwd = on(t, 'main', ['grill']);
  assert.strictEqual(run(cwd, 'git merge --ff-only spec-12'), '');
  assert.strictEqual(run(cwd, 'git merge spec-12'), '');
  assert.strictEqual(run(cwd, 'git commit --amend --no-edit'), '');
  assertDeny(run(cwd, 'git reset --hard HEAD~1'));
  assertDeny(run(cwd, 'git rebase card-7'));
  assertDeny(run(on(t, 'parent-12', ['grill']), 'git merge --ff-only spec-12'));
});

test('release or coordinate allows changing a protected branch', (t) => {
  assert.strictEqual(run(on(t, 'main', ['coordinate']), 'git reset --hard HEAD'), '');
  assert.strictEqual(run(on(t, 'main', ['release']), 'git merge --ff-only card-7'), '');
});

test('a marker older than the marker lifetime is ignored', (t) => {
  assertDeny(run(on(t, 'main', [['release', 13]]), 'git push'));
  const longer = PROFILE.replace('- Git guard: on', '- Git guard: on\n- Marker lifetime: 48h');
  assert.strictEqual(run(on(t, 'main', [['release', 13]], longer), 'git push'), '');
});

test('the profile is read at the repository root when cwd is a subfolder', (t) => {
  const cwd = on(t, 'main');
  const sub = path.join(cwd, 'src', 'deep');
  fs.mkdirSync(sub, { recursive: true });
  assertDeny(run(sub, 'git merge card-7'));
});

test('the bold profile field forms are read', (t) => {
  const bold = PROFILE.replace('- Integration branch: `main`', '- **Integration branch:** `trunk`')
    .replace('- Parent branch: `parent-<N>`, cut from main', '* **Parent branch**: `epic-<N>`');
  assertDeny(run(on(t, 'trunk', [], bold), 'git merge card-7'), /trunk/);
  assertDeny(run(on(t, 'epic-4', [], bold), 'git merge card-7'), /epic-4/);
  assert.strictEqual(run(on(t, 'main', [], bold), 'git merge card-7'), '');
});

test('no profile, or "Git guard: off", means silence', (t) => {
  assert.strictEqual(run(project(t, { branch: 'main' }), 'git push'), '');
  const off = PROFILE.replace('- Git guard: on', '- Git guard: off');
  assert.strictEqual(run(on(t, 'main', [], off), 'git push'), '');
});

test('a worktree root is its own project root', (t) => {
  const main = on(t, 'main');
  fs.writeFileSync(path.join(main, '.gitignore'), '.devfactory/.active/\n');
  git(main, 'add', '.');
  git(main, 'commit', '-q', '-m', 'profile');
  const wt = path.join(main, '.worktrees', 'parent-12');
  git(main, 'worktree', 'add', '-q', '-b', 'parent-12', wt);
  assertDeny(run(wt, 'git merge card-7'), /parent-12/);
  fs.mkdirSync(path.join(wt, '.devfactory', '.active'), { recursive: true });
  fs.writeFileSync(path.join(wt, '.devfactory', '.active', 'build'), new Date().toISOString());
  assert.strictEqual(run(wt, 'git merge --ff-only card-7'), '');
  assertDeny(run(main, 'git merge --ff-only card-7'));
});
