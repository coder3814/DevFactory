import datetime
import os
import unittest

from . import helpers
from .helpers import git, iso_ago, parse_iso, read, run, temp_dir, write

devfactory = helpers.load_script()

PROFILE = '\n'.join([
    '# Project profile: Example',
    '',
    '## Specs',
    '- Path: `specs/`',
    '',
    '## Branches and merging',
    '* Integration branch: `main`',
    '- **Parent branch:** `parent-<N>`, cut from main',
    '- **Sub-issue branch**: `card-<N>`',
    '',
    '## Environments',
    '### Local',
    '- Can show: everything',
    '',
    '## Hooks',
    '- Git guard: on',
    '',
    '## Standing answers',
    '- **Which log format?** JSON lines: decided in review',
    '',
])


def marker(root, name, age_hours):
    write(os.path.join(root, '.devfactory', '.active', name), iso_ago(age_hours) + '\n')


class MarkersProfileTest(unittest.TestCase):
    def test_the_field_parser_reads_the_four_forms_and_nothing_else(self):
        f = devfactory.profile_field_line
        self.assertEqual(f('- Name: value'), {'name': 'Name', 'value': 'value'})
        self.assertEqual(f('* Name: a: b'), {'name': 'Name', 'value': 'a: b'})
        self.assertEqual(f('- **Name:** value'), {'name': 'Name', 'value': 'value'})
        self.assertEqual(f('- **Name**: value'), {'name': 'Name', 'value': 'value'})
        self.assertIsNone(f('- **Which log format?** JSON lines: decided'))
        self.assertIsNone(f('| Stage | Column |'))

    def test_profile_reads_a_field_in_each_form_within_a_section(self):
        d = temp_dir(self)
        write(os.path.join(d, '.devfactory', 'profile.md'), PROFILE.replace('\n', '\r\n'))

        def field(section, name):
            return run(['profile', '--section', section, '--field', name], d)
        self.assertEqual(field('Branches and merging', 'Integration branch').lines, ['`main`'])
        self.assertEqual(field('Branches and merging', 'parent branch').lines, ['`parent-<N>`, cut from main'])
        self.assertEqual(field('Branches and merging', 'Sub-issue branch').lines, ['`card-<N>`'])
        self.assertEqual(field('Environments', 'Can show').lines, ['everything'])
        self.assertEqual(field('Specs', 'Integration branch').code, 2)
        self.assertEqual(field('Nowhere', 'Path').code, 2)

    def test_profile_section_alone_prints_that_section_only(self):
        d = temp_dir(self)
        write(os.path.join(d, '.devfactory', 'profile.md'), PROFILE)
        r = run(['profile', '--section', 'Environments'], d)
        self.assertEqual(r.code, 0, r.stderr)
        self.assertEqual(r.lines, ['### Local', '- Can show: everything'])

    def test_profile_begin_and_markers_use_the_repository_root_from_a_subfolder(self):
        d = temp_dir(self)
        git(d, 'init', '-q')
        write(os.path.join(d, '.devfactory', 'profile.md'), PROFILE)
        sub = os.path.join(d, 'src', 'deep')
        os.makedirs(sub)
        self.assertEqual(run(['profile', '--section', 'Specs', '--field', 'Path'], sub).lines, ['`specs/`'])
        self.assertEqual(run(['begin', 'build'], sub).code, 0)
        self.assertTrue(os.path.exists(os.path.join(d, '.devfactory', '.active', 'build')))
        self.assertFalse(os.path.exists(os.path.join(sub, '.devfactory')))

    def test_begin_refreshes_its_own_marker_and_reports_a_stale_one(self):
        d = temp_dir(self)
        write(os.path.join(d, '.devfactory', 'profile.md'), PROFILE)
        marker(d, 'grill', 20)
        marker(d, 'build', 1)
        r = run(['begin', 'grill'], d)
        self.assertEqual(r.code, 0, r.stderr)
        self.assertRegex(r.lines[0], r'^active build since \S+ \(1h ago\)$')
        self.assertRegex(r.lines[1], r'^refreshed grill \(was 20h old, stale\)$')
        stamp = parse_iso(read(os.path.join(d, '.devfactory', '.active', 'grill')))
        self.assertLess((datetime.datetime.now(datetime.timezone.utc) - stamp).total_seconds(), 60)

        marker(d, 'coordinate', 13)
        r = run(['begin', 'build'], d)
        self.assertRegex(r.lines[1], r'^stale coordinate since \S+ \(13h ago, older than 12h; the guards ignore it\)$')

    def test_markers_lists_each_with_its_age_honours_the_lifetime_and_clears_the_stale_ones(self):
        d = temp_dir(self)
        write(os.path.join(d, '.devfactory', 'profile.md'), PROFILE.replace('- Git guard: on', '- Git guard: on\n- Marker lifetime: 2h'))
        marker(d, 'build', 1)
        marker(d, 'grill', 3)
        r = run(['markers'], d)
        self.assertEqual(r.code, 0, r.stderr)
        self.assertRegex(r.lines[0], r'^active build since \S+ \(1h ago\)$')
        self.assertRegex(r.lines[1], r'^stale grill since \S+ \(3h ago, older than 2h; the guards ignore it\)$')
        r = run(['markers', '--clear-stale'], d)
        self.assertEqual(r.code, 0)
        self.assertRegex(r.lines[1], r'^cleared grill \(3h old\)$')
        self.assertEqual(os.listdir(os.path.join(d, '.devfactory', '.active')), ['build'])


if __name__ == '__main__':
    unittest.main()
