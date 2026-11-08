#!/usr/bin/env node
// PreToolUse (Bash): refuses a tracker write while no card skill is running. A write is a
// gh issue edit, comment or create, a gh project item-edit or item-add, an az boards
// work-item update, create or relation change, a gh api graphql call carrying a mutation
// (or an --input whose content cannot be seen), and any other gh api call whose method is
// not GET: an -X or --method other than GET, or a field (-f, -F, --raw-field, --field) or
// --input with no method, which gh sends as POST. Plain reads pass. Markers older than the
// profile's marker lifetime do not count. Silent (allow) on anything else, on a missing
// profile, on "Tracker guard: off", and on any error. Never throws; always exits 0.
'use strict';

const lib = require('./lib');

const REASON =
  'DevFactory: card writes go through the card skills (create-card, add-to-card, ' +
  're-evaluate-card, grill); none is running.';

const FIELD_FLAGS = ['-f', '-F', '--field', '--raw-field', '--input'];

function flagValue(words, i) {
  const w = words[i];
  const eq = w.indexOf('=');
  if (w.startsWith('--')) return eq > 0 ? w.slice(eq + 1) : words[i + 1];
  // -XPATCH or -X PATCH
  return w.length > 2 ? w.slice(2).replace(/^=/, '') : words[i + 1];
}

function isGhApiWrite(args) {
  if (args[0] === 'graphql' || args.includes('graphql')) {
    return args.some((a) => /\bmutation\b/.test(a)) ||
      args.some((a) => a === '--input' || a.startsWith('--input='));
  }
  let method = null;
  let fields = false;
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === '-X' || a.startsWith('-X') || a === '--method' || a.startsWith('--method=')) {
      method = (flagValue(args, i) || '').toUpperCase();
    } else if (FIELD_FLAGS.some((f) => a === f || a.startsWith(f + '=') ||
      (f.length === 2 && a.startsWith(f) && a.length > 2))) {
      fields = true;
    }
  }
  if (method === null) return fields;
  return method !== 'GET';
}

function isTrackerWrite(words) {
  const [prog, a, b, c, d] = words;
  if (lib.isProgram(prog, 'gh')) {
    if (a === 'issue' && ['edit', 'comment', 'create'].includes(b)) return true;
    if (a === 'project' && ['item-edit', 'item-add'].includes(b)) return true;
    if (a === 'api') return isGhApiWrite(words.slice(2));
    return false;
  }
  if (lib.isProgram(prog, 'az') && a === 'boards' && b === 'work-item') {
    if (['update', 'create'].includes(c)) return true;
    if (c === 'relation' && ['add', 'remove'].includes(d)) return true;
  }
  return false;
}

function main() {
  const input = lib.readInput();
  if (input.tool_name !== 'Bash') return;
  const command = input.tool_input && input.tool_input.command;
  if (typeof command !== 'string' || !/\b(gh|az)\b/.test(command)) return;
  if (!lib.segments(command).some((s) => isTrackerWrite(lib.commandWords(s)))) return;
  const root = lib.projectRoot(lib.inputCwd(input));
  if (!lib.hasProfile(root)) return; // no profile: silence
  if (lib.hookOff(root, 'Tracker guard')) return;
  if (lib.markers(root).some((m) => !m.stale)) return;
  lib.deny(REASON);
}

try {
  main();
} catch (e) {
  // silence on any error
}
process.exitCode = 0;
