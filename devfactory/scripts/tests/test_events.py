import os
import unittest

from .helpers import git, load_script, read, run, temp_dir, write


class EventTest(unittest.TestCase):
    def repo(self):
        d = temp_dir(self)
        git(d, 'init', '-q')
        return d

    def test_no_hook_does_nothing_and_succeeds(self):
        d = self.repo()
        r = run(['event', 'ready', '--card', '12'], d)
        self.assertEqual(r.code, 0)
        self.assertEqual(r.lines, ['no-hook ready'])

    def test_a_hook_runs_from_the_repository_root_with_the_card_and_event(self):
        d = self.repo()
        write(os.path.join(d, '.devfactory', 'hooks', 'ready.py'),
              'import os, sys\n'
              'open("seen.txt", "w").write("%s %s %s" % (sys.argv[1], os.environ["DEVFACTORY_EVENT"], os.environ["DEVFACTORY_CARD"]))\n'
              'print("moved")\n')
        os.makedirs(os.path.join(d, 'sub'))
        r = run(['event', 'ready', '--card', '12'], os.path.join(d, 'sub'))
        self.assertEqual(r.code, 0, r.stderr)
        self.assertEqual(r.lines, ['moved', 'ran ready.py'])
        self.assertEqual(read(os.path.join(d, 'seen.txt')), '12 ready 12')

    def test_a_failing_hook_reports_its_exit_and_fails(self):
        d = self.repo()
        write(os.path.join(d, '.devfactory', 'hooks', 'done.py'), 'import sys\nprint("no board")\nsys.exit(3)\n')
        r = run(['event', 'done', '--card', '7'], d)
        self.assertEqual(r.code, 1)
        self.assertEqual(r.lines, ['no board', 'hook-failed done.py exit 3'])

    def test_a_hook_for_another_event_is_not_run(self):
        d = self.repo()
        write(os.path.join(d, '.devfactory', 'hooks', 'ready-extra.py'), 'raise SystemExit(5)\n')
        self.assertEqual(run(['event', 'ready', '--card', '1'], d).lines, ['no-hook ready'])

    def test_every_event_is_accepted(self):
        d = self.repo()
        for name in ['request-met', 'ready', 'approved', 'work-started', 'development-started',
                     'readiness-lost', 'done', 'refused', 'accepted', 'released']:
            self.assertEqual(run(['event', name, '--card', '1'], d).lines, ['no-hook %s' % name])

    def test_the_hook_name_matches_without_regard_to_case(self):
        d = self.repo()
        write(os.path.join(d, '.devfactory', 'hooks', 'Ready.py'), 'print("ok")\n')
        self.assertEqual(run(['event', 'ready', '--card', '1'], d).lines, ['ok', 'ran Ready.py'])

    def test_a_hook_of_an_unknown_type_is_a_failed_hook(self):
        d = self.repo()
        write(os.path.join(d, '.devfactory', 'hooks', 'ready.txt'), 'move it\n')
        r = run(['event', 'ready', '--card', '1'], d)
        self.assertEqual(r.code, 1)
        self.assertRegex(r.lines[-1], r'^hook-failed ready\.txt could not start: no runner for "\.txt" files')

    @unittest.skipUnless(os.name == 'nt', 'cmd runs only on Windows')
    def test_a_cmd_hook_runs_with_the_card(self):
        d = self.repo()
        write(os.path.join(d, '.devfactory', 'hooks', 'done.cmd'), '@echo card %1\r\n')
        self.assertEqual(run(['event', 'done', '--card', '9'], d).lines, ['card 9', 'ran done.cmd'])

    def test_a_hook_past_its_time_is_stopped_and_fails(self):
        d = self.repo()
        write(os.path.join(d, '.devfactory', 'hooks', 'done.py'), 'import time\ntime.sleep(30)\n')
        script = load_script()
        script.EVENT_TIMEOUT_SECONDS = 1
        cwd = os.getcwd()
        os.chdir(d)
        self.addCleanup(os.chdir, cwd)
        out, code = script.cmd_event({'_': ['done'], 'card': '3'})
        self.assertEqual(code, 1)
        self.assertEqual(out, ['hook-failed done.py timed out after 1s'])

    def test_an_unknown_event_two_hooks_or_no_card_is_a_usage_error(self):
        d = self.repo()
        self.assertEqual(run(['event', 'moved', '--card', '1'], d).code, 2)
        self.assertEqual(run(['event', 'ready'], d).code, 2)
        write(os.path.join(d, '.devfactory', 'hooks', 'ready.py'), '')
        write(os.path.join(d, '.devfactory', 'hooks', 'ready.ps1'), '')
        r = run(['event', 'ready', '--card', '1'], d)
        self.assertEqual(r.code, 2)
        self.assertIn('more than one hook', r.stderr)


if __name__ == '__main__':
    unittest.main()
