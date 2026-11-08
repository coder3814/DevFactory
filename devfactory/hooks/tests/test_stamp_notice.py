import json
import os
import re
import subprocess
import sys
import unittest

from .helpers import SCRIPT, git, project, run_hook, write

PROFILE = '\n'.join([
    '# Project profile: Example',
    '',
    '## Specs',
    '- **Path:** `docs/specs/`',
    '',
    '## Hooks',
    '- Stamp notice: on',
    '',
])


def spec(revision, commit, status=None):
    status = status or ('Ready' if revision else 'drafting')
    return '\n'.join([
        '# Spec: Add export',
        '',
        '| | |',
        '|---|---|',
        '| **Card** | #12 |',
        '| **Version** | 1 |',
        '| **Status** | %s |' % status,
        '| **Card revision** | %s |' % revision,
        '| **Repo commit** | %s |' % commit,
        '| **Stamped** | 2026-11-07 |',
        '| **Request type(s)** | feature |',
        '',
    ])


class StampNoticeTest(unittest.TestCase):
    def setup_repo(self):
        """A repository with the profile, a card text file and its revision."""
        cwd = project(self, profile=PROFILE, branch='main')
        head = git(cwd, 'rev-parse', 'HEAD')
        card = os.path.join(cwd, 'card.txt')
        write(card, 'Add export\n- **C1.** It exports.\n')
        revision = subprocess.run([sys.executable, SCRIPT, 'stamp', '--text', card],
                                  stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

        def write_spec(n, text):
            os.makedirs(os.path.join(cwd, 'docs', 'specs', n), exist_ok=True)
            write(os.path.join(cwd, 'docs', 'specs', n, 'spec.md'), text)
        return cwd, head, card, revision, write_spec

    def notice(self, cwd, prompt, card):
        out = run_hook(self, 'stamp_notice.py', {'session_id': 'test', 'cwd': cwd,
                                                 'hook_event_name': 'UserPromptSubmit', 'prompt': prompt},
                       {'DEVFACTORY_STAMP_TEXT': card})
        return json.loads(out)['hookSpecificOutput']['additionalContext'].split('\n') if out else []

    def test_a_current_spec_is_reported_current_a_changed_card_as_changed(self):
        cwd, head, card, revision, write_spec = self.setup_repo()
        write_spec('12', spec(revision, head))
        self.assertEqual(self.notice(cwd, 'build #12', card), ["DevFactory: card 12's spec is current (Ready at %s)" % head])
        write(card, 'Add export\n- **C1.** It exports as CSV.\n')
        self.assertRegex(self.notice(cwd, 'build card 12', card)[0], r'^DevFactory: card 12 changed since its spec earned Ready')

    def test_a_drafting_spec_with_no_card_revision_is_silence_another_stamp_error_is_reported(self):
        cwd, _, card, revision, write_spec = self.setup_repo()
        write_spec('12', spec('', ''))
        self.assertEqual(self.notice(cwd, 'grill #12', card), [])
        write_spec('13', spec(revision, ''))
        self.assertRegex(self.notice(cwd, 'grill #13', card)[0], r"^DevFactory: could not check card 13's spec .*has no Repo commit")

    def test_a_drafting_spec_is_silence_even_when_it_carries_stamp_rows(self):
        cwd, head, card, revision, write_spec = self.setup_repo()
        write_spec('12', spec(revision, head, 'drafting'))
        write_spec('13', spec(revision, '', '`drafting`'))
        write(card, 'Add export\n- **C1.** It exports as CSV.\n')
        self.assertEqual(self.notice(cwd, 'grill #12 and #13', card), [])
        write_spec('12', spec(revision, head, 'approved'))
        self.assertRegex(self.notice(cwd, 'grill #12', card)[0], r'^DevFactory: card 12 changed since its spec earned Ready')

    def test_at_most_two_cards_are_checked_and_a_card_without_a_spec_is_skipped(self):
        cwd, head, card, revision, write_spec = self.setup_repo()
        for n in ['12', '13', '14']:
            write_spec(n, spec(revision, head))
        lines = self.notice(cwd, 'compare #99, #12, #13 and #14', card)
        self.assertEqual([re.search(r'card (\d+)', l).group(1) for l in lines], ['12', '13'])

    def test_stamp_notice_off_means_silence(self):
        cwd, head, card, revision, write_spec = self.setup_repo()
        write_spec('12', spec(revision, head))
        write(os.path.join(cwd, '.devfactory', 'profile.md'), PROFILE.replace('- Stamp notice: on', '- Stamp notice: off'))
        self.assertEqual(self.notice(cwd, 'build #12', card), [])


if __name__ == '__main__':
    unittest.main()
