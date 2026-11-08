'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const path = require('path');
const { project, runHook } = require('./helpers');

const PROFILE = [
  '# Project profile: Example',
  '',
  '## Stages',
  '- Column field: Status',
  '| Stage | Column |',
  '|---|---|',
  '| Request | Backlog |',
  '| Grilling | Specification |',
  '| Approval | Specification |',
  '| Development | In progress |',
  '| Done | In progress |',
  '| Acceptance | Review |',
  '| Release | Done |',
  '',
  '## Hooks',
  '- Session context: on',
  '',
].join('\n');

const run = (cwd) => runHook('session-context.js', { session_id: 'test', cwd, hook_event_name: 'SessionStart', source: 'startup' });

test('prints the profile, stages, skills, decision line and markers in under 25 lines', (t) => {
  const cwd = project(t, { profile: PROFILE });
  const lines = run(cwd).trimEnd().split('\n');
  assert.ok(lines.length < 25, `${lines.length} lines`);
  assert.strictEqual(lines[0], `DevFactory profile: ${path.join(cwd, '.devfactory', 'profile.md')}`);
  assert.strictEqual(lines[1], 'Stages (column field: Status):');
  assert.ok(lines.includes('| Stage | Column |'));
  for (const stage of ['Request', 'Grilling', 'Approval', 'Development', 'Done', 'Acceptance', 'Release']) {
    assert.ok(lines.some((l) => l.startsWith(`| ${stage} |`)), stage);
  }
  assert.ok(lines.some((l) => /create-card \/ add-to-card \/ re-evaluate-card/.test(l)));
  assert.ok(lines.some((l) => /^Decision line: the requester decides/.test(l)));
  assert.match(lines[lines.length - 1], /No card skill is running/);
});

test('names an active marker and reports a stale one', (t) => {
  const out = run(project(t, { profile: PROFILE, markers: ['grill', ['build', 30]] }));
  assert.match(out, /Active card skill markers: grill \(\d+s\)\./);
  assert.match(out, /Stale markers, which the guards ignore: build \(1d\); clear them/);
});

test('reads the profile at the repository root from a subfolder', (t) => {
  const cwd = project(t, { profile: PROFILE, branch: 'main' });
  const sub = path.join(cwd, 'src');
  fs.mkdirSync(sub);
  assert.match(run(sub), /^DevFactory profile: /);
});

test('no profile means silence', (t) => {
  assert.strictEqual(run(project(t, { profile: null })), '');
});

test('"Session context: off" means silence', (t) => {
  const off = PROFILE.replace('- Session context: on', '- Session context: off');
  assert.strictEqual(run(project(t, { profile: off })), '');
});
