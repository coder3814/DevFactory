import os
import re
import unittest

from .helpers import read, run, temp_dir, write


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
