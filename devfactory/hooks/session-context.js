#!/usr/bin/env node
// SessionStart: in a project with a DevFactory profile (at the repository root of cwd),
// prints the profile path, the lifecycle stages and their columns, the skills to use, the
// decision line, the active markers and any stale ones, in under 25 lines. Silent on a
// missing profile, on "Session context: off", and on any error.
'use strict';

const path = require('path');
const lib = require('./lib');

const MAX_LINES = 24;

function main() {
  let input = {};
  try {
    input = lib.readInput();
  } catch (e) {
    input = {};
  }
  const root = lib.projectRoot(lib.inputCwd(input));
  if (!lib.hasProfile(root)) return; // no profile: silence
  if (lib.hookOff(root, 'Session context')) return;

  const out = [`DevFactory profile: ${path.join(root, '.devfactory', 'profile.md')}`];

  const stages = lib.profileSection(root, 'Stages');
  if (stages) {
    const columnField = lib.profileField(root, 'Stages', 'Column field');
    out.push(columnField ? `Stages (column field: ${columnField}):` : 'Stages:');
    for (const line of stages.filter((l) => /^\s*\|/.test(l)).slice(0, 9)) out.push(line.trim());
  } else {
    out.push('Stages: the profile has no Stages section.');
  }

  out.push('Skills: use create-card / add-to-card / re-evaluate-card for cards, grill for ' +
    'specs, coordinate for a parent issue, build for one card, accept, release.');
  out.push('Decision line: the requester decides what an observer sees or can do, what ' +
    'persisted data ends up as, and scope; the developer decides internal structure, ' +
    'anything a recorded decision, the profile or existing code already answers, and ' +
    'anything the spec delegates.');

  const markers = lib.markers(root);
  const label = (m) => {
    const age = /\((\S+) ago/.exec(m.line);
    return age ? `${m.name} (${age[1]})` : m.name;
  };
  const active = markers.filter((m) => !m.stale);
  const stale = markers.filter((m) => m.stale);
  out.push(active.length
    ? `Active card skill markers: ${active.map(label).join(', ')}.`
    : 'No card skill is running (no fresh marker in .devfactory/.active/).');
  if (stale.length) {
    out.push(`Stale markers, which the guards ignore: ${stale.map(label).join(', ')}; ` +
      'clear them with the script\'s "markers --clear-stale".');
  }

  process.stdout.write(out.slice(0, MAX_LINES).join('\n') + '\n');
}

try {
  main();
} catch (e) {
  // silence on any error
}
process.exitCode = 0;
