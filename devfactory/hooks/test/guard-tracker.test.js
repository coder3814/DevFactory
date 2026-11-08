'use strict';

const test = require('node:test');
const assert = require('node:assert');
const { spawnSync } = require('child_process');
const path = require('path');
const { project, bash, assertDeny } = require('./helpers');

const PROFILE = [
  '# Project profile: Example',
  '',
  '## Tracker',
  '- Binding: github-projects',
  '',
  '## Hooks',
  '- Tracker guard: on',
  '- Git guard: on',
  '',
].join('\n');

const run = (cwd, command) => bash('guard-tracker.js', cwd, command);
const denied = (out) => assertDeny(out, /card skills/);

test('gh issue edit without a marker is denied', (t) => {
  denied(run(project(t, { profile: PROFILE }), 'gh issue edit 12 --body-file body.md'));
});

test('gh issue edit with a marker is allowed silently', (t) => {
  assert.strictEqual(run(project(t, { profile: PROFILE, markers: ['add-to-card'] }), 'gh issue edit 12 --add-label x'), '');
});

test('a stale marker does not count', (t) => {
  denied(run(project(t, { profile: PROFILE, markers: [['add-to-card', 13]] }), 'gh issue comment 12 --body x'));
});

test('gh issue view and a mention inside another command are allowed silently', (t) => {
  const cwd = project(t, { profile: PROFILE });
  assert.strictEqual(run(cwd, 'gh issue view 12 --json title,body'), '');
  assert.strictEqual(run(cwd, 'echo "gh issue edit 12"'), '');
});

test('no profile means silence', (t) => {
  assert.strictEqual(run(project(t, { profile: null }), 'gh issue edit 12 --title x'), '');
});

test('"Tracker guard: off" means silence', (t) => {
  const off = PROFILE.replace('- Tracker guard: on', '- Tracker guard: off');
  assert.strictEqual(run(project(t, { profile: off }), 'gh issue comment 12 --body x'), '');
});

test('gh api writes are denied without a marker', (t) => {
  const cwd = project(t, { profile: PROFILE });
  for (const c of [
    'gh api -X PATCH repos/o/r/issues/12 -f state=closed',
    'gh api --method=DELETE repos/o/r/labels/x',
    'gh api -XPOST repos/o/r/issues/12/comments',
    'gh api repos/o/r/issues/12/comments -f body=hello',
    'gh api repos/o/r/issues -F title=x',
    'gh api repos/o/r/issues/12 --input patch.json',
    "gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {}) { clientMutationId } }'",
    'gh api graphql --input query.json',
  ]) {
    denied(run(cwd, c));
  }
});

test('a gh api graphql call whose query or variables come from a file is denied', (t) => {
  const cwd = project(t, { profile: PROFILE });
  for (const c of [
    'gh api graphql -F query=@query.graphql',
    'gh api graphql -f query=@query.graphql',
    'gh api graphql -Fquery=@query.graphql',
    'gh api graphql --field=query=@query.graphql',
    'gh api graphql --raw-field query=@-',
    "gh api graphql -f query='query($n: Int!) { viewer { login } }' -F vars=@vars.json",
    'gh api graphql --input=query.json',
  ]) {
    denied(run(cwd, c));
  }
  assert.strictEqual(run(project(t, { profile: PROFILE, markers: ['grill'] }), 'gh api graphql -F query=@q.graphql'), '');
});

test('gh api reads are allowed silently', (t) => {
  const cwd = project(t, { profile: PROFILE });
  for (const c of [
    'gh api repos/o/r/issues/12',
    'gh api -X GET search/issues -f q=repo:o/r',
    'gh api --method GET repos/o/r/issues -F per_page=100',
    "gh api graphql -f query='query { viewer { login } }'",
    "gh api graphql -F owner=o -f query='query($owner: String!) { user(login: $owner) { email } }'",
    'gh api repos/o/r/issues --paginate --jq ".[].title"',
  ]) {
    assert.strictEqual(run(cwd, c), '', c);
  }
});

test('malformed input is silence', () => {
  const r = spawnSync(process.execPath, [path.resolve(__dirname, '..', 'guard-tracker.js')], { input: 'not json', encoding: 'utf8' });
  assert.strictEqual(r.status, 0);
  assert.strictEqual(r.stdout, '');
});
