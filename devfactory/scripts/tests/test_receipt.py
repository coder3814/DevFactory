import os
import unittest

from .helpers import git, run, temp_dir, write


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
        self.assertEqual(run(['receipt', 'write', 'specs/12'] + READY, d).code, 0)
        commit(d, 'spec')
        return d

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
