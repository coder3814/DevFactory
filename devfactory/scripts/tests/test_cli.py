import os
import re
import unittest

from . import helpers
from .helpers import git, read, run, spec_text, temp_dir, write

devfactory = helpers.load_script()


class HelpAndFlagsTest(unittest.TestCase):
    def test_help_in_every_form_prints_the_usage_and_exits_0(self):
        d = temp_dir(self)
        for args in [[], ['help'], ['--help'], ['-h'], ['gaps', '--help'], ['receipt', 'write', 'x', '-h'], ['markers', '--help']]:
            r = run(args, d)
            self.assertEqual(r.code, 0, args)
            self.assertEqual(r.lines[0], 'usage: devfactory <command> [<args>]', args)
            self.assertEqual(r.stderr, '')

    def test_the_usage_names_every_command_and_each_flag_it_takes(self):
        usage = devfactory.USAGE
        lines = usage.split('\n')
        for command, (_, flags) in devfactory.COMMANDS.items():
            subs = flags if isinstance(flags, dict) else {None: flags}
            for sub, names in subs.items():
                head = command if sub is None else '%s %s' % (command, sub)
                text = ' '.join(l + ' ' + (lines[i + 1] if i + 1 < len(lines) and lines[i + 1].startswith('      ') else '')
                                for i, l in enumerate(lines) if l.startswith('  %s ' % head) or l == '  %s' % head)
                self.assertTrue(text, head)
                for name in names:
                    self.assertIn('--%s' % name, text, head)
                self.assertEqual(sorted(set(re.findall(r'--([a-z-]+)', text))), sorted(names), head)

    def test_an_unknown_flag_is_a_usage_error_naming_the_command(self):
        d = temp_dir(self)
        cases = [
            (['stamp', '--txt', 'card.txt'], 'unknown flag --txt for stamp'),
            (['gaps', 'check', d, '--condition', 'Ready 3.2'], 'unknown flag --condition for gaps check'),
            (['gaps', 'add', d, '--stage', 'Done', '--question', 'q', '--condition', 'Done 4.2', '--card', '1'],
             'unknown flag --card for gaps add'),
            (['gaps', '--card', '1', 'check', d], 'unknown flag --card for gaps check'),
            (['receipt', 'check', d, '--check', 'ready', '--commit', 'HEAD'], 'unknown flag --commit for receipt check'),
            (['markers', '--post-release'],'unknown flag --post-release for markers'),
            (['begin', 'build', '--force'], 'unknown flag --force for begin'),
            (['profile', '--section=Specs', '--feild', 'Path'], 'unknown flag --feild for profile'),
        ]
        for args, message in cases:
            r = run(args, d)
            self.assertEqual(r.code, 2, args)
            self.assertEqual(r.stderr.strip(), 'devfactory: %s' % message)
        self.assertFalse(os.path.exists(os.path.join(d, 'gaps.md')))
        self.assertFalse(os.path.exists(os.path.join(d, '.devfactory')))

    def test_boolean_flags_take_no_value(self):
        d = temp_dir(self)
        r = run(['markers', '--clear-stale'], d)
        self.assertEqual((r.code, r.lines), (0, []), r.stderr)

    def test_an_unknown_command_is_a_usage_error(self):
        r = run(['stamps'], temp_dir(self))
        self.assertEqual(r.code, 2)
        self.assertIn('unknown command "stamps"', r.stderr)


class SpecOnlyTest(unittest.TestCase):
    def repo(self):
        d = temp_dir(self)
        git(d, 'init', '-q', '-b', 'main')
        write(os.path.join(d, 'src', 'app.py'), 'x = 1\n')
        write(os.path.join(d, 'specs', '12', 'spec.md'), spec_text())
        write(os.path.join(d, 'specs', '120', 'spec.md'), 'another card\n')
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'failed review')
        return d, git(d, 'rev-parse', 'HEAD')

    def test_prints_spec_only_when_every_change_is_inside_the_spec_folder(self):
        d, failed = self.repo()
        write(os.path.join(d, 'specs', '12', 'spec.md'), spec_text(status='approved'))
        write(os.path.join(d, 'specs', '12', 'evidence', 'C1', 'out.txt'), 'ok\n')
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'amendment')
        r = run(['spec-only', os.path.join(d, 'specs', '12'), '--base', failed[:8]], os.path.join(d, 'src'))
        self.assertEqual((r.code, r.lines), (0, ['spec-only']), r.stderr)
        r = run(['spec-only', 'specs/12', '--base', 'HEAD'], d)
        self.assertEqual((r.code, r.lines), (0, ['spec-only']), r.stderr)

    def test_prints_each_path_outside_the_spec_folder(self):
        d, failed = self.repo()
        write(os.path.join(d, 'specs', '12', 'spec.md'), spec_text(status='approved'))
        write(os.path.join(d, 'src', 'app.py'), 'x = 2\n')
        write(os.path.join(d, 'specs', '120', 'spec.md'), 'changed\n')
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'a code fix too')
        r = run(['spec-only', 'specs/12', '--base', failed], d)
        self.assertEqual(r.code, 1)
        self.assertEqual(r.lines, ['outside specs/120/spec.md', 'outside src/app.py'])

    def test_an_unknown_base_or_no_base_is_a_usage_error(self):
        d, _ = self.repo()
        r = run(['spec-only', 'specs/12', '--base', 'deadbeef'], d)
        self.assertEqual(r.code, 2)
        self.assertIn('--base deadbeef is not a commit', r.stderr)
        self.assertEqual(run(['spec-only', 'specs/12'], d).code, 2)


