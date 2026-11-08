'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const path = require('path');
const { tempDir, run, write } = require('./helpers');

test('criteria-ids lists IDs, allows a numbering gap and fails on a duplicate', (t) => {
  const dir = tempDir(t);
  const ok = path.join(dir, 'ok.txt');
  const dup = path.join(dir, 'dup.txt');
  const card = (c) => `Add export\r\n### Summary\r\n- C9 is not a criterion here.\r\n### Acceptance criteria\r\n${c}### Suggested model and effort\r\n- C7 neither.\r\n`;
  write(ok, card('- **C1.** It exports.\r\n- **C3.** It names the file.\r\n'));
  write(dup, card('- **C1.** It exports.\r\n- **C3.** It names the file.\r\n- **C3.** It again.\r\n'));

  const a = run(['criteria-ids', '--text', ok], dir);
  assert.strictEqual(a.code, 0, a.stderr);
  assert.deepStrictEqual(a.lines, ['C1', 'C3']);

  const b = run(['criteria-ids', '--text', dup], dir);
  assert.strictEqual(b.code, 1);
  assert.deepStrictEqual(b.lines.slice(0, 2), ['C1', 'C3']);
  assert.match(b.lines[2], /^duplicate C3\b/);
});

test('gaps add appends entries, check fails on an open one, ledger copies them', (t) => {
  const dir = tempDir(t);
  const spec = path.join(dir, 'specs', '12');
  fs.mkdirSync(spec, { recursive: true });

  let r = run(['gaps', 'add', spec, '--stage', 'Development', '--question', 'Which format?', '--condition', 'Ready 3.2', '--resolved', '2'], dir);
  assert.strictEqual(r.code, 0, r.stderr);
  r = run(['gaps', 'check', spec], dir);
  assert.strictEqual(r.code, 0, r.stdout);

  r = run(['gaps', 'add', spec, '--stage', 'Acceptance', '--question', 'The file name is wrong.', '--condition', 'Done 3.1'], dir);
  assert.strictEqual(r.code, 0, r.stderr);
  const gaps = fs.readFileSync(path.join(spec, 'gaps.md'), 'utf8');
  assert.match(gaps, /^## \d{4}-\d{2}-\d{2} — Development\n\n- \*\*Question or refusal:\*\* Which format\?\n- \*\*Let through by:\*\* Ready 3\.2\n- \*\*Resolved by:\*\* 2\n\n## /);
  assert.match(gaps, /- \*\*Resolved by:\*\* open\n$/);

  r = run(['gaps', 'check', spec], dir);
  assert.strictEqual(r.code, 1);
  assert.strictEqual(r.lines.length, 1);
  assert.match(r.lines[0], /^gap-open .*Acceptance: The file name is wrong\.$/);

  const ledger = path.join(dir, '.devfactory', 'gaps.md');
  write(ledger, '## #3 (bug fix) — 2026-10-01 — Done\r\n\r\n- **Question or refusal:** Old.\r\n- **Let through by:** Done 4.2\r\n- **Resolved by:** 2\r\n');
  r = run(['gaps', 'ledger', spec, '--card', '#12', '--types', 'feature', '--ledger', ledger], dir);
  assert.strictEqual(r.code, 0, r.stderr);
  const text = fs.readFileSync(ledger, 'utf8');
  const headings = text.split(/\r?\n/).filter((l) => l.startsWith('## '));
  assert.strictEqual(headings.length, 3);
  assert.match(headings[1], /^## #12 \(feature\) — \d{4}-\d{2}-\d{2} — Development$/);
  assert.match(headings[2], /^## #12 \(feature\) — \d{4}-\d{2}-\d{2} — Acceptance$/);
  assert.match(text, /- \*\*Question or refusal:\*\* The file name is wrong\.\n- \*\*Let through by:\*\* Done 3\.1\n- \*\*Resolved by:\*\* open\n$/);
});

test('evidence-check passes with sidecars and fails on a missing one', (t) => {
  const dir = tempDir(t);
  const spec = path.join(dir, 'spec');
  const criteria = path.join(dir, 'criteria.txt');
  write(criteria, 'C1\r\nC2\r\n');
  const sidecar = 'revision: abc1234 | checkpoint: Local | produced by: npm test\r\n';
  write(path.join(spec, 'evidence', 'C1', 'test-output.txt'), 'ok\n');
  write(path.join(spec, 'evidence', 'C1', 'test-output.txt.txt'), sidecar);
  write(path.join(spec, 'evidence', 'C2', 'page.png'), 'png');
  write(path.join(spec, 'evidence', 'C2', 'page.png.txt'), sidecar);

  let r = run(['evidence-check', spec, '--criteria', criteria], dir);
  assert.strictEqual(r.code, 0, r.stdout + r.stderr);

  write(path.join(spec, 'evidence', 'C2', 'run.log'), 'log');
  r = run(['evidence-check', spec, '--criteria', criteria], dir);
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(r.lines, ['sidecar-missing evidence/C2/run.log has no run.log.txt']);
});

test('begin writes a marker and lists others with their age; end removes it', (t) => {
  const dir = tempDir(t);
  const active = path.join(dir, '.devfactory', '.active');

  let r = run(['begin', 'grill'], dir);
  assert.strictEqual(r.code, 0, r.stderr);
  assert.deepStrictEqual(r.lines, []);
  const stamp = fs.readFileSync(path.join(active, 'grill'), 'utf8').trim();
  assert.ok(!Number.isNaN(Date.parse(stamp)), stamp);

  r = run(['begin', 'build'], dir);
  assert.strictEqual(r.code, 0);
  assert.strictEqual(r.lines.length, 1);
  assert.match(r.lines[0], /^active grill since \S+ \(\d+[smhd] ago\)$/);

  r = run(['end', 'grill'], dir);
  assert.strictEqual(r.code, 0);
  assert.deepStrictEqual(fs.readdirSync(active), ['build']);
  r = run(['end', 'build'], dir);
  assert.deepStrictEqual(fs.readdirSync(active), []);
});
