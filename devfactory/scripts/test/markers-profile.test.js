'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const path = require('path');
const { tempDir, run, write, git } = require('./helpers');
const { profileFieldLine } = require('../devfactory.js');

const PROFILE = [
  '# Project profile: Example',
  '',
  '## Specs',
  '- Path: `specs/`',
  '',
  '## Branches and merging',
  '* Integration branch: `main`',
  '- **Parent branch:** `parent-<N>`, cut from main',
  '- **Sub-issue branch**: `card-<N>`',
  '',
  '## Environments',
  '### Local',
  '- Can show: everything',
  '',
  '## Hooks',
  '- Git guard: on',
  '',
  '## Standing answers',
  '- **Which log format?** JSON lines: decided in review',
  '',
].join('\n');

function marker(root, name, ageHours) {
  write(path.join(root, '.devfactory', '.active', name), new Date(Date.now() - ageHours * 3600000).toISOString() + '\n');
}

test('the field parser reads the four forms and nothing else', () => {
  assert.deepStrictEqual(profileFieldLine('- Name: value'), { name: 'Name', value: 'value' });
  assert.deepStrictEqual(profileFieldLine('* Name: a: b'), { name: 'Name', value: 'a: b' });
  assert.deepStrictEqual(profileFieldLine('- **Name:** value'), { name: 'Name', value: 'value' });
  assert.deepStrictEqual(profileFieldLine('- **Name**: value'), { name: 'Name', value: 'value' });
  assert.strictEqual(profileFieldLine('- **Which log format?** JSON lines: decided'), null);
  assert.strictEqual(profileFieldLine('| Stage | Column |'), null);
});

test('profile reads a field in each form, within a section', (t) => {
  const dir = tempDir(t);
  write(path.join(dir, '.devfactory', 'profile.md'), PROFILE.replace(/\n/g, '\r\n'));
  const field = (section, name) => run(['profile', '--section', section, '--field', name], dir);
  assert.deepStrictEqual(field('Branches and merging', 'Integration branch').lines, ['`main`']);
  assert.deepStrictEqual(field('Branches and merging', 'parent branch').lines, ['`parent-<N>`, cut from main']);
  assert.deepStrictEqual(field('Branches and merging', 'Sub-issue branch').lines, ['`card-<N>`']);
  assert.deepStrictEqual(field('Environments', 'Can show').lines, ['everything']);
  assert.strictEqual(field('Specs', 'Integration branch').code, 2);
  assert.strictEqual(field('Nowhere', 'Path').code, 2);
});

test('profile --section alone prints that section only', (t) => {
  const dir = tempDir(t);
  write(path.join(dir, '.devfactory', 'profile.md'), PROFILE);
  const r = run(['profile', '--section', 'Environments'], dir);
  assert.strictEqual(r.code, 0, r.stderr);
  assert.deepStrictEqual(r.lines, ['### Local', '- Can show: everything']);
});

test('profile, begin and markers use the repository root from a subfolder', (t) => {
  const dir = tempDir(t);
  git(dir, 'init', '-q');
  write(path.join(dir, '.devfactory', 'profile.md'), PROFILE);
  const sub = path.join(dir, 'src', 'deep');
  fs.mkdirSync(sub, { recursive: true });
  assert.deepStrictEqual(run(['profile', '--section', 'Specs', '--field', 'Path'], sub).lines, ['`specs/`']);
  assert.strictEqual(run(['begin', 'build'], sub).code, 0);
  assert.ok(fs.existsSync(path.join(dir, '.devfactory', '.active', 'build')));
  assert.ok(!fs.existsSync(path.join(sub, '.devfactory')));
});

test('begin refreshes its own marker and reports a stale one', (t) => {
  const dir = tempDir(t);
  write(path.join(dir, '.devfactory', 'profile.md'), PROFILE);
  marker(dir, 'grill', 20);
  marker(dir, 'build', 1);
  let r = run(['begin', 'grill'], dir);
  assert.strictEqual(r.code, 0, r.stderr);
  assert.match(r.lines[0], /^active build since \S+ \(1h ago\)$/);
  assert.match(r.lines[1], /^refreshed grill \(was 20h old, stale\)$/);
  const stamp = Date.parse(fs.readFileSync(path.join(dir, '.devfactory', '.active', 'grill'), 'utf8').trim());
  assert.ok(Date.now() - stamp < 60000);

  marker(dir, 'coordinate', 13);
  r = run(['begin', 'build'], dir);
  assert.match(r.lines[1], /^stale coordinate since \S+ \(13h ago, older than 12h; the guards ignore it\)$/);
});

test('markers lists each with its age, honours the lifetime and clears the stale ones', (t) => {
  const dir = tempDir(t);
  write(path.join(dir, '.devfactory', 'profile.md'), PROFILE.replace('- Git guard: on', '- Git guard: on\n- Marker lifetime: 2h'));
  marker(dir, 'build', 1);
  marker(dir, 'grill', 3);
  let r = run(['markers'], dir);
  assert.strictEqual(r.code, 0, r.stderr);
  assert.match(r.lines[0], /^active build since \S+ \(1h ago\)$/);
  assert.match(r.lines[1], /^stale grill since \S+ \(3h ago, older than 2h; the guards ignore it\)$/);
  r = run(['markers', '--clear-stale'], dir);
  assert.strictEqual(r.code, 0);
  assert.match(r.lines[1], /^cleared grill \(3h old\)$/);
  assert.deepStrictEqual(fs.readdirSync(path.join(dir, '.devfactory', '.active')), ['build']);
});
