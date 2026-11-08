import hashlib
import os
import unittest

from . import helpers
from .helpers import git, run, spec_text, temp_dir, write

devfactory = helpers.load_script()


def sha(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


class StampTest(unittest.TestCase):
    def test_stamp_text_normalises_crlf_drops_spec_lines_and_trailing_line_feeds(self):
        d = temp_dir(self)
        crlf = os.path.join(d, 'crlf.txt')
        lf = os.path.join(d, 'lf.txt')
        write(crlf, 'Add export\r\n## Summary\r\nExports the list.\r\nSpec: specs/12/ @ 0a1b2c3\r\n- **C1.** It exports.\r\r\n\r\n')
        write(lf, 'Add export\n## Summary\nExports the list.\n- **C1.** It exports.\n')

        expected = sha('Add export\n## Summary\nExports the list.\n- **C1.** It exports.')
        a = run(['stamp', '--text', crlf], d)
        b = run(['stamp', '--text', lf], d)
        self.assertEqual(a.code, 0, a.stderr)
        self.assertEqual(a.lines, [expected])
        self.assertEqual(b.lines, [expected])

    def test_a_line_that_only_mentions_a_spec_is_kept(self):
        self.assertEqual(devfactory.card_text('T', 'See Spec: specs/1/ @ abc\nSpec: specs/1/ @ ABC'),
                         'T\nSee Spec: specs/1/ @ abc\nSpec: specs/1/ @ ABC')

    def stamped_repo(self, card_body):
        d = temp_dir(self)
        git(d, 'init', '-q')
        write(os.path.join(d, 'README.md'), 'x\n')
        git(d, 'add', '.')
        git(d, 'commit', '-q', '-m', 'base')
        head = git(d, 'rev-parse', 'HEAD')
        card = os.path.join(d, 'card.txt')
        write(card, 'Add export\n' + card_body)
        revision = run(['stamp', '--text', card], d).lines[0]
        self.assertEqual(revision, devfactory.card_revision('Add export', card_body))
        return d, head, card, revision

    def test_stamp_check_reports_match_and_ancestor_when_nothing_changed(self):
        d, head, card, revision = self.stamped_repo('- **C1.** It exports.\n')
        write(os.path.join(d, 'specs', '12', 'spec.md'), spec_text(revision=revision, commit=head))
        r = run(['stamp-check', '--text', card, '--spec', os.path.join(d, 'specs', '12')], d)
        self.assertEqual(r.code, 0, r.stdout + r.stderr)
        self.assertEqual(r.lines, ['match', 'ancestor'])

    def test_stamp_check_reports_changed_with_both_revisions_when_the_card_text_changed(self):
        d, head, card, revision = self.stamped_repo('- **C1.** It exports.\n')
        write(os.path.join(d, 'specs', '12', 'spec.md'), spec_text(revision=revision, commit=head))
        write(card, 'Add export\n- **C1.** It exports as CSV.\n')
        now = run(['stamp', '--text', card], d).lines[0]
        r = run(['stamp-check', '--text', card, '--spec', os.path.join(d, 'specs', '12')], d)
        self.assertEqual(r.code, 1)
        self.assertEqual(r.lines, ['changed %s %s' % (revision, now), 'ancestor'])

    def test_stamp_check_reports_not_ancestor_when_the_stamped_commit_is_off_the_branch(self):
        d, _, card, revision = self.stamped_repo('- **C1.** It exports.\n')
        orphan = git(d, 'commit-tree', 'HEAD^{tree}', '-m', 'elsewhere')
        write(os.path.join(d, 'specs', '12', 'spec.md'), spec_text(revision=revision, commit=orphan))
        r = run(['stamp-check', '--text', card, '--spec', os.path.join(d, 'specs', '12')], d)
        self.assertEqual(r.code, 1)
        self.assertEqual(r.lines, ['match', 'not-ancestor'])


if __name__ == '__main__':
    unittest.main()
