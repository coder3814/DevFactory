import os
import re
import unittest

from .helpers import git, read, run, temp_dir, write


def repo(test):
    d = temp_dir(test)
    git(d, 'init', '-q')
    write(os.path.join(d, '.devfactory', 'profile.md'), '# Profile\n\n## Specs\n- Path: specs/\n')
    write(os.path.join(d, 'src', 'app.py'), 'x = 1\n')
    write(os.path.join(d, 'specs', '12', 'spec.md'),
          '# Spec: Add export\n\n| | |\n|---|---|\n| **Status** | Ready |\n| **Version** | 1 |\n')
    write(os.path.join(d, 'card.txt'), 'Add export\n- **C1.** It exports.\n')
    write(os.path.join(d, 'facts.txt'), 'comment 2026-11-01 pat\nfield Work type: Feature\n')
    write(os.path.join(d, 'specs.txt'), 'specs/12\n')
    commit(d, 'base')
    return d


def commit(d, message):
    git(d, 'add', '-A')
    git(d, 'commit', '-q', '-m', message)


REQUEST = ['--check', 'request', '--text', 'card.txt', '--facts', 'facts.txt']
READY = ['--check', 'ready', '--specs', 'specs.txt']


class RequestReceiptTest(unittest.TestCase):
    def test_no_receipt_until_one_is_written(self):
        d = repo(self)
        r = run(['receipt', 'check', 'specs/12'] + REQUEST, d)
        self.assertEqual((r.code, r.lines), (1, ['no-receipt request']))

    def test_matches_when_nothing_changed(self):
        d = repo(self)
        self.assertEqual(run(['receipt', 'write', 'specs/12'] + REQUEST, d).code, 0)
        r = run(['receipt', 'check', 'specs/12'] + REQUEST, d)
        self.assertEqual((r.code, r.lines), (0, ['match request']), r.stderr)

    def test_fact_order_and_spacing_do_not_matter(self):
        d = repo(self)
        run(['receipt', 'write', 'specs/12'] + REQUEST, d)
        write(os.path.join(d, 'facts.txt'), '  field Work type:   Feature\r\n\r\ncomment 2026-11-01 pat\n')
        self.assertEqual(run(['receipt', 'check', 'specs/12'] + REQUEST, d).code, 0)

    def test_sub_issue_lines_compare_as_a_set(self):
        d = repo(self)
        write(os.path.join(d, 'facts.txt'), 'sub-issue 13\nsub-issue 14\n')
        run(['receipt', 'write', 'specs/12'] + REQUEST, d)
        write(os.path.join(d, 'facts.txt'), 'sub-issue 14\nsub-issue 13\n')
        r = run(['receipt', 'check', 'specs/12'] + REQUEST, d)
        self.assertEqual((r.code, r.lines), (0, ['match request']), r.stderr)
        write(os.path.join(d, 'facts.txt'), 'sub-issue 14\nsub-issue 15\n')
        r = run(['receipt', 'check', 'specs/12'] + REQUEST, d)
        self.assertEqual(r.code, 1)
        self.assertTrue(r.lines[0].startswith('differs Card facts '))

    def test_the_standard_is_the_hash_alone_and_the_older_version_form_still_matches(self):
        d = repo(self)
        run(['receipt', 'write', 'specs/12'] + REQUEST, d)
        file = os.path.join(d, 'specs', '12', 'receipts.md')
        text = read(file)
        m = re.search(r'^- Standard: (.*)$', text, re.M)
        self.assertRegex(m.group(1), r'^[0-9a-f]{64}$')
        write(file, text.replace(m.group(0), '- Standard: 0.0.1 %s' % m.group(1)))
        r = run(['receipt', 'check', 'specs/12'] + REQUEST, d)
        self.assertEqual((r.code, r.lines), (0, ['match request']), r.stderr)
        write(file, text.replace(m.group(0), '- Standard: 0.0.1 %s' % ('0' * 64)))
        r = run(['receipt', 'check', 'specs/12'] + REQUEST, d)
        self.assertEqual(r.code, 1)
        self.assertTrue(r.lines[0].startswith('differs Standard 0.0.1 '))

    def test_a_new_comment_a_card_edit_or_a_profile_edit_each_differ(self):
        d = repo(self)
        run(['receipt', 'write', 'specs/12'] + REQUEST, d)
        write(os.path.join(d, 'facts.txt'), 'comment 2026-11-01 pat\ncomment 2026-11-02 sam\nfield Work type: Feature\n')
        write(os.path.join(d, 'card.txt'), 'Add export\n- **C1.** It exports as CSV.\n')
        write(os.path.join(d, '.devfactory', 'modules', 'work-type.md'), 'rules\n')
        r = run(['receipt', 'check', 'specs/12'] + REQUEST, d)
        self.assertEqual(r.code, 1)
        self.assertEqual(len(r.lines), 3)
        self.assertTrue(r.lines[0].startswith('differs Card revision '))
        self.assertTrue(r.lines[1].startswith('differs Card facts '))
        self.assertTrue(r.lines[2].startswith('differs Profile '))


