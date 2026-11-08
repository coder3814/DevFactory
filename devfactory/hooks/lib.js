// Shared by the DevFactory hooks; holds no hook itself. The profile and the markers are read
// through the plugin's script (`profile`, `markers`), so the hooks parse neither themselves.
'use strict';

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const SCRIPT = path.resolve(__dirname, '..', 'scripts', 'devfactory.js');

function readInput() {
  return JSON.parse(fs.readFileSync(0, 'utf8'));
}

function inputCwd(input) {
  return path.resolve((input && input.cwd) || process.env.CLAUDE_PROJECT_DIR || process.cwd());
}

// The repository root of a directory (a worktree's own root), else the directory itself.
function projectRoot(dir) {
  const r = spawnSync('git', ['rev-parse', '--show-toplevel'], {
    cwd: dir,
    encoding: 'utf8',
    timeout: 5000,
    stdio: ['ignore', 'pipe', 'ignore'],
    windowsHide: true,
  });
  const top = !r.error && r.status === 0 ? (r.stdout || '').trim() : '';
  return path.resolve(top || dir);
}

function hasProfile(root) {
  return fs.existsSync(path.join(root, '.devfactory', 'profile.md'));
}

function script(root, args, timeout = 5000) {
  return spawnSync(process.execPath, [SCRIPT, ...args], {
    cwd: root,
    encoding: 'utf8',
    timeout,
    windowsHide: true,
  });
}

// One profile field's value, or null when the profile, the section or the field is missing.
function profileField(root, section, field) {
  const r = script(root, ['profile', '--section', section, '--field', field]);
  return !r.error && r.status === 0 ? (r.stdout || '').replace(/\r?\n$/, '') : null;
}

// One profile section's lines, or null.
function profileSection(root, section) {
  const r = script(root, ['profile', '--section', section]);
  return !r.error && r.status === 0 ? (r.stdout || '').split(/\r?\n/) : null;
}

// A hook is on unless its line under Hooks says off.
function hookOff(root, name) {
  const value = profileField(root, 'Hooks', name);
  return value !== null && /^`?off\b/i.test(value.trim());
}

// The markers in a root, as { name, stale, line } from the script's `markers` listing.
function markers(root) {
  const r = script(root, ['markers']);
  if (r.error || r.status !== 0) return [];
  const out = [];
  for (const line of (r.stdout || '').split(/\r?\n/)) {
    const m = /^(active|stale) (\S+) /.exec(line);
    if (m) out.push({ name: m[2], stale: m[1] === 'stale', line });
  }
  return out;
}

// The first backticked token of a profile value, else its first word.
function firstToken(value) {
  if (!value) return '';
  const ticked = /`([^`]+)`/.exec(value);
  return (ticked ? ticked[1] : value.trim().split(/\s+/)[0] || '').trim();
}

// Splits a command line into segments at unquoted ; & | ( ) and newlines, and each segment
// into words, honouring single and double quotes and backslash escapes.
function segments(command) {
  const result = [];
  let words = [];
  let word = '';
  let inWord = false;
  let quote = null;
  const endWord = () => {
    if (inWord) words.push(word);
    word = '';
    inWord = false;
  };
  const endSegment = () => {
    endWord();
    if (words.length) result.push(words);
    words = [];
  };
  for (let i = 0; i < command.length; i++) {
    const c = command[i];
    if (quote) {
      if (c === quote) quote = null;
      // Inside double quotes a backslash escapes only $ ` " and \, as in bash.
      else if (c === '\\' && quote === '"' && '$`"\\'.includes(command[i + 1] || '#')) word += command[++i];
      else word += c;
      continue;
    }
    if (c === "'" || c === '"') {
      quote = c;
      inWord = true;
    } else if (c === '\\' && i + 1 < command.length) {
      word += command[++i];
      inWord = true;
    } else if (';&|()\n\r'.includes(c)) {
      endSegment();
    } else if (c === ' ' || c === '\t') {
      endWord();
    } else {
      word += c;
      inWord = true;
    }
  }
  endSegment();
  return result;
}

const WRAPPERS = new Set(['command', 'exec', 'time', 'nohup', 'sudo', 'env', 'builtin']);

// The words of a segment from its command token on: leading VAR=value assignments and
// wrappers such as env or sudo are dropped.
function commandWords(words) {
  let i = 0;
  while (i < words.length && (/^[A-Za-z_][A-Za-z0-9_]*=/.test(words[i]) || WRAPPERS.has(words[i]))) i++;
  return words.slice(i);
}

function isProgram(word, name) {
  return new RegExp(`(^|[\\\\/])${name}(\\.exe)?$`, 'i').test(word || '');
}

function deny(reason) {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny',
      permissionDecisionReason: reason,
    },
  }));
}

module.exports = {
  SCRIPT,
  readInput,
  inputCwd,
  projectRoot,
  hasProfile,
  script,
  profileField,
  profileSection,
  hookOff,
  markers,
  firstToken,
  segments,
  commandWords,
  isProgram,
  deny,
};
