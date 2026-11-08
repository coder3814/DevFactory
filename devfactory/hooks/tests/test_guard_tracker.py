import os
import subprocess
import sys
import unittest

from .helpers import HOOKS, assert_deny, bash, project

PROFILE = '\n'.join([
    '# Project profile: Example',
    '',
    '## Tracker',
    '- Binding: github-projects',
    '',
    '## Hooks',
    '- Tracker guard: on',
    '- Git guard: on',
    '',
])


class GuardTrackerTest(unittest.TestCase):
    def run_guard(self, cwd, command):
        return bash(self, 'guard_tracker.py', cwd, command)

    def denied(self, out):
        assert_deny(self, out, r'card skills')

    def test_gh_issue_edit_without_a_marker_is_denied(self):
        self.denied(self.run_guard(project(self, profile=PROFILE), 'gh issue edit 12 --body-file body.md'))

    def test_gh_issue_edit_with_a_marker_is_allowed_silently(self):
        self.assertEqual(self.run_guard(project(self, profile=PROFILE, markers=['add-to-card']), 'gh issue edit 12 --add-label x'), '')

    def test_a_stale_marker_does_not_count(self):
        self.denied(self.run_guard(project(self, profile=PROFILE, markers=[('add-to-card', 13)]), 'gh issue comment 12 --body x'))

    def test_only_a_card_writing_skill_marker_unlocks_a_write(self):
        self.denied(self.run_guard(project(self, profile=PROFILE, markers=['configure-project']), 'gh issue comment 1 -b hi'))
        self.assertEqual(self.run_guard(project(self, profile=PROFILE, markers=['add-to-card']), 'gh issue comment 1 -b hi'), '')

    def test_gh_issue_view_and_a_mention_inside_another_command_are_allowed_silently(self):
        cwd = project(self, profile=PROFILE)
        self.assertEqual(self.run_guard(cwd, 'gh issue view 12 --json title,body'), '')
        self.assertEqual(self.run_guard(cwd, 'echo "gh issue edit 12"'), '')

    def test_no_profile_means_silence(self):
        self.assertEqual(self.run_guard(project(self, profile=None), 'gh issue edit 12 --title x'), '')

    def test_tracker_guard_off_means_silence(self):
        off = PROFILE.replace('- Tracker guard: on', '- Tracker guard: off')
        self.assertEqual(self.run_guard(project(self, profile=off), 'gh issue comment 12 --body x'), '')

    def test_gh_api_writes_are_denied_without_a_marker(self):
        cwd = project(self, profile=PROFILE)
        for c in [
            'gh api -X PATCH repos/o/r/issues/12 -f state=closed',
            'gh api --method=DELETE repos/o/r/labels/x',
            'gh api -XPOST repos/o/r/issues/12/comments',
            'gh api repos/o/r/issues/12/comments -f body=hello',
            'gh api repos/o/r/issues -F title=x',
            'gh api repos/o/r/issues/12 --input patch.json',
            "gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: {}) { clientMutationId } }'",
            'gh api graphql --input query.json',
        ]:
            with self.subTest(command=c):
                self.denied(self.run_guard(cwd, c))

    def test_a_gh_api_graphql_call_whose_query_or_variables_come_from_a_file_is_denied(self):
        cwd = project(self, profile=PROFILE)
        for c in [
            'gh api graphql -F query=@query.graphql',
            'gh api graphql -f query=@query.graphql',
            'gh api graphql -Fquery=@query.graphql',
            'gh api graphql --field=query=@query.graphql',
            'gh api graphql --raw-field query=@-',
            "gh api graphql -f query='query($n: Int!) { viewer { login } }' -F vars=@vars.json",
            'gh api graphql --input=query.json',
        ]:
            with self.subTest(command=c):
                self.denied(self.run_guard(cwd, c))
        self.assertEqual(self.run_guard(project(self, profile=PROFILE, markers=['grill']), 'gh api graphql -F query=@q.graphql'), '')

    def test_gh_api_reads_are_allowed_silently(self):
        cwd = project(self, profile=PROFILE)
        for c in [
            'gh api repos/o/r/issues/12',
            'gh api -X GET search/issues -f q=repo:o/r',
            'gh api --method GET repos/o/r/issues -F per_page=100',
            "gh api graphql -f query='query { viewer { login } }'",
            "gh api graphql -F owner=o -f query='query($owner: String!) { user(login: $owner) { email } }'",
            'gh api repos/o/r/issues --paginate --jq ".[].title"',
        ]:
            self.assertEqual(self.run_guard(cwd, c), '', c)

    def test_malformed_input_is_silence(self):
        r = subprocess.run([sys.executable, os.path.join(HOOKS, 'guard_tracker.py')], input=b'not json',
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, b'')


if __name__ == '__main__':
    unittest.main()
