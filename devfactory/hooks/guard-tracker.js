#!/usr/bin/env node
// PreToolUse (Bash): refuses a tracker write while no card skill is running.
// Silent (allow) on anything else, on a missing profile, on "Tracker guard: off",
// and on any error. Never throws; always exits 0.
'use strict';

const fs = require('fs');
const path = require('path');

const REASON =
  'DevFactory: card writes go through the card skills (create-card, add-to-card, ' +
  're-evaluate-card, grill); none is running.';

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

function activeMarkers(cwd) {
  try {
    return fs.readdirSync(path.join(cwd, '.devfactory', '.active'))
      .filter((name) => !name.startsWith('.'));
  } catch (e) {
    return [];
  }
}

const WRITES = [
  /\bgh\s+issue\s+(edit|comment|create)\b/,
  /\bgh\s+project\s+item-(edit|add)\b/,
  /\baz\s+boards\s+work-item\s+(update|create)\b/,
  /\baz\s+boards\s+work-item\s+relation\s+(add|remove)\b/,
];

function isTrackerWrite(command) {
  if (WRITES.some((re) => re.test(command))) return true;
  // gh api with an explicit write method on an issues path.
  return /\bgh\s+api\b/.test(command) &&
    /(?:^|\s)(?:-X|--method)(?:\s+|=)?['"]?(PATCH|POST|PUT|DELETE)\b/i.test(command) &&
    /\/issues\b/.test(command);
}

function main() {
  const input = JSON.parse(fs.readFileSync(0, 'utf8'));
  if (input.tool_name !== 'Bash') return;
  const command = input.tool_input && input.tool_input.command;
  if (typeof command !== 'string' || !isTrackerWrite(command)) return;
  const cwd = input.cwd || process.env.CLAUDE_PROJECT_DIR || process.cwd();
  let profile;
  try {
    profile = readProfile(cwd);
  } catch (e) {
    return; // no profile: silence
  }
  if (isOff(profile, 'Tracker guard')) return;
  if (activeMarkers(cwd).length > 0) return;
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny',
      permissionDecisionReason: REASON,
    },
  }));
}

try {
  main();
} catch (e) {
  // silence on any error
}
process.exitCode = 0;
