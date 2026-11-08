import os
import unittest

from .helpers import assert_deny, bash, git, iso_ago, project, write

PROFILE = '\n'.join([
    '# Project profile: Example',
    '',
    '## Branches and merging',
    '- Integration branch: `main`',
    '- Worktree layout: `.worktrees/<branch>`',
    '- Parent branch: `parent-<N>`, cut from main',
    '- Sub-issue branch: `card-<N>`',
    '',
    '## Hooks',
    '- Git guard: on',
    '',
])


class GuardGitTest(unittest.TestCase):
    def run_guard(self, cwd, command):
        return bash(self, 'guard_git.py', cwd, command)

    def on(self, branch, markers=(), profile=PROFILE):
        return project(self, profile=profile, markers=markers, branch=branch)

    def deny(self, out, pattern=r'^DevFactory: '):
        assert_deny(self, out, pattern)

    def test_git_push_without_a_marker_is_denied(self):
        self.deny(self.run_guard(self.on('card-7'), 'git push origin card-7'), r'release skill')

    def test_git_push_with_a_release_or_coordinate_marker_is_allowed_silently(self):
        self.assertEqual(self.run_guard(self.on('main', ['release']), 'git push origin main'), '')
        self.assertEqual(self.run_guard(self.on('main', ['coordinate']), 'git push origin main'), '')

    def test_git_push_under_build_or_grill_is_denied(self):
        self.deny(self.run_guard(self.on('card-7', ['build']), 'git -C . push'), r'never pushes')
        self.deny(self.run_guard(self.on('main', ['grill']), 'git push'))

    def test_push_only_counts_as_the_command_token_not_as_a_word_in_another_argument(self):
        cwd = self.on('card-7')
        self.assertEqual(self.run_guard(cwd, 'git log --grep=push && echo git push'), '')
        self.assertEqual(self.run_guard(cwd, 'git commit -m "then git push; done"'), '')
        self.deny(self.run_guard(cwd, 'git status && git push'))
        self.deny(self.run_guard(cwd, 'FOO=1 git -c core.x=y push'))

    def test_merging_or_rebasing_a_protected_branch_into_a_feature_branch_is_allowed(self):
        cwd = self.on('card-7')
        self.assertEqual(self.run_guard(cwd, 'git merge main'), '')
        self.assertEqual(self.run_guard(cwd, 'git rebase main'), '')
        self.assertEqual(self.run_guard(cwd, 'git rebase --onto parent-12 main'), '')
        self.assertEqual(self.run_guard(cwd, 'git reset --hard origin/main'), '')

    def test_merge_rebase_reset_hard_and_commit_amend_on_the_integration_branch_are_denied(self):
        cwd = self.on('main')
        for c in ['git merge card-7', 'git merge --ff-only card-7', 'git rebase card-7',
                  'git reset --hard HEAD~1', 'git commit --amend --no-edit']:
            with self.subTest(command=c):
                self.deny(self.run_guard(cwd, c), r'integration branch')
        self.assertEqual(self.run_guard(cwd, 'git commit -m "a commit"'), '')
        self.assertEqual(self.run_guard(cwd, 'git reset --soft HEAD'), '')
        self.assertEqual(self.run_guard(cwd, 'git merge --abort'), '')

    def test_a_rebase_that_names_a_protected_branch_to_rebase_is_denied(self):
        self.deny(self.run_guard(self.on('card-7'), 'git rebase card-7 main'))

    def test_the_effective_directory_is_followed_through_git_c_and_cd(self):
        session = self.on('card-7')
        target = self.on('parent-12')
        self.deny(self.run_guard(session, 'git -C "%s" merge card-7' % target), r'parent branch')
        self.deny(self.run_guard(session, 'cd "%s" && git merge card-7' % target), r'parent branch')
        self.assertEqual(self.run_guard(target, 'git -C "%s" merge parent-12' % session), '')

    def test_build_may_fast_forward_a_parent_branch_also_from_its_own_worktree_but_nothing_else(self):
        session = self.on('card-7', ['build'])
        parent = self.on('parent-12')
        self.assertEqual(self.run_guard(session, 'git -C "%s" merge --ff-only card-7' % parent), '')
        self.assertEqual(self.run_guard(self.on('parent-12', ['build']), 'git merge --ff-only card-7'), '')
        self.deny(self.run_guard(session, 'git -C "%s" merge card-7' % parent))
        self.deny(self.run_guard(self.on('main', ['build']), 'git merge --ff-only card-7'))
        self.deny(self.run_guard(self.on('parent-12', ['build']), 'git reset --hard HEAD'))

    def test_grill_may_only_commit_or_fast_forward_onto_the_integration_branch(self):
        cwd = self.on('main', ['grill'])
        self.assertEqual(self.run_guard(cwd, 'git commit -m "spec for #12"'), '')
        self.assertEqual(self.run_guard(cwd, 'git merge --ff-only spec-12'), '')
        for c in ['git merge spec-12', 'git merge --no-ff spec-12', 'git commit --amend --no-edit',
                  'git reset --hard HEAD~1', 'git rebase card-7', 'git pull --ff-only', 'git cherry-pick abc1234']:
            with self.subTest(command=c):
                self.deny(self.run_guard(cwd, c), r'grill may only commit its spec')
        self.deny(self.run_guard(self.on('parent-12', ['grill']), 'git merge --ff-only spec-12'))

    def test_card_skills_may_fast_forward_a_receipt_onto_the_integration_branch(self):
        for skill in ['create-card', 're-evaluate-card']:
            with self.subTest(skill=skill):
                cwd = self.on('main', [skill])
                self.assertEqual(self.run_guard(cwd, 'git merge --ff-only receipt-12'), '')
                self.deny(self.run_guard(cwd, 'git merge receipt-12'))

    def test_git_pull_onto_a_protected_branch_is_denied_onto_a_feature_branch_allowed(self):
        cwd = self.on('main')
        for c in ['git pull', 'git pull origin main', 'git pull --ff-only', 'git pull --rebase',
                  'git pull -r origin main', 'git pull --rebase=merges']:
            with self.subTest(command=c):
                self.deny(self.run_guard(cwd, c), r'integration branch')
        self.deny(self.run_guard(cwd, 'git pull --no-rebase'), r'git pull changes main')
        self.deny(self.run_guard(cwd, 'git pull -r'), r'git pull --rebase changes main')
        self.deny(self.run_guard(self.on('parent-12'), 'git pull'), r'parent branch')
        self.assertEqual(self.run_guard(self.on('card-7'), 'git pull origin main'), '')
        self.assertEqual(self.run_guard(self.on('card-7'), 'git pull --rebase origin parent-12'), '')

    def test_git_cherry_pick_onto_a_protected_branch_is_denied_its_abort_allowed(self):
        cwd = self.on('main')
        self.deny(self.run_guard(cwd, 'git cherry-pick abc1234'), r'cherry-pick changes main')
        self.deny(self.run_guard(cwd, 'git cherry-pick -x -m 1 abc1234'))
        self.deny(self.run_guard(cwd, 'git cherry-pick --continue'))
        self.assertEqual(self.run_guard(cwd, 'git cherry-pick --abort'), '')
        self.assertEqual(self.run_guard(self.on('card-7'), 'git cherry-pick abc1234'), '')

    def test_git_branch_f_that_moves_a_protected_branch_is_denied_wherever_head_is(self):
        cwd = self.on('card-7')
        self.deny(self.run_guard(cwd, 'git branch -f main card-7'), r'branch -f changes main, the integration branch')
        self.deny(self.run_guard(cwd, 'git branch --force parent-12 HEAD'), r'parent branch')
        self.assertEqual(self.run_guard(cwd, 'git branch -f card-8 main'), '')
        self.assertEqual(self.run_guard(cwd, 'git branch card-9 main'), '')
        self.assertEqual(self.run_guard(self.on('main'), 'git branch --list'), '')
        self.deny(self.run_guard(self.on('card-7', ['build']), 'git branch -f parent-12 card-7'))
        self.assertEqual(self.run_guard(self.on('card-7', ['coordinate']), 'git branch -f main card-7'), '')

    def test_release_or_coordinate_allows_changing_a_protected_branch(self):
        self.assertEqual(self.run_guard(self.on('main', ['coordinate']), 'git reset --hard HEAD'), '')
        self.assertEqual(self.run_guard(self.on('main', ['release']), 'git merge --ff-only card-7'), '')

    def test_a_marker_older_than_the_marker_lifetime_is_ignored(self):
        self.deny(self.run_guard(self.on('main', [('release', 13)]), 'git push'))
        longer = PROFILE.replace('- Git guard: on', '- Git guard: on\n- Marker lifetime: 48h')
        self.assertEqual(self.run_guard(self.on('main', [('release', 13)], longer), 'git push'), '')

    def test_the_profile_is_read_at_the_repository_root_when_cwd_is_a_subfolder(self):
        cwd = self.on('main')
        sub = os.path.join(cwd, 'src', 'deep')
        os.makedirs(sub)
        self.deny(self.run_guard(sub, 'git merge card-7'))

    def test_the_bold_profile_field_forms_are_read(self):
        bold = (PROFILE.replace('- Integration branch: `main`', '- **Integration branch:** `trunk`')
                .replace('- Parent branch: `parent-<N>`, cut from main', '* **Parent branch**: `epic-<N>`'))
        self.deny(self.run_guard(self.on('trunk', [], bold), 'git merge card-7'), r'trunk')
        self.deny(self.run_guard(self.on('epic-4', [], bold), 'git merge card-7'), r'epic-4')
        self.assertEqual(self.run_guard(self.on('main', [], bold), 'git merge card-7'), '')

    def test_no_profile_or_git_guard_off_means_silence(self):
        self.assertEqual(self.run_guard(project(self, branch='main'), 'git push'), '')
        off = PROFILE.replace('- Git guard: on', '- Git guard: off')
        self.assertEqual(self.run_guard(self.on('main', [], off), 'git push'), '')

    def test_a_worktree_root_is_its_own_project_root(self):
        main = self.on('main')
        write(os.path.join(main, '.gitignore'), '.devfactory/.active/\n')
        git(main, 'add', '.')
        git(main, 'commit', '-q', '-m', 'profile')
        wt = os.path.join(main, '.worktrees', 'parent-12')
        git(main, 'worktree', 'add', '-q', '-b', 'parent-12', wt)
        self.deny(self.run_guard(wt, 'git merge card-7'), r'parent-12')
        os.makedirs(os.path.join(wt, '.devfactory', '.active'), exist_ok=True)
        write(os.path.join(wt, '.devfactory', '.active', 'build'), iso_ago(0))
        self.assertEqual(self.run_guard(wt, 'git merge --ff-only card-7'), '')
        self.deny(self.run_guard(main, 'git merge --ff-only card-7'))


if __name__ == '__main__':
    unittest.main()
