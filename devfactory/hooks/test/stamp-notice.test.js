'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const { project, runHook, git } = require('./helpers');

const SCRIPT = path.resolve(__dirname, '..', '..', 'scripts', 'devfactory.js');

const PROFILE = [
  '# Project profile: Example',
  '',
  '## Specs',
  '- **Path:** `docs/specs/`',
  '',
  '## Hooks',
  '- Stamp notice: on',
  '',
].join('\n');

function spec(revision, commit) {
  return [
    '# Spec: Add export',
    '',
    '| | |',
    '|---|---|',
    '| **Card** | #12 |',
    '| **Version** | 1 |',
    `| **Status** | ${revision ? 'Ready' : 'drafting'} |`,
    `| **Card revision** | ${revision} |`,
    `| **Repo commit** | ${commit} |`,
    '| **Stamped** | 2026-11-07 |',
    '| **Request type(s)** | feature |',
    '',
  ].join('\n');
}

// A repository with the profile, a card text file and its revision.
function setup(t) {
  const cwd = project(t, { profile: PROFILE, branch: 'main' });
  const head = git(cwd, 'rev-parse', 'HEAD');
  const card = path.join(cwd, 'card.txt');
  fs.writeFileSync(card, 'Add export\n- **C1.** It exports.\n');
  const revision = spawnSync(process.execPath, [SCRIPT, 'stamp', '--text', card], { encoding: 'utf8' }).stdout.trim();
  const writeSpec = (n, text) => {
    fs.mkdirSync(path.join(cwd, 'docs', 'specs', n), { recursive: true });
    fs.writeFileSync(path.join(cwd, 'docs', 'specs', n, 'spec.md'), text);
  };
  return { cwd, head, card, revision, writeSpec };
}

function notice(cwd, prompt, card) {
  const out = runHook('stamp-notice.js', { session_id: 'test', cwd, hook_event_name: 'UserPromptSubmit', prompt },
    { DEVFACTORY_STAMP_TEXT: card });
  return out ? JSON.parse(out).hookSpecificOutput.additionalContext.split('\n') : [];
}

test('a current spec is reported current, a changed card as changed', (t) => {
  const { cwd, head, card, revision, writeSpec } = setup(t);
  writeSpec('12', spec(revision, head));
  assert.deepStrictEqual(notice(cwd, 'build #12', card), [`DevFactory: card 12's spec is current (Ready at ${head})`]);
  fs.writeFileSync(card, 'Add export\n- **C1.** It exports as CSV.\n');
  assert.match(notice(cwd, 'build card 12', card)[0], /^DevFactory: card 12 changed since its spec earned Ready/);
});

test('a drafting spec with no Card revision is silence; another stamp error is reported', (t) => {
  const { cwd, card, revision, writeSpec } = setup(t);
  writeSpec('12', spec('', ''));
  assert.deepStrictEqual(notice(cwd, 'grill #12', card), []);
  writeSpec('13', spec(revision, ''));
  assert.match(notice(cwd, 'grill #13', card)[0], /^DevFactory: could not check card 13's spec .*has no Repo commit/);
});

test('at most two cards are checked, and a card without a spec is skipped', (t) => {
  const { cwd, head, card, revision, writeSpec } = setup(t);
  for (const n of ['12', '13', '14']) writeSpec(n, spec(revision, head));
  const lines = notice(cwd, 'compare #99, #12, #13 and #14', card);
  assert.deepStrictEqual(lines.map((l) => /card (\d+)/.exec(l)[1]), ['12', '13']);
});

test('"Stamp notice: off" means silence', (t) => {
  const { cwd, head, card, revision, writeSpec } = setup(t);
  writeSpec('12', spec(revision, head));
  fs.writeFileSync(path.join(cwd, '.devfactory', 'profile.md'), PROFILE.replace('- Stamp notice: on', '- Stamp notice: off'));
  assert.deepStrictEqual(notice(cwd, 'build #12', card), []);
});
