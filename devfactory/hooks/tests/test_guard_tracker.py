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


CARD_WRITERS = ['create-card', 'add-to-card', 're-evaluate-card', 'grill', 'check-ready', 'build',
                'coordinate', 'accept', 'release', 'configure-project']


class GuardTrackerTest(unittest.TestCase):
    def run_guard(self, cwd, command, tool='Bash'):
        return bash(self, 'guard_tracker.py', cwd, command, tool)

    def denied(self, out):
        assert_deny(self, out, r'card skills')

    def test_the_powershell_tool_is_guarded_as_bash_is(self):
        cwd = project(self, profile=PROFILE)
        for c in ['gh issue edit 12 --title x', 'gh issue view 12; gh issue comment 12 -b hi',
                  'gh issue view 12\ngh issue close 12', "gh api -X PATCH 'repos/o/r/issues/12' -f state=closed",
                  'az rest --method patch --url https://dev.azure.com/o/p/_apis/wit/workitems/1']:
            with self.subTest(command=c):
                self.denied(self.run_guard(cwd, c, 'PowerShell'))
        self.assertEqual(self.run_guard(cwd, 'gh issue view 12 --json title', 'PowerShell'), '')
        marked = project(self, profile=PROFILE, markers=['add-to-card'])
        self.assertEqual(self.run_guard(marked, 'gh issue edit 12 --title x', 'PowerShell'), '')

    def test_a_card_writer_begun_earlier_in_the_same_command_allows_the_write(self):
        cwd = project(self, profile=PROFILE)
        for c, tool in [
            ('devfactory begin add-to-card && gh issue edit 12 --title x', 'Bash'),
            ('python "C:/Program Files/plugin/scripts/devfactory.py" begin grill; gh issue comment 12 -b x', 'Bash'),
            ("python3 -I '/c/plugin/scripts/devfactory.py' begin accept\ngh issue edit 12 -b x", 'Bash'),
            ('python "${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py" begin release 2>&1 && gh issue close 12', 'Bash'),
            ('python $env:CLAUDE_PLUGIN_ROOT\\scripts\\devfactory.py begin grill; gh issue edit 12 -b x', 'PowerShell'),
            ('& python "C:\\plugin\\scripts\\devfactory.py" begin create-card\ngh issue create -t x -b y', 'PowerShell'),
        ]:
            with self.subTest(command=c):
                self.assertEqual(self.run_guard(cwd, c, tool), '')

    def test_a_begin_after_the_write_after_a_failure_join_or_of_another_skill_does_not_count(self):
        cwd = project(self, profile=PROFILE)
        for c in ['gh issue edit 12 -b x && devfactory begin grill',
                  'devfactory begin grill || gh issue edit 12 -b x',
                  'devfactory begin grill | gh issue edit 12 -b x',
                  'devfactory begin curate && gh issue edit 12 -b x',
                  'devfactory begin start && gh issue edit 12 -b x',
                  'python other.py begin grill && gh issue edit 12 -b x',
                  'echo devfactory begin grill && gh issue edit 12 -b x']:
            with self.subTest(command=c):
                self.denied(self.run_guard(cwd, c))

    def test_every_issue_project_label_and_work_item_command_but_a_known_read_is_a_write(self):
        cwd = project(self, profile=PROFILE)
        for c in ['gh issue close 12', 'gh issue reopen 12', 'gh issue delete 12 --yes',
                  'gh issue develop 12', 'gh issue transfer 12 o/s', 'gh issue lock 12', 'gh issue pin 12',
                  'gh issue -R o/r edit 12 -b x', 'gh issue --repo o/r close 12',
                  'gh project item-delete 1 --id x', 'gh project item-archive 1 --id x',
                  'gh project item-create 1 --title x', 'gh project field-create 1 --name x',
                  'gh project edit 1 --title x', 'gh project create --title x', 'gh project link 1',
                  'gh label create bug', 'gh label edit bug -c red', 'gh label delete bug --yes',
                  'gh label clone o/s', 'az boards work-item delete --id 1 --yes',
                  'az boards work-item relation add --id 1 --relation-type parent --target-id 2',
                  'bash -c "gh issue close 12"', "powershell -Command 'gh label create x'"]:
            with self.subTest(command=c):
                self.denied(self.run_guard(cwd, c))

    def test_the_known_reads_and_other_gh_and_az_areas_are_allowed_silently(self):
        cwd = project(self, profile=PROFILE)
        for c in ['gh issue view 12', 'gh issue list --state open', 'gh issue status',
                  'gh issue -R o/r view 12', 'gh issue edit --help',
                  'gh project view 1 --owner o', 'gh project list --owner o --format json',
                  'gh project item-list 1 --owner o', 'gh project field-list 1 --owner o',
                  'gh label list', 'az boards work-item show --id 1',
                  'az boards work-item relation show --id 1', 'az boards query --wiql "select 1"',
                  'az boards iteration project list',
                  'gh pr create --fill', 'gh pr merge 3', 'gh run list', 'gh workflow run ci.yml',
                  'gh variable set X', 'gh repo view', 'gh auth status', 'gh release create v1',
                  'az pipelines run --name x', 'az repos pr create', 'az devops configure -d x=y']:
            with self.subTest(command=c):
                self.assertEqual(self.run_guard(cwd, c), '')

    def test_az_rest_is_a_write_only_when_not_a_get_against_a_work_item_api(self):
        cwd = project(self, profile=PROFILE)
        wit = 'https://dev.azure.com/o/p/_apis/wit/workitems/1?api-version=7.1'
        for c in ['az rest --method patch --url "%s" --body @patch.json' % wit,
                  'az rest -m POST --uri https://dev.azure.com/o/p/_apis/wit/attachments?fileName=a.png',
                  'az rest --method=delete --url=%s' % wit,
                  'az rest --method post --url "$url"']:
            with self.subTest(command=c):
                self.denied(self.run_guard(cwd, c))
        for c in ['az rest --url "%s"' % wit, 'az rest --method get --url "%s"' % wit,
                  'az rest -m GET -u "$url"',
                  'az rest --method post --url https://management.azure.com/subscriptions/x/providers?api-version=1',
                  'az rest --method patch --url https://dev.azure.com/o/p/_apis/pipelines/1']:
            with self.subTest(command=c):
                self.assertEqual(self.run_guard(cwd, c), '')
        self.assertEqual(self.run_guard(project(self, profile=PROFILE, markers=['grill']),
                                        'az rest --method patch --url "%s"' % wit), '')

    def test_every_card_writing_skill_marker_allows_a_write_and_no_other_does(self):
        for skill in CARD_WRITERS:
            with self.subTest(skill=skill):
                self.assertEqual(self.run_guard(project(self, profile=PROFILE, markers=[skill]),
                                                'gh issue close 12'), '')
        for skill in ['curate', 'start']:
            with self.subTest(skill=skill):
                cwd = project(self, profile=PROFILE, markers=[skill])
                self.denied(self.run_guard(cwd, 'gh issue close 12'))
                self.assertEqual(self.run_guard(cwd, 'gh issue view 12'), '')

    def test_gh_issue_edit_without_a_marker_is_denied(self):
        self.denied(self.run_guard(project(self, profile=PROFILE), 'gh issue edit 12 --body-file body.md'))

    def test_gh_issue_edit_with_a_marker_is_allowed_silently(self):
        self.assertEqual(self.run_guard(project(self, profile=PROFILE, markers=['add-to-card']), 'gh issue edit 12 --add-label x'), '')

    def test_a_stale_marker_does_not_count(self):
        self.denied(self.run_guard(project(self, profile=PROFILE, markers=[('add-to-card', 13)]), 'gh issue comment 12 --body x'))

    def test_only_a_card_writing_skill_marker_unlocks_a_write(self):
        self.denied(self.run_guard(project(self, profile=PROFILE, markers=['curate']), 'gh issue comment 1 -b hi'))
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
