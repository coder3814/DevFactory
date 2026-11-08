'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const HOOK = path.resolve(__dirname, '..', 'session-context.js');

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

function project({ profile = PROFILE, markers = [] } = {}) {
  const cwd = fs.mkdtempSync(path.join(os.tmpdir(), 'devfactory-session-'));
  if (profile !== null) {
    fs.mkdirSync(path.join(cwd, '.devfactory', '.active'), { recursive: true });
    fs.writeFileSync(path.join(cwd, '.devfactory', 'profile.md'), profile);
    for (const m of markers) {
      fs.writeFileSync(path.join(cwd, '.devfactory', '.active', m), new Date().toISOString());
    }
  }
  return cwd;
}

function run(cwd) {
  const input = { session_id: 'test', cwd, hook_event_name: 'SessionStart', source: 'startup' };
  const r = spawnSync(process.execPath, [HOOK], { input: JSON.stringify(input), encoding: 'utf8' });
  assert.strictEqual(r.status, 0, r.stderr);
  return r.stdout;
}

test('prints the profile, stages, skills, decision line and markers in under 25 lines', () => {
  const cwd = project();
  const lines = run(cwd).trimEnd().split('\n');
  assert.ok(lines.length < 25, `${lines.length} lines`);
  assert.strictEqual(lines[0], `DevFactory profile: ${path.join(cwd, '.devfactory', 'profile.md')}`);
  assert.ok(lines.includes('| Stage | Column |'));
  for (const stage of ['Request', 'Grilling', 'Approval', 'Development', 'Done', 'Acceptance', 'Release']) {
    assert.ok(lines.some((l) => l.startsWith(`| ${stage} |`)), stage);
  }
  assert.ok(lines.some((l) => /create-card \/ add-to-card \/ re-evaluate-card/.test(l)));
  assert.ok(lines.some((l) => /^Decision line: the requester decides/.test(l)));
  assert.match(lines[lines.length - 1], /No card skill is running/);
});

test('names an active marker', () => {
  const out = run(project({ markers: ['grill'] }));
  assert.match(out, /Active card skill markers: grill \(\d+ min\)\./);
});

test('no profile means silence', () => {
  assert.strictEqual(run(project({ profile: null })), '');
});

test('"Session context: off" means silence', () => {
  const off = PROFILE.replace('- Session context: on', '- Session context: off');
  assert.strictEqual(run(project({ profile: off })), '');
});
