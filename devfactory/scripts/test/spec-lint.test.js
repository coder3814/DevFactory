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

const DISPOSITIONS_HEAD = '| Concern | Disposition | Demands (criterion or evidence row) |\n|---|---|---|\n';

test('a blank Disposition cell, or one holding only the italic prompt, is reported by its concern', (t) => {
  const dispositions = DISPOSITIONS_HEAD +
    '| Existing data changed | Not applicable, because nothing is stored | |\n| Security |  | |\n' +
    '| Performance | *say what load it adds* | |\n| Release sequencing | *does the change need anything before or after the deploy* | |\n' +
    '| Owner steps | None, because *nothing* is asked | |';
  const r = lint(t, specText({ dispositions }));
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(r.lines, ['disposition-blank Security', 'disposition-blank Performance', 'disposition-blank Release sequencing']);
});

test('a core concern with no Dispositions row is reported', (t) => {
  const dispositions = DISPOSITIONS_HEAD +
    '| Existing data changed | Not applicable, because nothing is stored | |\n| Performance | Not applicable, because the list is small | |\n' +
    '| Release sequencing | Nothing before or after the deploy | |\n| Owner steps | None | |\n| Accessibility | Not applicable | |';
  const r = lint(t, specText({ dispositions }));
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(r.lines, ['disposition-missing Security has no row']);
});

function blankStamp(status, version = '1') {
  return [
    ['Card', '#12'],
    ['Version', version],
    ['Status', status],
    ['Card revision', ''],
    ['Repo commit', ''],
    ['Stamped', ''],
    ['Request type(s)', 'feature'],
  ];
}

test('a drafting spec with blank Card revision, Repo commit and Stamped passes', (t) => {
  const r = lint(t, specText({ header: blankStamp('drafting') }));
  assert.strictEqual(r.code, 0, r.stdout);
  assert.deepStrictEqual(r.lines, []);
});

test('an empty header value is reported; a drafting spec is excused only the stamp rows', (t) => {
  const drafting = lint(t, specText({ header: blankStamp('drafting', '') }));
  assert.strictEqual(drafting.code, 1);
  assert.deepStrictEqual(drafting.lines, ['header-empty Version']);
  for (const status of ['Ready', 'approved']) {
    const r = lint(t, specText({ header: blankStamp(status) }));
    assert.strictEqual(r.code, 1);
    assert.deepStrictEqual(r.lines, ['header-empty Card revision', 'header-empty Repo commit', 'header-empty Stamped']);
  }
});

function header({ status = 'Ready', revision = 'a'.repeat(64), commit = 'abc1234', stamped = '2026-11-07', types = 'feature' } = {}) {
  return [
    ['Card', '#12'],
    ['Version', '1'],
    ['Status', status],
    ['Card revision', revision],
    ['Repo commit', commit],
    ['Stamped', stamped],
    ['Request type(s)', types],
  ];
}

test('request types are each one of the five', (t) => {
  assert.strictEqual(lint(t, specText({ header: header({ types: 'bug fix, data correction' }) })).code, 0);
  assert.strictEqual(lint(t, specText({ header: header({ types: 'Refactor / other' }) })).code, 0);
  const r = lint(t, specText({ header: header({ types: 'feature, chore' }) }));
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(codes(r), ['request-type-invalid']);
  assert.match(r.lines[0], /"chore"/);
});

test('a Ready or approved spec needs a full card revision, a hex repo commit and a stamp date', (t) => {
  for (const status of ['Ready', 'approved']) {
    const r = lint(t, specText({ header: header({ status, revision: 'A'.repeat(64), commit: 'abc12', stamped: 'today' }) }));
    assert.strictEqual(r.code, 1);
    assert.deepStrictEqual(codes(r), ['card-revision-invalid', 'repo-commit-invalid', 'stamped-invalid']);
  }
  const long = lint(t, specText({ header: header({ commit: 'f'.repeat(40) }) }));
  assert.strictEqual(long.code, 0, long.stdout);
  const tooLong = lint(t, specText({ header: header({ commit: 'f'.repeat(41) }) }));
  assert.deepStrictEqual(codes(tooLong), ['repo-commit-invalid']);
  const drafting = lint(t, specText({ header: header({ status: 'drafting', revision: 'pending', commit: 'pending' }) }));
  assert.strictEqual(drafting.code, 0, drafting.stdout);
});

test('an evidence plan missing one of the six columns is reported', (t) => {
  const evidence = '| Criterion | Shown by | What it will show | Generated by | Checkpoint |\n|---|---|---|---|---|\n| C1 | test | the list | npm test | Local |\n| C2 | log | the count | npm run job | Local |';
  const r = lint(t, specText({ evidence }));
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(r.lines, ['evidence-column-missing Under what condition']);
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
