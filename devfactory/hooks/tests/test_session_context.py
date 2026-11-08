import os
import unittest

from .helpers import project, run_hook

PROFILE = '\n'.join([
    '# Project profile: Example',
    '',
    '## Hooks',
    '- Session context: on',
    '',
])


class SessionContextTest(unittest.TestCase):
    def run_context(self, cwd):
        return run_hook(self, 'session_context.py', {'session_id': 'test', 'cwd': cwd,
                                                     'hook_event_name': 'SessionStart', 'source': 'startup'})

    def test_prints_the_profile_hooks_skills_decision_line_and_markers_in_under_25_lines(self):
        cwd = project(self, profile=PROFILE)
        lines = self.run_context(cwd).rstrip().split('\n')
        self.assertLess(len(lines), 25, '%d lines' % len(lines))
        self.assertEqual(lines[0], 'DevFactory profile: %s' % os.path.join(cwd, '.devfactory', 'profile.md'))
        self.assertEqual(lines[1], 'Event hooks: none in .devfactory/hooks/; the plugin moves no card on the board.')
        self.assertTrue(any('create-card / add-to-card / re-evaluate-card' in l for l in lines))
        self.assertTrue(any(l.startswith('Decision line: the requester decides') for l in lines))
        self.assertRegex(lines[-1], r'No card skill is running')

    def test_names_the_event_hooks_the_project_has(self):
        cwd = project(self, profile=PROFILE)
        hooks = os.path.join(cwd, '.devfactory', 'hooks')
        os.makedirs(hooks)
        for name in ['ready.ps1', 'done.py']:
            open(os.path.join(hooks, name), 'w').close()
        lines = self.run_context(cwd).rstrip().split('\n')
        self.assertEqual(lines[1], 'Event hooks in .devfactory/hooks/: done.py, ready.ps1.')

    def test_names_an_active_marker_and_reports_a_stale_one(self):
        out = self.run_context(project(self, profile=PROFILE, markers=['grill', ('build', 30)]))
        self.assertRegex(out, r'Active card skill markers: grill \(\d+s\)\.')
        self.assertRegex(out, r'Stale markers, which the guards ignore: build \(1d\); clear them')

    def test_reads_the_profile_at_the_repository_root_from_a_subfolder(self):
        cwd = project(self, profile=PROFILE, branch='main')
        sub = os.path.join(cwd, 'src')
        os.mkdir(sub)
        self.assertRegex(self.run_context(sub), r'^DevFactory profile: ')

    def test_no_profile_means_silence(self):
        self.assertEqual(self.run_context(project(self, profile=None)), '')

    def test_session_context_off_means_silence(self):
        off = PROFILE.replace('- Session context: on', '- Session context: off')
        self.assertEqual(self.run_context(project(self, profile=off)), '')


if __name__ == '__main__':
    unittest.main()
