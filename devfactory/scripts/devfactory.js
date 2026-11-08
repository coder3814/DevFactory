#!/usr/bin/env node
'use strict';

// DevFactory's mechanical checks. Node standard library only.
// Exit codes: 0 success, 1 failed check (findings on stdout as "<code> <message>"),
// 2 usage or environment error (message on stderr).

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const childProcess = require('child_process');

class UsageError extends Error {}

const SPEC_LINE = /^Spec: .+ @ [0-9a-f]+$/;
const HEADER_ROWS = ['Card', 'Version', 'Status', 'Card revision', 'Repo commit', 'Stamped', 'Request type(s)'];
const STATUSES = ['drafting', 'Ready', 'approved'];
const SECTIONS = [
  { name: 'Decisions delegated to the developer' },
  { name: 'Boundaries' },
  { name: 'Dispositions' },
  { name: 'Interface surface' },
  { name: 'Data population', optional: true },
  { name: 'Evidence plan' },
  { name: 'Owner steps', optional: true },
  { name: 'Project bindings used' },
  { name: 'Amendments' },
];
const GAP_STAGES = ['Approval', 'Development', 'Done', 'Acceptance'];
const GAP_FIELDS = [
  { key: 'question', label: 'Question or refusal' },
  { key: 'condition', label: 'Let through by' },
  { key: 'resolved', label: 'Resolved by' },
];

// ---------- text helpers ----------

function toLf(s) {
  return String(s).replace(/\r\n?/g, '\n');
}

function readText(file) {
  let raw;
  try {
    raw = fs.readFileSync(file, 'utf8');
  } catch (e) {
    throw new UsageError(`cannot read ${file}: ${e.message}`);
  }
  return toLf(raw.replace(/^﻿/, ''));
}

function readIdList(file) {
  return readText(file)
    .split('\n')
    .map((l) => l.trim())
    .filter((l) => l !== '');
}

function oneLine(s) {
  return toLf(s).split('\n').map((l) => l.trim()).filter(Boolean).join(' ');
}

function today() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

function sha256(s) {
  return crypto.createHash('sha256').update(s, 'utf8').digest('hex');
}

// ---------- the stamp ----------

// The card text as spec-template.md's "The stamp" defines it.
function cardText(title, body) {
  const lines = toLf(body || '').split('\n').filter((l) => !SPEC_LINE.test(l));
  const cleanBody = lines.join('\n').replace(/\n+$/, '');
  return toLf(title || '').replace(/\n+$/, '') + '\n' + cleanBody;
}

function cardRevision(title, body) {
  return sha256(cardText(title, body));
}

// A --text file: first line the title, the rest the body.
function splitTextCard(text) {
  const t = toLf(text);
  const i = t.indexOf('\n');
  return i < 0 ? { title: t, body: '' } : { title: t.slice(0, i), body: t.slice(i + 1) };
}

