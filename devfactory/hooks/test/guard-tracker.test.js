'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const HOOK = path.resolve(__dirname, '..', 'guard-tracker.js');

const PROFILE = [
  '# Project profile: Example',
  '',
  '## Tracker',
  '- Binding: github-projects',
  '',
  '## Hooks',
  '- Tracker guard: on',
  '- Git guard: on',
  '',
].join('\n');

function project({ profile = PROFILE, markers = [] } = {}) {
  const cwd = fs.mkdtempSync(path.join(os.tmpdir(), 'devfactory-tracker-'));
  if (profile !== null) {
    fs.mkdirSync(path.join(cwd, '.devfactory', '.active'), { recursive: true });
    fs.writeFileSync(path.join(cwd, '.devfactory', 'profile.md'), profile);
    for (const m of markers) {
      fs.writeFileSync(path.join(cwd, '.devfactory', '.active', m), new Date().toISOString());
    }
  }
  return cwd;
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
  assert.match(parsed.hookSpecificOutput.permissionDecisionReason, /card skills/);
}

test('gh issue edit without a marker is denied', () => {
  assertDeny(run(project(), 'gh issue edit 12 --body-file body.md'));
});

test('gh issue edit with a marker is allowed silently', () => {
  assert.strictEqual(run(project({ markers: ['add-to-card'] }), 'gh issue edit 12 --add-label x'), '');
});

test('gh issue view is allowed silently', () => {
  assert.strictEqual(run(project(), 'gh issue view 12 --json title,body'), '');
});

test('no profile means silence', () => {
  assert.strictEqual(run(project({ profile: null }), 'gh issue edit 12 --title x'), '');
});

test('"Tracker guard: off" means silence', () => {
  const off = PROFILE.replace('- Tracker guard: on', '- Tracker guard: off');
  assert.strictEqual(run(project({ profile: off }), 'gh issue comment 12 --body x'), '');
});

test('gh api write on an issues path without a marker is denied', () => {
  assertDeny(run(project(), 'gh api -X PATCH repos/o/r/issues/12 -f state=closed'));
});

test('malformed input is silence', () => {
  const r = spawnSync(process.execPath, [HOOK], { input: 'not json', encoding: 'utf8' });
  assert.strictEqual(r.status, 0);
  assert.strictEqual(r.stdout, '');
});
