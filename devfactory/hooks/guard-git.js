#!/usr/bin/env node
// PreToolUse (Bash): refuses a git push, and a merge or rebase that touches the integration
// branch or a parent branch, while neither the release nor the coordinate skill is running.
// A build session may fast-forward a parent branch (git merge --ff-only) and rebase its own
// card branch, as the coordinator asks; it never pushes. Silent (allow) otherwise, on a
// missing profile, on "Git guard: off", and on any error. Never throws; always exits 0.
'use strict';

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

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

// The branch name in a profile value: the first backticked token, else the first word.
function branchToken(value) {
  if (!value) return '';
  const ticked = /`([^`]+)`/.exec(value);
  return (ticked ? ticked[1] : value.split(/\s+/)[0] || '').trim();
}

// A parent-branch pattern such as parent-<N>: <N> is digits, any other <placeholder> is a
// run of branch-name characters, everything else is literal.
function patternRegex(pattern) {
  if (!pattern) return null;
  let source = '';
  const parts = pattern.split(/(<[^>]+>)/);
  for (const part of parts) {
    if (!part) continue;
    if (/^<n>$/i.test(part)) source += '\\d+';
    else if (/^<[^>]+>$/.test(part)) source += '[A-Za-z0-9._/-]+';
    else source += part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  return new RegExp('^' + source + '$');
}

function normaliseBranch(name) {
  return String(name)
    .replace(/^refs\/heads\//, '')
    .replace(/^refs\/remotes\//, '')
    .replace(/^origin\//, '');
}

// Splits a command line into segments at unquoted ; & | and newlines, and each segment into
// words, honouring single and double quotes and backslash escapes.
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
      else if (c === '\\' && quote === '"' && i + 1 < command.length) word += command[++i];
      else word += c;
      continue;
    }
    if (c === "'" || c === '"') {
      quote = c;
      inWord = true;
    } else if (c === '\\' && i + 1 < command.length) {
      word += command[++i];
      inWord = true;
    } else if (c === ';' || c === '&' || c === '|' || c === '\n' || c === '\r') {
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

const GLOBAL_WITH_VALUE = new Set(['-C', '-c', '--git-dir', '--work-tree', '--namespace',
  '--exec-path', '--config-env']);
const VALUE_OPTIONS = {
  merge: new Set(['-m', '-s', '-X', '-F', '--strategy', '--strategy-option', '--file',
    '--message', '--into-name', '--cleanup']),
  rebase: new Set(['-s', '-X', '-x', '--exec', '--strategy', '--strategy-option']),
};

// Parses one segment into { sub, args, flags, dir } when it runs git, else null.
function parseGit(words, dir) {
  const at = words.findIndex((w) => /(^|[\\/])git(\.exe)?$/i.test(w));
  if (at < 0) return null;
  let i = at + 1;
  let gitDir = dir;
  while (i < words.length && words[i].startsWith('-')) {
    const opt = words[i];
    if (opt === '-C' && i + 1 < words.length) {
      gitDir = path.resolve(gitDir, words[i + 1]);
      i += 2;
    } else if (GLOBAL_WITH_VALUE.has(opt)) {
      i += 2;
    } else {
      i += 1;
    }
  }
  const sub = words[i];
  if (!sub) return null;
  const takesValue = VALUE_OPTIONS[sub] || new Set();
  const args = [];
  const flags = [];
  for (let j = i + 1; j < words.length; j++) {
    const w = words[j];
    if (w === '--onto' && j + 1 < words.length) {
      args.push(words[++j]);
    } else if (w.startsWith('--onto=')) {
      args.push(w.slice('--onto='.length));
    } else if (w.startsWith('-')) {
      flags.push(w.split('=')[0]);
      if (takesValue.has(w)) j++;
    } else {
      args.push(w);
    }
  }
  return { sub, args, flags, dir: gitDir };
}

function currentBranch(dir) {
  try {
    return execFileSync('git', ['rev-parse', '--abbrev-ref', 'HEAD'], {
      cwd: dir,
      encoding: 'utf8',
      timeout: 5000,
      stdio: ['ignore', 'pipe', 'ignore'],
      windowsHide: true,
    }).trim();
  } catch (e) {
    return '';
  }
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

function main() {
  const input = JSON.parse(fs.readFileSync(0, 'utf8'));
  if (input.tool_name !== 'Bash') return;
  const command = input.tool_input && input.tool_input.command;
  if (typeof command !== 'string' || !/\bgit\b/.test(command)) return;
  const cwd = input.cwd || process.env.CLAUDE_PROJECT_DIR || process.cwd();
  let profile;
  try {
    profile = readProfile(cwd);
  } catch (e) {
    return; // no profile: silence
  }
  if (isOff(profile, 'Git guard')) return;

  const markers = activeMarkers(cwd);
  if (markers.includes('release') || markers.includes('coordinate')) return;
  const building = markers.includes('build');

  const branches = (profile['branches and merging'] || { fields: {} }).fields;
  const integration = branchToken(branches['integration branch']);
  const parentRe = patternRegex(branchToken(branches['parent branch']));
  const isIntegration = (b) => !!integration && normaliseBranch(b) === integration;
  const isParent = (b) => !!parentRe && parentRe.test(normaliseBranch(b));
  const isProtected = (b) => isIntegration(b) || isParent(b);

  let dir = cwd;
  for (const words of segments(command)) {
    if (words[0] === 'cd' && words[1]) {
      dir = path.resolve(dir, words[1]);
      continue;
    }
    const git = parseGit(words, dir);
    if (!git) continue;

    if (git.sub === 'push') {
      deny(building
        ? 'DevFactory: a build session never pushes; a push is the release, which goes ' +
          'through the release skill.'
        : 'DevFactory: a push goes through the release skill, or coordinate for a parent ' +
          'issue; neither is running.');
      return;
    }

    if (git.sub !== 'merge' && git.sub !== 'rebase') continue;
    if (git.flags.some((f) => f === '--abort' || f === '--quit')) continue;

    const hitArgs = git.args.filter(isProtected);
    const head = currentBranch(git.dir);
    const headProtected = !!head && head !== 'HEAD' && isProtected(head);
    if (hitArgs.length === 0 && !headProtected) continue;

    if (building) {
      const touchesIntegration = isIntegration(head) || git.args.some(isIntegration);
      if (git.sub === 'merge' && git.flags.includes('--ff-only') && !touchesIntegration) {
        continue; // the fast-forward of a parent branch the coordinator asks for
      }
      if (git.sub === 'rebase' && !headProtected) {
        continue; // rebasing the card's own branch onto the parent or integration branch
      }
    }

    const named = Array.from(new Set(hitArgs.concat(headProtected ? [head] : [])));
    deny(building
      ? `DevFactory: a build session may only fast-forward a parent branch with git merge ` +
        `--ff-only and rebase its own branch; this ${git.sub} touches ${named.join(', ')}, ` +
        `which goes through the release skill or coordinate.`
      : `DevFactory: a ${git.sub} touching ${named.join(', ')} goes through the release ` +
        `skill, or coordinate for a parent issue; neither is running.`);
    return;
  }
}

try {
  main();
} catch (e) {
  // silence on any error
}
process.exitCode = 0;
