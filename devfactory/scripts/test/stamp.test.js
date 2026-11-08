'use strict';

const test = require('node:test');
const assert = require('node:assert');
const crypto = require('crypto');
const path = require('path');
const { tempDir, run, write, git, specText } = require('./helpers');
const { cardText } = require('../devfactory.js');

const sha = (s) => crypto.createHash('sha256').update(s, 'utf8').digest('hex');

test('stamp --text normalises CRLF, drops spec lines and trailing line feeds', (t) => {
  const dir = tempDir(t);
  const crlf = path.join(dir, 'crlf.txt');
  const lf = path.join(dir, 'lf.txt');
  write(crlf, 'Add export\r\n## Summary\r\nExports the list.\r\nSpec: specs/12/ @ 0a1b2c3\r\n- **C1.** It exports.\r\r\n\r\n');
  write(lf, 'Add export\n## Summary\nExports the list.\n- **C1.** It exports.\n');

  const expected = sha('Add export\n## Summary\nExports the list.\n- **C1.** It exports.');
  const a = run(['stamp', '--text', crlf], dir);
  const b = run(['stamp', '--text', lf], dir);
  assert.strictEqual(a.code, 0, a.stderr);
  assert.deepStrictEqual(a.lines, [expected]);
  assert.deepStrictEqual(b.lines, [expected]);
});

test('a line that only mentions a spec is kept', () => {
  assert.strictEqual(cardText('T', 'See Spec: specs/1/ @ abc\nSpec: specs/1/ @ ABC'), 'T\nSee Spec: specs/1/ @ abc\nSpec: specs/1/ @ ABC');
});

function stampedRepo(t, cardBody) {
  const dir = tempDir(t);
  git(dir, 'init', '-q');
  write(path.join(dir, 'README.md'), 'x\n');
  git(dir, 'add', '.');
  git(dir, 'commit', '-q', '-m', 'base');
  const head = git(dir, 'rev-parse', 'HEAD');
  const card = path.join(dir, 'card.txt');
  write(card, `Add export\n${cardBody}`);
  const revision = run(['stamp', '--text', card], dir).lines[0];
  return { dir, head, card, revision };
}

test('stamp-check reports match and ancestor when nothing changed', (t) => {
  const { dir, head, card, revision } = stampedRepo(t, '- **C1.** It exports.\n');
  write(path.join(dir, 'specs', '12', 'spec.md'), specText({ revision, commit: head }));
  const r = run(['stamp-check', '--text', card, '--spec', path.join(dir, 'specs', '12')], dir);
  assert.strictEqual(r.code, 0, r.stdout + r.stderr);
  assert.deepStrictEqual(r.lines, ['match', 'ancestor']);
});

test('stamp-check reports changed with both revisions when the card text changed', (t) => {
  const { dir, head, card, revision } = stampedRepo(t, '- **C1.** It exports.\n');
  write(path.join(dir, 'specs', '12', 'spec.md'), specText({ revision, commit: head }));
  write(card, 'Add export\n- **C1.** It exports as CSV.\n');
  const now = run(['stamp', '--text', card], dir).lines[0];
  const r = run(['stamp-check', '--text', card, '--spec', path.join(dir, 'specs', '12')], dir);
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(r.lines, [`changed ${revision} ${now}`, 'ancestor']);
});

test('stamp-check reports not-ancestor when the stamped commit is off the branch', (t) => {
  const { dir, card, revision } = stampedRepo(t, '- **C1.** It exports.\n');
  const orphan = git(dir, 'commit-tree', 'HEAD^{tree}', '-m', 'elsewhere');
  write(path.join(dir, 'specs', '12', 'spec.md'), specText({ revision, commit: orphan }));
  const r = run(['stamp-check', '--text', card, '--spec', path.join(dir, 'specs', '12')], dir);
  assert.strictEqual(r.code, 1);
  assert.deepStrictEqual(r.lines, ['match', 'not-ancestor']);
});
