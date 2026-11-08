#!/usr/bin/env node
// SessionStart: in a project with a DevFactory profile, prints the profile path, the
// lifecycle stages and their columns, the skills to use, the decision line and any active
// marker, in under 25 lines. Silent on a missing profile, on "Session context: off", and on
// any error.
'use strict';

const fs = require('fs');
const path = require('path');

const MAX_LINES = 24;

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

function markerAges(cwd) {
  const dir = path.join(cwd, '.devfactory', '.active');
  let names;
  try {
    names = fs.readdirSync(dir).filter((name) => !name.startsWith('.'));
  } catch (e) {
    return [];
  }
  return names.map((name) => {
    let age = '';
    try {
      const stamp = Date.parse(fs.readFileSync(path.join(dir, name), 'utf8').trim());
      if (!Number.isNaN(stamp)) {
        const minutes = Math.max(0, Math.round((Date.now() - stamp) / 60000));
        age = minutes < 120 ? `${minutes} min` : `${Math.round(minutes / 60)} h`;
      }
    } catch (e) {
      // age unknown
    }
    return age ? `${name} (${age})` : name;
  });
}

function main() {
  let input = {};
  try {
    input = JSON.parse(fs.readFileSync(0, 'utf8'));
  } catch (e) {
    input = {};
  }
  const cwd = input.cwd || process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const profilePath = path.join(cwd, '.devfactory', 'profile.md');
  let profile;
  try {
    profile = readProfile(cwd);
  } catch (e) {
    return; // no profile: silence
  }
  if (isOff(profile, 'Session context')) return;

  const out = [`DevFactory profile: ${profilePath}`];

  const stages = profile.stages;
  if (stages) {
    const columnField = stages.fields['column field'];
    out.push(columnField ? `Stages (column field: ${columnField}):` : 'Stages:');
    for (const line of stages.lines.filter((l) => /^\s*\|/.test(l)).slice(0, 9)) {
      out.push(line.trim());
    }
  } else {
    out.push('Stages: the profile has no Stages section.');
  }

  out.push('Skills: use create-card / add-to-card / re-evaluate-card for cards, grill for ' +
    'specs, coordinate for a parent issue, build for one card, accept, release.');
  out.push('Decision line: the requester decides what an observer sees or can do, what ' +
    'persisted data ends up as, and scope; the developer decides internal structure, ' +
    'anything a recorded decision, the profile or existing code already answers, and ' +
    'anything the spec delegates.');

  const markers = markerAges(cwd);
  out.push(markers.length
    ? `Active card skill markers: ${markers.join(', ')}.`
    : 'No card skill is running (no marker in .devfactory/.active/).');

  process.stdout.write(out.slice(0, MAX_LINES).join('\n') + '\n');
}

try {
  main();
} catch (e) {
  // silence on any error
}
process.exitCode = 0;
