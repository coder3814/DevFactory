#!/usr/bin/env node
// UserPromptSubmit: for each card the prompt names (#<n> or "card <n>") that has a spec,
// runs stamp-check and says whether the spec is still current. Never blocks. Silent on a
// missing profile, on "Stamp notice: off", on a card without a spec, and on any error.
'use strict';

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

function readProfile(cwd) {
  const text = fs.readFileSync(path.join(cwd, '.devfactory', 'profile.md'), 'utf8');
  const sections = {};
  let current = null;
  for (const line of text.split(/\r?\n/)) {
    const heading = /^##\s+(.+?)\s*$/.exec(line);
    if (heading) {
      current = { fields: {}, lines: [] };
      sections[heading[1].trim().toLowerCase()] = current;
      continue;
    }
    if (!current) continue;
    current.lines.push(line);
    const field = /^\s*-\s+([^:]+?):\s*(.*)$/.exec(line);
    if (field) current.fields[field[1].trim().toLowerCase()] = field[2].trim();
  }
  return sections;
}

function isOff(profile, name) {
  const hooks = profile.hooks;
  const value = hooks && hooks.fields[name.toLowerCase()];
  return typeof value === 'string' && /^`?off\b/i.test(value);
}

function specsPath(profile) {
  const value = profile.specs && profile.specs.fields.path;
  if (!value) return 'specs/';
  const ticked = /`([^`]+)`/.exec(value);
  return (ticked ? ticked[1] : value.split(/\s+/)[0]) || 'specs/';
}

function cardNumbers(prompt) {
  const found = [];
  const re = /(?:#|\bcard\s+#?)(\d+)\b/gi;
  let m;
  while ((m = re.exec(prompt)) !== null) {
    if (!found.includes(m[1])) found.push(m[1]);
  }
  return found.slice(0, 5);
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

function notice(cwd, script, specsDir, card) {
  const dir = path.join(specsDir, card);
  const specFile = path.join(dir, 'spec.md');
  if (!fs.existsSync(specFile)) return null;
  const run = spawnSync(process.execPath,
    [script, 'stamp-check', '--card', card, '--spec', dir], {
      cwd,
      encoding: 'utf8',
      timeout: 20000,
      windowsHide: true,
    });
  if (run.error) return null;
  if (run.status !== 0 && run.status !== 1) {
    const why = ((run.stderr || '').split(/\r?\n/).find((l) => l.trim()) || 'the stamp check failed')
      .replace(/^devfactory:\s*/, '');
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
  const input = JSON.parse(fs.readFileSync(0, 'utf8'));
  const prompt = input.prompt;
  if (typeof prompt !== 'string') return;
  const cards = cardNumbers(prompt);
  if (cards.length === 0) return;
  const cwd = input.cwd || process.env.CLAUDE_PROJECT_DIR || process.cwd();
  let profile;
  try {
    profile = readProfile(cwd);
  } catch (e) {
    return; // no profile: silence
  }
  if (isOff(profile, 'Stamp notice')) return;
  const root = process.env.CLAUDE_PLUGIN_ROOT || path.resolve(__dirname, '..');
  const script = path.join(root, 'scripts', 'devfactory.js');
  if (!fs.existsSync(script)) return;
  const specsDir = path.resolve(cwd, specsPath(profile));
  const lines = [];
  for (const card of cards) {
    try {
      const line = notice(cwd, script, specsDir, card);
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
