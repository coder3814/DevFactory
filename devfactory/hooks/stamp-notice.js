#!/usr/bin/env node
// UserPromptSubmit: for the first two cards the prompt names (#<n> or "card <n>") that have
// a spec, runs stamp-check and says whether the spec is still current. Never blocks. Silent
// on a missing profile, on "Stamp notice: off", on a card without a spec, on a spec with no
// Card revision yet (still drafting), and on any error. When DEVFACTORY_STAMP_TEXT is set,
// stamp-check reads the card from that file (--text) instead of the tracker, for tests.
'use strict';

const fs = require('fs');
const path = require('path');
const lib = require('./lib');

const MAX_CARDS = 2;
const CHECK_TIMEOUT_MS = 8000;

function cardNumbers(prompt) {
  const found = [];
  const re = /(?:#|\bcard\s+#?)(\d+)\b/gi;
  let m;
  while ((m = re.exec(prompt)) !== null) {
    if (!found.includes(m[1])) found.push(m[1]);
  }
  return found;
}

function repoCommit(specFile) {
  try {
    const text = fs.readFileSync(specFile, 'utf8');
    const m = /\|\s*\*\*Repo commit\*\*\s*\|\s*([^|\r\n]*?)\s*\|/.exec(text);
    return m ? m[1] : '';
  } catch (e) {
    return '';
  }
}

function notice(root, specsDir, card) {
  const dir = path.join(specsDir, card);
  const specFile = path.join(dir, 'spec.md');
  if (!fs.existsSync(specFile)) return null;
  const source = process.env.DEVFACTORY_STAMP_TEXT
    ? ['--text', process.env.DEVFACTORY_STAMP_TEXT]
    : ['--card', card];
  const run = lib.script(root, ['stamp-check', ...source, '--spec', dir], CHECK_TIMEOUT_MS);
  if (run.error) return null;
  if (run.status !== 0 && run.status !== 1) {
    const why = ((run.stderr || '').split(/\r?\n/).find((l) => l.trim()) || 'the stamp check failed')
      .replace(/^devfactory:\s*/, '');
    if (/has no Card revision hash/.test(why)) return null; // a drafting spec: nothing to say
    return `DevFactory: could not check card ${card}'s spec against its stamp (${why}); ` +
      'check it before building.';
  }
  const out = run.stdout || '';
  const commit = repoCommit(specFile);
  if (run.status === 0 && /^match\b/m.test(out)) {
    return `DevFactory: card ${card}'s spec is current (Ready at ${commit || 'its stamped commit'})`;
  }
  if (/^changed\b/m.test(out)) {
    return `DevFactory: card ${card} changed since its spec earned Ready; run grill ` +
      're-derive before building.';
  }
  if (/^not-ancestor\b/m.test(out)) {
    return `DevFactory: card ${card}'s spec was stamped at ${commit || 'a commit'}, which is ` +
      'not an ancestor of HEAD; run grill re-derive before building.';
  }
  return null;
}

function main() {
  const input = lib.readInput();
  const prompt = input.prompt;
  if (typeof prompt !== 'string') return;
  const cards = cardNumbers(prompt);
  if (cards.length === 0) return;
  const root = lib.projectRoot(lib.inputCwd(input));
  if (!lib.hasProfile(root)) return; // no profile: silence
  if (lib.hookOff(root, 'Stamp notice')) return;
  const specsDir = path.resolve(root, lib.firstToken(lib.profileField(root, 'Specs', 'Path')) || 'specs/');
  const lines = [];
  let checked = 0;
  for (const card of cards) {
    if (checked >= MAX_CARDS) break;
    if (!fs.existsSync(path.join(specsDir, card, 'spec.md'))) continue;
    checked++;
    try {
      const line = notice(root, specsDir, card);
      if (line) lines.push(line);
    } catch (e) {
      // skip this card
    }
  }
  if (lines.length === 0) return;
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'UserPromptSubmit',
      additionalContext: lines.join('\n'),
    },
  }));
}

try {
  main();
} catch (e) {
  // silence on any error
}
process.exitCode = 0;