function ghIssue(card, repo) {
  const n = String(card).replace(/^#/, '');
  if (!/^\d+$/.test(n)) throw new UsageError(`card must be an issue number, got "${card}"`);
  const args = ['issue', 'view', n, '--json', 'title,body'];
  if (repo) args.push('--repo', repo);
  const r = childProcess.spawnSync('gh', args, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
  if (r.error) throw new UsageError(`cannot run gh: ${r.error.message}`);
  if (r.status !== 0) throw new UsageError(`gh issue view ${n} failed: ${(r.stderr || '').trim()}`);
  let j;
  try {
    j = JSON.parse(r.stdout);
  } catch (e) {
    throw new UsageError('gh issue view returned invalid JSON');
  }
  return { title: j.title || '', body: j.body || '' };
}

function readCard(opts) {
  if (opts.text) return splitTextCard(readText(opts.text));
  if (opts.card) return ghIssue(opts.card, opts.repo);
  throw new UsageError('give --card <n> or --text <file>');
}

// ---------- Markdown parsing ----------

function cleanHeading(s) {
  return s.replace(/\s*\*\([^)]*\)\*\s*$/, '').replace(/\s+#+\s*$/, '').trim();
}

// Splits a document into the lines before the first "## " heading and its "## " sections.
function splitSections(text) {
  const out = { preamble: [], sections: [] };
  let cur = null;
  let fence = false;
  for (const line of toLf(text).split('\n')) {
    if (/^\s*(```|~~~)/.test(line)) fence = !fence;
    const m = !fence && /^##\s+(.+)$/.exec(line);
    if (m) {
      cur = { title: cleanHeading(m[1]), lines: [] };
      out.sections.push(cur);
      continue;
    }
    (cur ? cur.lines : out.preamble).push(line);
  }
  return out;
}

function splitRow(line) {
  let s = line.trim();
  if (s.startsWith('|')) s = s.slice(1);
  if (s.endsWith('|') && !s.endsWith('\\|')) s = s.slice(0, -1);
  return s.split(/(?<!\\)\|/).map((c) => c.trim());
}

function isSeparator(line) {
  return /^\|?(\s*:?-+:?\s*\|)*\s*:?-+:?\s*\|?$/.test(line.trim());
}

// Every pipe table in the lines, as { header, rows }.
function parseTables(lines) {
  const tables = [];
  let i = 0;
  while (i < lines.length) {
    if (!lines[i].trim().startsWith('|')) {
      i++;
      continue;
    }
    const block = [];
    while (i < lines.length && lines[i].trim().startsWith('|')) block.push(lines[i++]);
    if (block.length >= 2 && isSeparator(block[1])) {
      tables.push({ header: splitRow(block[0]), rows: block.slice(2).map(splitRow) });
    }
  }
  return tables;
}

function plain(cell) {
  return (cell || '').replace(/\*\*/g, '').trim();
}

function column(table, predicate) {
  return table.header.findIndex((h) => predicate(plain(h).toLowerCase()));
}

function findSection(doc, name) {
  return doc.sections.find((s) => s.title.toLowerCase() === name.toLowerCase());
}

function headerRows(doc) {
  const table = parseTables(doc.preamble)[0];
  const rows = {};
  if (!table) return rows;
  for (const row of [table.header, ...table.rows]) {
    const name = plain(row[0]);
    if (name && !(name in rows)) rows[name] = plain(row[1]);
  }
  return rows;
}

function criterionIdsIn(cell) {
  return (cell || '').match(/\bC\d+\b/g) || [];
}

// ---------- gaps.md ----------

function parseGaps(text) {
  const entries = [];
  const errors = [];
  let cur = null;
  let lastField = null;
  toLf(text).split('\n').forEach((line, idx) => {
    const n = idx + 1;
    if (/^##\s/.test(line)) {
      const m = /^##\s+(\d{4}-\d{2}-\d{2})\s+[—–-]\s+(.+?)\s*$/.exec(line);
      lastField = null;
      if (!m) {
        errors.push(`line ${n}: heading is not "## <date> — <stage>"`);
        cur = null;
        return;
      }
      cur = { date: m[1], stage: m[2], fields: {}, line: n };
      entries.push(cur);
      return;
    }
    if (line.trim() === '') return;
    if (/^#\s/.test(line) && entries.length === 0) return;
    const f = /^\s*[-*]\s+\*\*([^*]+?)\*\*\s*(.*)$/.exec(line);
    if (f && cur) {
      const label = f[1].replace(/:\s*$/, '').trim().toLowerCase();
      const field = GAP_FIELDS.find((g) => g.label.toLowerCase() === label);
      if (!field) {
        errors.push(`line ${n}: unknown field "${f[1]}"`);
        lastField = null;
        return;
      }
      cur.fields[field.key] = f[2].replace(/^:\s*/, '').trim();
      lastField = field.key;
      return;
    }
    if (cur && lastField && /^\s+\S/.test(line)) {
      cur.fields[lastField] = (cur.fields[lastField] + ' ' + line.trim()).trim();
      return;
    }
    errors.push(`line ${n}: text outside an entry's fields`);
  });
  for (const e of entries) {
    if (!GAP_STAGES.includes(e.stage)) errors.push(`line ${e.line}: stage "${e.stage}" is not one of ${GAP_STAGES.join(', ')}`);
    for (const g of GAP_FIELDS) {
      if (!e.fields[g.key]) errors.push(`line ${e.line}: entry has no "${g.label}"`);
    }
  }
  return { entries, errors };
}

function formatGapBody(fields) {
  return GAP_FIELDS.map((g) => `- **${g.label}:** ${fields[g.key]}`).join('\n');
}

function appendBlock(file, block) {
  let prefix = '';
  if (fs.existsSync(file)) {
    const existing = fs.readFileSync(file, 'utf8');
    if (existing.length > 0) prefix = /\n\s*\n$/.test(toLf(existing)) ? '' : existing.endsWith('\n') ? '\n' : '\n\n';
  } else {
    fs.mkdirSync(path.dirname(path.resolve(file)), { recursive: true });
  }
  fs.appendFileSync(file, prefix + block + '\n');
}

function loadGaps(dir) {
  const file = path.join(dir, 'gaps.md');
  if (!fs.existsSync(file)) return null;
  return parseGaps(readText(file));
}

// ---------- commands ----------

function cmdStamp(opts) {
  const card = readCard(opts);
  return { out: [cardRevision(card.title, card.body)], code: 0 };
}

function cmdStampCheck(opts) {
  if (!opts.spec) throw new UsageError('give --spec <dir>');
  const specFile = path.join(opts.spec, 'spec.md');
  if (!fs.existsSync(specFile)) throw new UsageError(`no spec.md in ${opts.spec}`);
  const rows = headerRows(splitSections(readText(specFile)));
  const oldRev = ((rows['Card revision'] || '').match(/[0-9a-f]{64}/i) || [])[0];
  const commit = ((rows['Repo commit'] || '').match(/\b[0-9a-f]{7,40}\b/i) || [])[0];
  if (!oldRev) throw new UsageError(`${specFile} has no Card revision hash`);
  if (!commit) throw new UsageError(`${specFile} has no Repo commit`);
  const card = readCard(opts);
  const newRev = cardRevision(card.title, card.body);
  const out = [];
  const matched = oldRev.toLowerCase() === newRev;
  out.push(matched ? 'match' : `changed ${oldRev.toLowerCase()} ${newRev}`);
  const r = childProcess.spawnSync('git', ['merge-base', '--is-ancestor', commit, 'HEAD'], { encoding: 'utf8' });
  if (r.error) throw new UsageError(`cannot run git: ${r.error.message}`);
  if (r.status !== 0 && r.status !== 1) throw new UsageError(`git merge-base failed: ${(r.stderr || '').trim()}`);
  const ancestor = r.status === 0;
  out.push(ancestor ? 'ancestor' : 'not-ancestor');
  return { out, code: matched && ancestor ? 0 : 1 };
}

function lintSpec(dir, criteria) {
  const findings = [];
  const specFile = path.join(dir, 'spec.md');
  if (!fs.existsSync(specFile)) throw new UsageError(`no spec.md in ${dir}`);
  const doc = splitSections(readText(specFile));

  const rows = headerRows(doc);
  for (const name of HEADER_ROWS) {
    if (!(name in rows)) findings.push(`header-missing ${name}`);
  }
  if ('Status' in rows && !STATUSES.includes(rows.Status)) {
    findings.push(`status-invalid "${rows.Status}" is not one of ${STATUSES.join(', ')}`);
  }

  let last = -1;
  for (const s of doc.sections) {
    const idx = SECTIONS.findIndex((r) => r.name.toLowerCase() === s.title.toLowerCase());
    if (idx < 0) continue;
    if (idx < last) findings.push(`section-order "${SECTIONS[idx].name}" comes after "${SECTIONS[last].name}"`);
    else last = idx;
  }
  for (const r of SECTIONS) {
    if (!r.optional && !findSection(doc, r.name)) findings.push(`section-missing ${r.name}`);
  }

  const disp = findSection(doc, 'Dispositions');
  if (disp) {
    const t = parseTables(disp.lines)[0];
    if (!t) findings.push('dispositions-no-table the Dispositions section has no table');
    else {
      const c = column(t, (h) => h === 'disposition');
      const concern = column(t, (h) => h === 'concern');
      t.rows.forEach((row, i) => {
        if (c < 0 || !plain(row[c])) findings.push(`disposition-blank ${plain(row[concern < 0 ? 0 : concern]) || `row ${i + 1}`}`);
      });
    }
  }

  const ev = findSection(doc, 'Evidence plan');
  if (ev) {
    const t = parseTables(ev.lines)[0];
    if (!t) findings.push('evidence-no-table the Evidence plan section has no table');
    else if (criteria) {
      const c = column(t, (h) => h === 'criterion');
      const planned = new Set();
      t.rows.forEach((row) => criterionIdsIn(c < 0 ? '' : row[c]).forEach((id) => planned.add(id)));
      for (const id of criteria) if (!planned.has(id)) findings.push(`evidence-missing ${id} has no evidence row`);
      const known = new Set(criteria);
      for (const id of planned) if (!known.has(id)) findings.push(`evidence-unknown ${id} is not a criterion of the card`);
    }
  }

  const owner = findSection(doc, 'Owner steps');
  if (owner) {
    for (const t of parseTables(owner.lines).slice(0, 1)) {
      const m = column(t, (h) => h.startsWith('moment'));
      const step = column(t, (h) => h === 'step');
      t.rows.forEach((row, i) => {
        if (m < 0 || !plain(row[m])) findings.push(`owner-step-no-moment ${plain(row[step < 0 ? 0 : step]) || `row ${i + 1}`}`);
      });
    }
  }

  const am = findSection(doc, 'Amendments');
  if (am) {
    const t = parseTables(am.lines)[0];
    if (!t || t.rows.length === 0) findings.push('amendments-empty the Amendments table has no row');
  }

  const gaps = loadGaps(dir);
  if (gaps) for (const e of gaps.errors) findings.push(`gaps-parse ${e}`);
  return findings;
}

function cmdSpecLint(opts) {
  const dir = opts._[0];
  if (!dir) throw new UsageError('give the spec folder');
  const criteria = opts.criteria ? readIdList(opts.criteria) : null;
  const findings = lintSpec(dir, criteria);
  return { out: findings, code: findings.length ? 1 : 0 };
}

// Criterion IDs in a card: C<n> opening a list item, within "Acceptance criteria" if present.
function criteriaIds(body) {
  const doc = toLf(body).split('\n');
  let lines = doc;
  const start = doc.findIndex((l) => /^#{1,6}\s+acceptance criteria\b/i.test(l.trim()));
  if (start >= 0) {
    const level = /^(#+)/.exec(doc[start].trim())[1].length;
    let end = doc.length;
    for (let i = start + 1; i < doc.length; i++) {
      const h = /^(#+)\s/.exec(doc[i].trim());
      if (h && h[1].length <= level) {
        end = i;
        break;
      }
    }
    lines = doc.slice(start + 1, end);
  }
  const ids = [];
  for (const l of lines) {
    const m = /^\s*(?:[-*+]|\d+[.)])\s+(?:\*\*|__)?(C\d+)\b/.exec(l);
    if (m) ids.push(m[1]);
  }
  return ids;
}

function cmdCriteriaIds(opts) {
  const card = readCard(opts);
  const ids = criteriaIds(card.body);
  const seen = new Set();
  const out = [];
  const dups = [];
  for (const id of ids) {
    if (seen.has(id)) {
      if (!dups.includes(id)) dups.push(id);
    } else {
      seen.add(id);
      out.push(id);
    }
  }
  for (const d of dups) out.push(`duplicate ${d} opens more than one criterion`);
  return { out, code: dups.length ? 1 : 0 };
}

function cmdGaps(opts) {
  const [sub, dir] = opts._;
  if (!sub || !dir) throw new UsageError('give gaps add|check|ledger <dir>');
  if (!fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) throw new UsageError(`no folder ${dir}`);
  if (sub === 'add') {
    for (const k of ['stage', 'question', 'condition']) if (!opts[k]) throw new UsageError(`gaps add needs --${k}`);
    if (!GAP_STAGES.includes(opts.stage)) throw new UsageError(`--stage must be one of ${GAP_STAGES.join(', ')}`);
    const fields = { question: oneLine(opts.question), condition: oneLine(opts.condition), resolved: oneLine(opts.resolved || 'open') };
    appendBlock(path.join(dir, 'gaps.md'), `## ${today()} — ${opts.stage}\n\n${formatGapBody(fields)}`);
    return { out: [], code: 0 };
  }
  if (sub === 'check') {
    const gaps = loadGaps(dir);
    if (!gaps) return { out: [], code: 0 };
    const out = gaps.errors.map((e) => `gaps-parse ${e}`);
    for (const e of gaps.entries) {
      if ((e.fields.resolved || '').toLowerCase() === 'open') out.push(`gap-open ${e.date} — ${e.stage}: ${e.fields.question}`);
    }
    return { out, code: out.length ? 1 : 0 };
  }
  if (sub === 'ledger') {
    for (const k of ['card', 'types', 'ledger']) if (!opts[k]) throw new UsageError(`gaps ledger needs --${k}`);
    const gaps = loadGaps(dir);
    if (!gaps) return { out: ['appended 0'], code: 0 };
    if (gaps.errors.length) return { out: gaps.errors.map((e) => `gaps-parse ${e}`), code: 1 };
    const blocks = gaps.entries.map(
      (e) => `## ${opts.card} (${opts.types}) — ${e.date} — ${e.stage}\n\n${formatGapBody(e.fields)}`
    );
    if (blocks.length) appendBlock(opts.ledger, blocks.join('\n\n'));
    return { out: [`appended ${blocks.length}`], code: 0 };
  }
  throw new UsageError(`unknown gaps subcommand "${sub}"`);
}

function listFiles(dir, base = dir) {
  const out = [];
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) out.push(...listFiles(full, base));
    else out.push(path.relative(base, full).split(path.sep).join('/'));
  }
  return out;
}

const SIDECAR = /^revision:\s*\S.*\|\s*checkpoint:\s*\S.*\|\s*produced by:\s*\S/;

function cmdEvidenceCheck(opts) {
  const dir = opts._[0];
  if (!dir) throw new UsageError('give the spec folder');
  if (!opts.criteria) throw new UsageError('give --criteria <file>');
  const out = [];
  for (const id of readIdList(opts.criteria)) {
    const folder = path.join(dir, 'evidence', id);
    if (!fs.existsSync(folder) || !fs.statSync(folder).isDirectory()) {
      out.push(`evidence-missing ${id} has no evidence/${id}/ folder`);
      continue;
    }
    const files = listFiles(folder);
    if (files.length === 0) {
      out.push(`evidence-empty evidence/${id}/ holds nothing`);
      continue;
    }
    const set = new Set(files);
    const artifacts = files.filter((f) => !(f.endsWith('.txt') && set.has(f.slice(0, -4))));
    for (const a of artifacts) {
      const side = `${a}.txt`;
      if (!set.has(side)) {
        out.push(`sidecar-missing evidence/${id}/${a} has no ${path.posix.basename(side)}`);
        continue;
      }
      const lines = readText(path.join(folder, side)).split('\n').filter((l) => l.trim() !== '');
      if (lines.length !== 1) out.push(`sidecar-invalid evidence/${id}/${side} must hold exactly one line`);
      else if (!SIDECAR.test(lines[0].trim())) {
        out.push(`sidecar-invalid evidence/${id}/${side} needs "revision: … | checkpoint: … | produced by: …"`);
      }
    }
  }
  return { out, code: out.length ? 1 : 0 };
}

function markerDir() {
  return path.join(process.cwd(), '.devfactory', '.active');
}

function skillName(opts) {
  const name = opts._[0];
  if (!name || !/^[A-Za-z0-9._-]+$/.test(name)) throw new UsageError('give a skill name (letters, digits, . _ -)');
  return name;
}

function age(ms) {
  const s = Math.max(0, Math.round(ms / 1000));
  if (s < 60) return `${s}s`;
  if (s < 3600) return `${Math.floor(s / 60)}m`;
  if (s < 86400) return `${Math.floor(s / 3600)}h`;
  return `${Math.floor(s / 86400)}d`;
}

function cmdBegin(opts) {
  const name = skillName(opts);
  const dir = markerDir();
  fs.mkdirSync(dir, { recursive: true });
  const out = [];
  for (const other of fs.readdirSync(dir)) {
    if (other === name) continue;
    const file = path.join(dir, other);
    if (!fs.statSync(file).isFile()) continue;
    const stamp = fs.readFileSync(file, 'utf8').trim();
    let t = Date.parse(stamp);
    if (Number.isNaN(t)) t = fs.statSync(file).mtimeMs;
    out.push(`active ${other} since ${new Date(t).toISOString()} (${age(Date.now() - t)} ago)`);
  }
  fs.writeFileSync(path.join(dir, name), new Date().toISOString() + '\n');
  return { out, code: 0 };
}

function cmdEnd(opts) {
  const name = skillName(opts);
  fs.rmSync(path.join(markerDir(), name), { force: true });
  return { out: [], code: 0 };
}

function escapeRe(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function cmdProfile(opts) {
  const file = path.join(process.cwd(), '.devfactory', 'profile.md');
  if (!fs.existsSync(file)) throw new UsageError(`no profile at ${file}`);
  let lines = readText(file).split('\n');
  if (!opts.field) return { out: [lines.join('\n').replace(/\n+$/, '')], code: 0 };
  if (opts.section) {
    const start = lines.findIndex((l) => {
      const h = /^(#{1,6})\s+(.+?)\s*$/.exec(l);
      return h && h[2].toLowerCase() === opts.section.toLowerCase();
    });
    if (start < 0) throw new UsageError(`profile has no section "${opts.section}"`);
    const level = /^(#+)/.exec(lines[start])[1].length;
    let end = lines.length;
    for (let i = start + 1; i < lines.length; i++) {
      const h = /^(#+)\s/.exec(lines[i]);
      if (h && h[1].length <= level) {
        end = i;
        break;
      }
    }
    lines = lines.slice(start + 1, end);
  }
  const re = new RegExp(`^\\s*[-*]\\s+(?:\\*\\*)?${escapeRe(opts.field)}(?:\\*\\*)?:\\s*(.*?)\\s*$`, 'i');
  for (const l of lines) {
    const m = re.exec(l);
    if (m) return { out: [m[1]], code: 0 };
  }
  throw new UsageError(`profile has no "- ${opts.field}:" field${opts.section ? ` under "${opts.section}"` : ''}`);
}

// ---------- entry point ----------

function parseArgs(argv) {
  const opts = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const eq = a.indexOf('=');
      if (eq > 0) {
        opts[a.slice(2, eq)] = a.slice(eq + 1);
      } else {
        if (i + 1 >= argv.length) throw new UsageError(`${a} needs a value`);
        opts[a.slice(2)] = argv[++i];
      }
    } else {
      opts._.push(a);
    }
  }
  return opts;
}

const COMMANDS = {
  stamp: cmdStamp,
  'stamp-check': cmdStampCheck,
  'spec-lint': cmdSpecLint,
  'criteria-ids': cmdCriteriaIds,
  gaps: cmdGaps,
  'evidence-check': cmdEvidenceCheck,
  begin: cmdBegin,
  end: cmdEnd,
  profile: cmdProfile,
};

function main(argv) {
  const [command, ...rest] = argv;
  try {
    const fn = COMMANDS[command];
    if (!fn) throw new UsageError(`unknown command "${command || ''}"; commands: ${Object.keys(COMMANDS).join(', ')}`);
    const { out, code } = fn(parseArgs(rest));
    if (out.length) process.stdout.write(out.join('\n') + '\n');
    return code;
  } catch (e) {
    process.stderr.write(`devfactory: ${e instanceof UsageError ? e.message : e.stack || e}\n`);
    return 2;
  }
}

if (require.main === module) {
  process.exitCode = main(process.argv.slice(2));
}

module.exports = { cardText, cardRevision, splitTextCard, criteriaIds, parseGaps, lintSpec, SPEC_LINE };