class ReviewsTest(unittest.TestCase):
    def repo(self):
        d = temp_dir(self)
        git(d, 'init', '-q', '-b', 'main')
        write(os.path.join(d, 'src', 'app.py'), 'x = 1\n')
        git(d, 'add', '-A')
        git(d, 'commit', '-q', '-m', 'start')
        return d

    def store(self, d, card):
        return os.path.join(d, '.git', 'devfactory', 'reviews', card + '.md')

    def findings(self, d, text):
        f = os.path.join(temp_dir(self), 'findings.txt')
        write(f, text)
        return f

    def test_add_appends_a_block_per_round_to_the_store_and_show_prints_it(self):
        d = self.repo()
        self.assertEqual(run(['reviews', 'show', '--card', '12'], d).lines, ['no-reviews'])
        f = self.findings(d, 'Done 4.3 | C2 | the export reads every row\r\n\r\n- Done 5.1|-|  an unrelated rename\r\n')
        r = run(['reviews', 'add', '--card', '#12', '--round', '1', '--verdict', 'FAIL', '--findings', f], os.path.join(d, 'src'))
        self.assertEqual((r.code, r.lines), (0, []), r.stderr)
        r = run(['reviews', 'add', '--card', '12', '--round', '2', '--verdict', 'PASS'], d)
        self.assertEqual(r.code, 0, r.stderr)
        text = read(self.store(d, '12'))
        self.assertRegex(text, r'^## \d{4}-\d{2}-\d{2} — round 1 — FAIL\n\n- Done 4\.3 \| C2 \| the export reads every row\n'
                               r'- Done 5\.1 \| - \| an unrelated rename\n\n## \d{4}-\d{2}-\d{2} — round 2 — PASS\n\Z')
        r = run(['reviews', 'show', '--card', '#12'], d)
        self.assertEqual((r.code, r.lines), (0, [l for l in text.split('\n') if l]), r.stderr)
        self.assertEqual(git(d, 'status', '--porcelain'), '', 'the store is outside the tracked tree')

    def test_two_worktrees_of_one_repository_read_the_same_store(self):
        d = self.repo()
        other = os.path.join(temp_dir(self), 'wt')
        git(d, 'worktree', 'add', '-q', '-b', 'card-12', other)
        r = run(['reviews', 'add', '--card', '12', '--round', '1', '--verdict', 'FAIL', '--findings',
                 self.findings(d, 'Done 3.1 | C1 | no screenshot\n')], other)
        self.assertEqual(r.code, 0, r.stderr)
        r = run(['reviews', 'add', '--card', '12', '--round', '2', '--verdict', 'PASS'], d)
        self.assertEqual(r.code, 0, r.stderr)
        shown = run(['reviews', 'show', '--card', '12'], d).lines
        self.assertEqual(run(['reviews', 'show', '--card', '12'], other).lines, shown)
        self.assertEqual([l.split(' — ')[1:] for l in shown if l.startswith('## ')], [['round 1', 'FAIL'], ['round 2', 'PASS']])
        self.assertTrue(os.path.exists(self.store(d, '12')))

    def test_add_validates_the_card_the_round_the_verdict_and_each_finding(self):
        d = self.repo()
        add = ['reviews', 'add', '--card', '12', '--round', '1', '--verdict', 'NOT DONE']
        self.assertEqual(run(add, d).code, 0)
        self.assertEqual(run(['reviews', 'add', '--card', '12', '--round', 'one', '--verdict', 'FAIL'], d).code, 2)
        self.assertEqual(run(['reviews', 'add', '--card', '12', '--round', '1', '--verdict', 'fail'], d).code, 2)
        self.assertEqual(run(['reviews', 'add', '--round', '1', '--verdict', 'FAIL'], d).code, 2)
        self.assertEqual(run(['reviews', 'add', '--card', '../12', '--round', '1', '--verdict', 'FAIL'], d).code, 2)
        r = run(['reviews', 'add', 'specs/12', '--card', '12', '--round', '1', '--verdict', 'FAIL'], d)
        self.assertEqual(r.code, 2)
        self.assertIn('takes no folder', r.stderr)
        for bad in ['Ready 3.2 | C1 | text', 'Done 9.9 | C1 | text', '4.3 | C1 | text', 'Done 4.3 | criterion 1 | text',
                    'Done 4.3 | C1 |', 'Done 4.3 the export is slow']:
            r = run(add + ['--findings', self.findings(d, bad + '\n')], d)
            self.assertEqual(r.code, 2, bad)
            self.assertIn('findings.txt line 1', r.stderr)
        self.assertEqual(len(re.findall(r'^## ', read(self.store(d, '12')), re.M)), 1)

    def test_outside_a_repository_is_a_usage_error(self):
        d = temp_dir(self)
        r = run(['reviews', 'show', '--card', '12'], d)
        self.assertEqual(r.code, 2)
        self.assertIn('not in a git repository', r.stderr)

    def test_ledger_files_the_blocks_under_the_card_heading_skips_those_already_there_and_removes_the_store(self):
        d = self.repo()
        ledger = os.path.join(d, '.devfactory', 'reviews.md')
        write(ledger, '# Reviews\r\n\r\n## #12\r\n\r\n### 2026-10-01 — round 1 — PASS\r\n\r\n## #13\r\n\r\n### 2026-10-02 — round 1 — PASS\r\n')
        add = lambda card, rnd, verdict, *more: run(['reviews', 'add', '--card', card, '--round', rnd, '--verdict', verdict] + list(more), d)
        add('12', '1', 'FAIL', '--findings', self.findings(d, 'Done 3.1 | C1 | no screenshot\n'))
        add('12', '2', 'PASS')
        r = run(['reviews', 'ledger', '--card', '12', '--ledger', ledger], d)
        self.assertEqual((r.code, r.lines), (0, ['appended 2 skipped 0']), r.stderr)
        text = read(ledger)
        self.assertRegex(text, r'^# Reviews\r\n\r\n## #12\r\n\r\n### 2026-10-01 — round 1 — PASS\r\n\r\n'
                               r'### \d{4}-\d{2}-\d{2} — round 1 — FAIL\r\n\r\n- Done 3\.1 \| C1 \| no screenshot\r\n\r\n'
                               r'### \d{4}-\d{2}-\d{2} — round 2 — PASS\r\n\r\n## #13\r\n')
        self.assertFalse(os.path.exists(self.store(d, '12')))
        self.assertEqual(run(['reviews', 'show', '--card', '12'], d).lines, ['no-reviews'])
        r = run(['reviews', 'ledger', '--card', '#12', '--ledger', ledger], d)
        self.assertEqual((r.code, r.lines), (0, ['appended 0 skipped 0']), r.stderr)
        self.assertEqual(read(ledger), text)
        add('12', '1', 'FAIL', '--findings', self.findings(d, 'Done 3.1 | C1 | no screenshot\n'))
        add('12', '2', 'PASS')
        r = run(['reviews', 'ledger', '--card', '#12', '--ledger', ledger], d)
        self.assertEqual(r.lines, ['appended 0 skipped 2'])
        self.assertEqual(read(ledger), text)
        add('14', '1', 'FAIL', '--findings', self.findings(d, 'Done 3.1 | C1 | no screenshot\n'))
        new = os.path.join(d, 'new.md')
        r = run(['reviews', 'ledger', '--card', '#14', '--ledger', new], d)
        self.assertEqual(r.lines, ['appended 1 skipped 0'])
        self.assertRegex(read(new), r'^## #14\n\n### \d{4}-\d{2}-\d{2} — round 1 — FAIL\n\n- Done 3\.1')

    def test_ledger_with_no_reviews_appends_nothing_and_a_malformed_record_fails_and_stays(self):
        d = self.repo()
        ledger = os.path.join(d, 'ledger.md')
        self.assertEqual(run(['reviews', 'ledger', '--card', '1', '--ledger', ledger], d).lines, ['appended 0 skipped 0'])
        write(self.store(d, '1'), '## round 1 FAIL\n\n- Done 3.1 | C1 | x\n')
        r = run(['reviews', 'ledger', '--card', '1', '--ledger', ledger], d)
        self.assertEqual(r.code, 1)
        self.assertEqual([l.split(' ')[0] for l in r.lines], ['reviews-parse'])
        self.assertFalse(os.path.exists(ledger))
        self.assertTrue(os.path.exists(self.store(d, '1')))


if __name__ == '__main__':
    unittest.main()
