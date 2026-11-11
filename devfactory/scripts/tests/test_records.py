import os
import re
import unittest

from .helpers import git, read, run, spec_text, temp_dir, write


class RecordsTest(unittest.TestCase):
    def test_criteria_ids_lists_ids_allows_a_numbering_gap_and_fails_on_a_duplicate(self):
        d = temp_dir(self)
        ok = os.path.join(d, 'ok.txt')
        dup = os.path.join(d, 'dup.txt')

        def card(c):
            return ('Add export\r\n### Summary\r\n- C9 is not a criterion here.\r\n### Acceptance criteria\r\n'
                    '%s### Suggested model and effort\r\n- C7 neither.\r\n' % c)
        write(ok, card('- **C1.** It exports.\r\n- **C3.** It names the file.\r\n'))
        write(dup, card('- **C1.** It exports.\r\n- **C3.** It names the file.\r\n- **C3.** It again.\r\n'))

        a = run(['criteria-ids', '--text', ok], d)
        self.assertEqual(a.code, 0, a.stderr)
        self.assertEqual(a.lines, ['C1', 'C3'])

        b = run(['criteria-ids', '--text', dup], d)
        self.assertEqual(b.code, 1)
        self.assertEqual(b.lines[:2], ['C1', 'C3'])
        self.assertRegex(b.lines[2], r'^duplicate C3\b')

    def test_gaps_add_appends_entries_check_fails_on_an_open_one_ledger_copies_them(self):
        d = temp_dir(self)
        spec = os.path.join(d, 'specs', '12')
        os.makedirs(spec)

        r = run(['gaps', 'add', spec, '--stage', 'Development', '--question', 'Which format?', '--condition', 'Ready 3.2', '--resolved', '2'], d)
        self.assertEqual(r.code, 0, r.stderr)
        r = run(['gaps', 'check', spec], d)
        self.assertEqual(r.code, 0, r.stdout)

        r = run(['gaps', 'add', spec, '--stage', 'Acceptance', '--question', 'The file name is wrong.', '--condition', 'Done 3.1'], d)
        self.assertEqual(r.code, 0, r.stderr)
        gaps = read(os.path.join(spec, 'gaps.md'))
        self.assertRegex(gaps, r'^## \d{4}-\d{2}-\d{2} — Development\n\n- \*\*Question or refusal:\*\* Which format\?\n- \*\*Let through by:\*\* Ready 3\.2\n- \*\*Resolved by:\*\* 2\n\n## ')
        self.assertRegex(gaps, r'- \*\*Resolved by:\*\* open\n\Z')

        r = run(['gaps', 'check', spec], d)
        self.assertEqual(r.code, 1)
        self.assertEqual(len(r.lines), 1)
        self.assertRegex(r.lines[0], r'^gap-open .*Acceptance: The file name is wrong\.$')

        ledger = os.path.join(d, '.devfactory', 'gaps.md')
        write(ledger, '## #3 (bug fix) — 2026-10-01 — Done\r\n\r\n- **Question or refusal:** Old.\r\n- **Let through by:** Done 4.2\r\n- **Resolved by:** 2\r\n')
        r = run(['gaps', 'ledger', spec, '--card', '#12', '--types', 'feature', '--ledger', ledger], d)
        self.assertEqual(r.code, 0, r.stderr)
        text = read(ledger)
        headings = [l for l in re.split(r'\r?\n', text) if l.startswith('## ')]
        self.assertEqual(len(headings), 3)
        self.assertRegex(headings[1], r'^## #12 \(feature\) — \d{4}-\d{2}-\d{2} — Development$')
        self.assertRegex(headings[2], r'^## #12 \(feature\) — \d{4}-\d{2}-\d{2} — Acceptance$')
        self.assertRegex(text, r'- \*\*Question or refusal:\*\* The file name is wrong\.\n- \*\*Let through by:\*\* Done 3\.1\n- \*\*Resolved by:\*\* open\n\Z')

    def test_evidence_check_passes_with_sidecars_and_fails_on_a_missing_one(self):
        d = temp_dir(self)
        spec = os.path.join(d, 'spec')
        criteria = os.path.join(d, 'criteria.txt')
        write(criteria, 'C1\r\nC2\r\n')
        sidecar = 'revision: abc1234 | checkpoint: Local | produced by: npm test\r\n'
        write(os.path.join(spec, 'evidence', 'C1', 'test-output.txt'), 'ok\n')
        write(os.path.join(spec, 'evidence', 'C1', 'test-output.txt.txt'), sidecar)
        write(os.path.join(spec, 'evidence', 'C2', 'page.png'), 'png')
        write(os.path.join(spec, 'evidence', 'C2', 'page.png.txt'), sidecar)

        r = run(['evidence-check', spec, '--criteria', criteria], d)
        self.assertEqual(r.code, 0, r.stdout + r.stderr)

        write(os.path.join(spec, 'evidence', 'C2', 'run.log'), 'log')
        r = run(['evidence-check', spec, '--criteria', criteria], d)
        self.assertEqual(r.code, 1)
        self.assertEqual(r.lines, ['sidecar-missing evidence/C2/run.log has no run.log.txt'])

    def evidence_repo(self):
        """A repository with a spec planning C1 and C2 at Local, and C1's committed evidence
        naming the commit before it."""
        d = temp_dir(self)
        git(d, 'init', '-q', '-b', 'main')
        spec = os.path.join(d, 'specs', '12')
        write(os.path.join(spec, 'spec.md'), spec_text())
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'spec')
        produced = git(d, 'rev-parse', 'HEAD')
        criteria = os.path.join(temp_dir(self), 'criteria.txt')
        write(criteria, 'C1\n')
        write(os.path.join(spec, 'evidence', 'C1', 'out.txt'), 'ok\n')
        write(os.path.join(spec, 'evidence', 'C1', 'out.txt.txt'),
              'revision: %s | checkpoint: Local | produced by: npm test\n' % produced[:9])
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'evidence')
        return d, spec, criteria

    def test_evidence_check_passes_on_committed_evidence_at_an_ancestor_and_the_planned_checkpoint(self):
        d, spec, criteria = self.evidence_repo()
        r = run(['evidence-check', spec, '--criteria', criteria], d)
        self.assertEqual(r.code, 0, r.stdout + r.stderr)

    def test_evidence_check_fails_evidence_a_clean_checkout_would_lack(self):
        d, spec, criteria = self.evidence_repo()
        write(os.path.join(d, '.gitignore'), '*.log\n')
        write(os.path.join(spec, 'evidence', 'C1', 'run.log'), 'log')
        write(os.path.join(spec, 'evidence', 'C1', 'run.log.txt'),
              'revision: %s | checkpoint: Local | produced by: npm run job\n' % git(d, 'rev-parse', 'HEAD'))
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'log sidecar, log ignored')
        write(os.path.join(spec, 'evidence', 'C1', 'out.txt'), 'changed\n')
        r = run(['evidence-check', spec, '--criteria', criteria], d)
        self.assertEqual(r.code, 1)
        self.assertEqual([l.split(' ')[:2] for l in r.lines],
                         [['evidence-uncommitted', 'evidence/C1/out.txt'],
                          ['evidence-uncommitted', 'evidence/C1/run.log']])

    def test_evidence_check_fails_a_sidecar_revision_that_is_unknown_or_not_an_ancestor(self):
        d, spec, criteria = self.evidence_repo()
        git(d, 'switch', '-q', '-c', 'other')
        write(os.path.join(d, 'other.txt'), 'x')
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'elsewhere')
        elsewhere = git(d, 'rev-parse', 'HEAD')
        git(d, 'switch', '-q', 'main')
        write(os.path.join(spec, 'evidence', 'C1', 'out.txt.txt'),
              'revision: %s | checkpoint: Local | produced by: npm test\n' % elsewhere)
        write(os.path.join(spec, 'evidence', 'C1', 'page.png'), 'png')
        write(os.path.join(spec, 'evidence', 'C1', 'page.png.txt'),
              'revision: deadbeef | checkpoint: Local | produced by: a browser\n')
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'stale sidecars')
        r = run(['evidence-check', spec, '--criteria', criteria], d)
        self.assertEqual(r.code, 1)
        self.assertEqual(len(r.lines), 2, r.lines)
        self.assertRegex(r.lines[0], r'^sidecar-revision evidence/C1/out\.txt\.txt names %s, which is not an ancestor of HEAD' % elsewhere)
        self.assertRegex(r.lines[1], r'^sidecar-revision evidence/C1/page\.png\.txt names deadbeef, which is not a commit')

    def test_evidence_check_accepts_a_sidecar_revision_a_rebase_carried_over_unaltered(self):
        d, spec, criteria = self.evidence_repo()
        git(d, 'switch', '-q', '-c', 'card')
        write(os.path.join(d, 'feature.txt'), 'feature\n')
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'feature')
        before = git(d, 'rev-parse', 'HEAD')
        write(os.path.join(spec, 'evidence', 'C1', 'out.txt.txt'),
              'revision: %s | checkpoint: Local | produced by: npm test\n' % before)
        git(d, 'commit', '-q', '-am', 'evidence at the feature')
        git(d, 'switch', '-q', 'main')
        write(os.path.join(d, 'elsewhere.txt'), 'x\n')
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'main moves on')
        git(d, 'switch', '-q', 'card')
        git(d, 'rebase', '-q', 'main')
        self.assertNotEqual(git(d, 'rev-parse', 'HEAD~1'), before)
        r = run(['evidence-check', spec, '--criteria', criteria], d)
        self.assertEqual(r.code, 0, r.stdout + r.stderr)

    def test_evidence_check_fails_a_sidecar_checkpoint_the_plan_does_not_give(self):
        d, spec, criteria = self.evidence_repo()
        write(os.path.join(spec, 'evidence', 'C1', 'out.txt.txt'),
              'revision: %s | checkpoint: `local` | produced by: npm test\n' % git(d, 'rev-parse', 'HEAD~1'))
        git(d, 'commit', '-q', '-am', 'same checkpoint, other case')
        r = run(['evidence-check', spec, '--criteria', criteria], d)
        self.assertEqual(r.code, 0, r.stdout)
        write(os.path.join(spec, 'evidence', 'C1', 'out.txt.txt'),
              'revision: %s | checkpoint: in-process host | produced by: npm test\n' % git(d, 'rev-parse', 'HEAD~1'))
        git(d, 'commit', '-q', '-am', 'other checkpoint')
        r = run(['evidence-check', spec, '--criteria', criteria], d)
        self.assertEqual(r.code, 1)
        self.assertEqual(r.lines, ['sidecar-checkpoint evidence/C1/out.txt.txt names checkpoint "in-process host", '
                                   'but the evidence plan gives "local" for C1'])

    def card_with_evidence(self):
        """evidence_repo, then a card branch whose feature commit C1's evidence was captured at."""
        d, spec, criteria = self.evidence_repo()
        git(d, 'switch', '-q', '-c', 'card')
        write(os.path.join(d, 'src', 'feature.txt'), 'feature\n')
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'feature')
        captured = git(d, 'rev-parse', 'HEAD')
        write(os.path.join(spec, 'evidence', 'C1', 'out.txt.txt'),
              'revision: %s | checkpoint: Local | produced by: npm test\n' % captured[:9])
        git(d, 'commit', '-q', '-am', 'evidence at the feature')
        return d, spec, criteria, captured

    def test_evidence_check_fails_an_artifact_captured_before_a_later_code_change(self):
        d, spec, criteria, captured = self.card_with_evidence()
        r = run(['evidence-check', spec, '--criteria', criteria, '--base', 'main'], d)
        self.assertEqual(r.code, 0, r.stdout + r.stderr)
        write(os.path.join(d, 'src', 'feature.txt'), 'feature, reworded\n')
        git(d, 'commit', '-q', '-am', 'review fix')
        r = run(['evidence-check', spec, '--criteria', criteria, '--base', 'main'], d)
        self.assertEqual(r.code, 1)
        self.assertEqual(r.lines, ['evidence-stale evidence/C1/out.txt.txt names %s, but 1 code file the change set '
                                   'touches changed after it (src/feature.txt), so capture it again at the current '
                                   'revision' % captured[:9]])
        r = run(['evidence-check', spec, '--criteria', criteria], d)
        self.assertEqual(r.code, 0, 'without --base the stale test does not run: ' + r.stdout)

    def test_evidence_check_ignores_later_commits_to_specs_evidence_devfactory_and_not_code_paths(self):
        d, spec, criteria, _ = self.card_with_evidence()
        write(os.path.join(spec, 'spec.md'), spec_text(amendments='| Version | Date | What changed | Driven by |\n'
                                                       '|---|---|---|---|\n| 1 | 2026-11-07 | Initial spec | — |\n'
                                                       '| 2 | 2026-11-08 | Log | review |'))
        write(os.path.join(d, 'specs', '13', 'spec.md'), 'another card\n')
        write(os.path.join(spec, 'evidence', 'C1', 'more.txt'), 'more\n')
        write(os.path.join(spec, 'evidence', 'C1', 'more.txt.txt'),
              'revision: %s | checkpoint: Local | produced by: npm test\n' % git(d, 'rev-parse', 'HEAD'))
        write(os.path.join(d, 'docs', 'notes', 'change-feature.md'), 'what changed\n')
        write(os.path.join(d, 'CHANGELOG.md'), 'feature\n')
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'spec amendment, another spec, more evidence, a change note')
        r = run(['evidence-check', spec, '--criteria', criteria, '--base', 'main'], d)
        self.assertEqual(r.code, 1, 'a change note is code until the profile says otherwise')
        self.assertEqual(len(r.lines), 2, r.lines)
        for line in r.lines:
            self.assertRegex(line, r'^evidence-stale evidence/C1/(out|more)\.txt\.txt .*\(CHANGELOG\.md, docs/notes/change-feature\.md\)')
        write(os.path.join(d, '.devfactory', 'profile.md'),
              '# Project profile: Test\n\n## Specs\n- Path: specs/\n- Not code: `docs/notes/`, `CHANGELOG.md`\n')
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'profile names the change notes')
        r = run(['evidence-check', spec, '--criteria', criteria, '--base', 'main'], d)
        self.assertEqual(r.code, 0, r.stdout + r.stderr)

    def test_evidence_check_stale_test_holds_across_a_rebase_and_ignores_code_outside_the_change_set(self):
        d, spec, criteria, captured = self.card_with_evidence()
        git(d, 'switch', '-q', 'main')
        write(os.path.join(d, 'src', 'other.txt'), 'another card\'s code\n')
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'main moves on')
        git(d, 'switch', '-q', 'card')
        git(d, 'rebase', '-q', 'main')
        self.assertNotEqual(git(d, 'rev-parse', 'HEAD~1'), captured)
        base = git(d, 'merge-base', 'main', 'HEAD')
        r = run(['evidence-check', spec, '--criteria', criteria, '--base', base], d)
        self.assertEqual(r.code, 0, r.stdout + r.stderr)
        write(os.path.join(d, 'src', 'feature.txt'), 'feature, fixed after the rebase\n')
        git(d, 'commit', '-q', '-am', 'fix')
        r = run(['evidence-check', spec, '--criteria', criteria, '--base', base], d)
        self.assertEqual(r.code, 1)
        self.assertEqual([l.split(' ')[0] for l in r.lines], ['evidence-stale'])

    def test_evidence_check_exempts_a_capture_at_the_base_and_rejects_an_unknown_base(self):
        d, spec, criteria = self.evidence_repo()
        git(d, 'switch', '-q', '-c', 'card')
        write(os.path.join(d, 'src', 'fix.txt'), 'fixed\n')
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'the fix, after the failing run at base was captured')
        r = run(['evidence-check', spec, '--criteria', criteria, '--base', 'main'], d)
        self.assertEqual(r.code, 0, r.stdout + r.stderr)
        r = run(['evidence-check', spec, '--criteria', criteria, '--base', 'deadbeef'], d)
        self.assertEqual(r.code, 2)
        self.assertIn('--base deadbeef is not a commit', r.stderr)

    def test_begin_writes_a_marker_and_lists_others_with_their_age_end_removes_it(self):
        d = temp_dir(self)
        active = os.path.join(d, '.devfactory', '.active')

        r = run(['begin', 'grill'], d)
        self.assertEqual(r.code, 0, r.stderr)
        self.assertEqual(r.lines, [])
        stamp = read(os.path.join(active, 'grill')).strip()
        self.assertRegex(stamp, r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$')

        r = run(['begin', 'build'], d)
        self.assertEqual(r.code, 0)
        self.assertEqual(len(r.lines), 1)
        self.assertRegex(r.lines[0], r'^active grill since \S+ \(\d+[smhd] ago\)$')

        r = run(['end', 'grill'], d)
        self.assertEqual(r.code, 0)
        self.assertEqual(sorted(os.listdir(active)), ['build'])
        r = run(['end', 'build'], d)
        self.assertEqual(os.listdir(active), [])


if __name__ == '__main__':
    unittest.main()