class ReadyReceiptTest(unittest.TestCase):
    def written(self):
        d = repo(self)
        r = run(['receipt', 'write', 'specs/12'] + READY + ['--commit', 'HEAD'], d)
        self.assertEqual(r.code, 0, r.stderr)
        commit(d, 'spec')
        return d

    def test_write_needs_a_commit_that_exists_and_records_its_full_hash(self):
        d = repo(self)
        self.assertEqual(run(['receipt', 'write', 'specs/12'] + READY, d).code, 2)
        r = run(['receipt', 'write', 'specs/12'] + READY + ['--commit', 'deadbeef'], d)
        self.assertEqual(r.code, 2)
        self.assertIn('--commit deadbeef is not a commit', r.stderr)
        read_at = git(d, 'rev-parse', 'HEAD')
        write(os.path.join(d, 'src', 'app.py'), 'x = 2\n')
        commit(d, 'code after the checker read')
        r = run(['receipt', 'write', 'specs/12'] + READY + ['--commit', read_at[:7]], d)
        self.assertEqual(r.code, 0, r.stderr)
        self.assertIn('- Repo commit: %s\n' % read_at, read(os.path.join(d, 'specs', '12', 'receipts.md')))
        r = run(['receipt', 'check', 'specs/12'] + READY, d)
        self.assertEqual(r.code, 1, 'the code changed after the commit the checker read')
        self.assertTrue(r.lines[-1].startswith('differs Repo commit %s ' % read_at))

    def test_check_takes_no_commit(self):
        d = self.written()
        r = run(['receipt', 'check', 'specs/12'] + READY + ['--commit', 'HEAD'], d)
        self.assertEqual(r.code, 2)
        self.assertIn('unknown flag --commit for receipt check', r.stderr)

    def test_the_parent_card_revision_is_recorded_and_compared(self):
        d = repo(self)
        write(os.path.join(d, 'specs', 'parent.txt'), 'Export\n## Work order\n1. #12\n')
        parent = ['--parent-text', 'specs/parent.txt']
        self.assertEqual(run(['receipt', 'write', 'specs/12'] + READY + ['--commit', 'HEAD'] + parent, d).code, 0)
        self.assertRegex(read(os.path.join(d, 'specs', '12', 'receipts.md')), r'- Parent card: [0-9a-f]{64}\n')
        commit(d, 'receipt')
        r = run(['receipt', 'check', 'specs/12'] + READY + parent, d)
        self.assertEqual((r.code, r.lines), (0, ['match ready']), r.stdout + r.stderr)
        r = run(['receipt', 'check', 'specs/12'] + READY, d)
        self.assertEqual(r.code, 2, 'a recorded parent revision cannot be left unchecked')
        write(os.path.join(d, 'specs', 'parent.txt'), 'Export\n## Work order\n1. #12\n2. #13\n')
        r = run(['receipt', 'check', 'specs/12'] + READY + parent, d)
        self.assertEqual(r.code, 1)
        self.assertEqual([l.split(' ')[1] + ' ' + l.split(' ')[2] for l in r.lines], ['Parent card'])

    def test_matches_after_the_spec_commit_and_an_approval(self):
        d = self.written()
        spec = os.path.join(d, 'specs', '12', 'spec.md')
        with open(spec, encoding='utf-8') as f:
            text = f.read()
        write(spec, text.replace('| Ready |', '| approved |'))
        commit(d, 'approve')
        r = run(['receipt', 'check', 'specs/12'] + READY, d)
        self.assertEqual((r.code, r.lines), (0, ['match ready']), r.stdout + r.stderr)

    def test_a_code_change_differs(self):
        d = self.written()
        write(os.path.join(d, 'src', 'app.py'), 'x = 2\n')
        commit(d, 'code')
        r = run(['receipt', 'check', 'specs/12'] + READY, d)
        self.assertEqual(r.code, 1)
        self.assertEqual(len(r.lines), 1)
        self.assertTrue(r.lines[0].startswith('differs Repo commit '))

    def test_a_spec_edit_or_a_new_gap_differs(self):
        d = self.written()
        spec = os.path.join(d, 'specs', '12', 'spec.md')
        with open(spec, encoding='utf-8') as f:
            text = f.read()
        write(spec, text.replace('| 1 |', '| 2 |'))
        write(os.path.join(d, 'specs', '12', 'gaps.md'), '# Gaps\n')
        r = run(['receipt', 'check', 'specs/12'] + READY, d)
        self.assertEqual(r.code, 1)
        self.assertEqual([' '.join(l.split(' ')[1:3]) for l in r.lines], ['Specs content', 'Gap sources'])

    def test_a_different_set_of_specs_differs(self):
        d = self.written()
        write(os.path.join(d, 'specs', '13', 'spec.md'), '# Spec\n')
        write(os.path.join(d, 'specs.txt'), 'specs/12\nspecs/13\n')
        r = run(['receipt', 'check', 'specs/12'] + READY, d)
        self.assertEqual(r.code, 1)
        self.assertTrue(r.lines[0].startswith('differs Specs specs/12 '))

    def test_both_receipts_live_in_one_file(self):
        d = self.written()
        run(['receipt', 'write', 'specs/12'] + REQUEST, d)
        self.assertEqual(run(['receipt', 'check', 'specs/12'] + READY, d).code, 0)
        self.assertEqual(run(['receipt', 'check', 'specs/12'] + REQUEST, d).code, 0)


if __name__ == '__main__':
    unittest.main()
