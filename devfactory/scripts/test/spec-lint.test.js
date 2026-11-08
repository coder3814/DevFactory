'use strict';

const test = require('node:test');
const assert = require('node:assert');
const path = require('path');
const { tempDir, run, write, specText } = require('./helpers');

function lint(t, spec, { criteria = 'C1\nC2\n', gaps } = {}) {
  const dir = tempDir(t);
  write(path.join(dir, 'spec', 'spec.md'), spec);
  if (gaps !== undefined) write(path.join(dir, 'spec', 'gaps.md'), gaps);
  const args = ['spec-lint', path.join(dir, 'spec')];
  if (criteria !== null) {
    write(path.join(dir, 'criteria.txt'), criteria);
    args.push('--criteria', path.join(dir, 'criteria.txt'));
  }
  return run(args, dir);
}

function codes(r) {
  return r.lines.map((l) => l.split(' ')[0]);
}

test('a complete spec passes, with CRLF line endings too', (t) => {
  const r = lint(t, specText().replace(/\n/g, '\r\n'), {
    gaps: '## 2026-11-07 — Development\r\n\r\n- **Question or refusal:** Which format?\r\n- **Let through by:** Ready 3.2\r\n- **Resolved by:** 2\r\n',
  });
  assert.strictEqual(r.code, 0, r.stdout + r.stderr);
  assert.deepStrictEqual(r.lines, []);
});

test('optional sections may be left out', (t) => {
  const r = lint(t, specText({ omit: ['Owner steps'] }));
  assert.strictEqual(r.code, 0, r.stdout);
});

test('a missing header row is reported', (t) => {
  const header = [
    ['Card', '#12'],
    ['Version', '1'],
    ['Status', 'Ready'],
    ['Card revision', 'a'.repeat(64)],
    ['Repo commit', 'abc1234'],
    ['Request type(s)', 'feature'],
  ];
  const r = lint(t, specText({ header }));
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(r.lines, ['header-missing Stamped']);
});

test('a status outside drafting, Ready and approved is reported', (t) => {
  const r = lint(t, specText({ status: 'done' }));
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(codes(r), ['status-invalid']);
});

test('a missing required section is reported', (t) => {
  const r = lint(t, specText({ omit: ['Boundaries'] }));
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(r.lines, ['section-missing Boundaries']);
});

test('a section out of order is reported', (t) => {
  const order = ['Decisions delegated to the developer', 'Dispositions', 'Boundaries', 'Interface surface', 'Evidence plan', 'Owner steps', 'Project bindings used', 'Amendments'];
  const r = lint(t, specText({ order }));
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(codes(r), ['section-order']);
});

test('a blank Disposition cell is reported by its concern', (t) => {
  const dispositions = '| Concern | Disposition | Demands (criterion or evidence row) |\n|---|---|---|\n| Existing data changed | Not applicable, because nothing is stored | |\n| Security |  | |';
  const r = lint(t, specText({ dispositions }));
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(r.lines, ['disposition-blank Security']);
});

test('a criterion without an evidence row is reported', (t) => {
  const r = lint(t, specText(), { criteria: 'C1\nC2\nC4\n' });
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(codes(r), ['evidence-missing']);
  assert.match(r.lines[0], /C4/);
});

test('an evidence row for an unknown criterion ID is reported', (t) => {
  const r = lint(t, specText(), { criteria: 'C1\n' });
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(codes(r), ['evidence-unknown']);
  assert.match(r.lines[0], /C2/);
});

test('an owner step without a moment is reported', (t) => {
  const owner = '| Step | Who | Moment in the run |\n|---|---|---|\n| Approve the wording | the requester | |';
  const r = lint(t, specText({ owner }));
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(r.lines, ['owner-step-no-moment Approve the wording']);
});

test('an empty amendments table is reported', (t) => {
  const amendments = '| Version | Date | What changed | Driven by |\n|---|---|---|---|';
  const r = lint(t, specText({ amendments }));
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(codes(r), ['amendments-empty']);
});

test('a gaps.md that does not parse is reported', (t) => {
  const r = lint(t, specText(), { gaps: '## 2026-11-07 — Development\n\n- **Question or refusal:** Which format?\n' });
  assert.strictEqual(r.code, 1);
  assert.ok(codes(r).every((c) => c === 'gaps-parse'), r.stdout);
});
