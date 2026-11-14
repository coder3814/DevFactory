import base64
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
    def run_guard(self, cwd, command, tool='Bash'):
        return bash(self, 'guard_git.py', cwd, command, tool)

    def on(self, branch, markers=(), profile=PROFILE):
        return project(self, profile=profile, markers=markers, branch=branch)

    def deny(self, out, pattern=r'^DevFactory: '):
        assert_deny(self, out, pattern)

    def with_history(self, branch, markers=(), others=('card-7',)):
        """A repository on branch with two commits and the other branches at its first."""
        cwd = self.on(branch, markers)
        for b in others:
            git(cwd, 'branch', b)
        git(cwd, 'commit', '-q', '--allow-empty', '-m', 'two')
        return cwd

    def test_the_powershell_tool_is_guarded_with_its_own_quoting_and_separators(self):
        session = self.on('card-7')
        target = self.on('main')
        self.deny(self.run_guard(self.on('card-7', ['grill']), 'git push origin card-7', 'PowerShell'),
                  r'release skill')
        for c in ['cd %s; git merge card-7' % target, 'Set-Location -Path "%s"\ngit merge card-7' % target,
                  "git -C '%s' merge --ff-only card-7" % target, 'git status; git -C %s reset --hard' % target,
                  'if ($true) { git -C %s merge card-7 }' % target]:
            with self.subTest(command=c):
                self.deny(self.run_guard(session, c, 'PowerShell'), r'integration branch')
        self.assertEqual(self.run_guard(session, 'git log --oneline; git status', 'PowerShell'), '')
        self.assertEqual(self.run_guard(target, "git commit -m 'it''s done; git push'", 'PowerShell'), '')
        self.assertEqual(self.run_guard(target, 'git commit -m "say `"hi`"; git push"', 'PowerShell'), '')

    def test_a_skill_begun_earlier_in_the_same_command_counts_as_its_fresh_marker(self):
        cwd = self.on('main')
        for c, tool in [
            ('devfactory begin release && git push origin main', 'Bash'),
            ('python "C:/plugin dir/scripts/devfactory.py" begin coordinate; git reset --hard HEAD', 'Bash'),
            ('python /c/plugin/scripts/devfactory.py begin grill\ngit merge --ff-only spec-12', 'Bash'),
            ('python $env:CLAUDE_PLUGIN_ROOT\\scripts\\devfactory.py begin curate; git merge --ff-only x', 'PowerShell'),
        ]:
            with self.subTest(command=c):
                self.assertEqual(self.run_guard(cwd, c, tool), '')
        for c in ['git merge card-7 && devfactory begin release',
                  'devfactory begin release || git merge card-7',
                  'devfactory begin build && git push',
                  'devfactory begin grill && git merge spec-12']:
            with self.subTest(command=c):
                self.deny(self.run_guard(cwd, c))

    def test_update_ref_of_a_protected_branch_or_of_head_on_one_is_denied(self):
        card = self.with_history('card-7', others=('main', 'parent-12'))
        self.deny(self.run_guard(card, 'git update-ref refs/heads/main HEAD'), r'update-ref changes main')
        self.deny(self.run_guard(card, 'git update-ref -d refs/heads/parent-12'), r'parent branch')
        self.deny(self.run_guard(card, 'git update-ref -m x refs/heads/main abc1234'), r'integration branch')
        self.deny(self.run_guard(card, 'git update-ref --stdin'), r'stdin')
        self.assertEqual(self.run_guard(card, 'git update-ref refs/heads/card-8 HEAD'), '')
        self.assertEqual(self.run_guard(card, 'git update-ref HEAD HEAD~1'), '')
        main = self.with_history('main')
        self.deny(self.run_guard(main, 'git update-ref HEAD HEAD~1'), r'integration branch')
        self.assertEqual(self.run_guard(main, 'git update-ref --no-deref HEAD HEAD~1'), '')
        self.assertEqual(self.run_guard(self.on('main', ['release']), 'git update-ref refs/heads/main HEAD'), '')

    def test_a_reset_to_another_revision_in_any_mode_is_denied_one_that_moves_no_branch_allowed(self):
        cwd = self.with_history('main')
        for c in ['git reset HEAD~1', 'git reset --soft HEAD~1', 'git reset --mixed card-7',
                  'git reset --keep HEAD~1', 'git reset --merge card-7', 'git reset -q HEAD~1']:
            with self.subTest(command=c):
                self.deny(self.run_guard(cwd, c), r'reset.* changes main, the integration branch')
        for c in ['git reset', 'git reset HEAD', 'git reset --soft HEAD', 'git reset main', 'git reset -- a.txt',
                  'git reset HEAD~1 -- a.txt', 'git reset HEAD~1 a.txt', 'git reset a.txt', 'git reset -p HEAD~1',
                  'git reset --keep']:
            with self.subTest(command=c):
                self.assertEqual(self.run_guard(cwd, c), '')
        self.assertEqual(self.run_guard(self.with_history('card-7', others=('main',)), 'git reset --soft HEAD~1'), '')

    def test_checkout_b_and_switch_c_of_a_protected_branch_are_denied(self):
        cwd = self.with_history('card-7', others=('main', 'parent-12'))
        for c in ['git checkout -B main', 'git checkout -B main card-7', 'git switch -C parent-12 card-7',
                  'git switch --force-create=main']:
            with self.subTest(command=c):
                self.deny(self.run_guard(cwd, c))
        for c in ['git checkout -B card-8', 'git switch -C card-8 main', 'git checkout -b card-9 main',
                  'git switch -c card-9']:
            with self.subTest(command=c):
                self.assertEqual(self.run_guard(cwd, c), '')

    def test_branch_rename_or_delete_of_a_protected_branch_is_denied(self):
        cwd = self.with_history('card-7', others=('main', 'parent-12', 'card-8'))
        for c in ['git branch -m main old-main', 'git branch -M parent-12 parent-13', 'git branch -d main',
                  'git branch -D card-8 parent-12', 'git branch --delete main', 'git branch --move main x',
                  'git branch -M card-8 main', 'git branch -C card-8 main']:
            with self.subTest(command=c):
                self.deny(self.run_guard(cwd, c))
        for c in ['git branch -m card-8 card-10', 'git branch -m card-11', 'git branch -d card-8',
                  'git branch -c card-8 card-12', 'git branch -m card-8 main-copy']:
            with self.subTest(command=c):
                self.assertEqual(self.run_guard(cwd, c), '')
        self.deny(self.run_guard(self.on('main'), 'git branch -m trunk'), r'branch -m changes main')
        self.assertEqual(self.run_guard(self.on('main', ['coordinate']), 'git branch -D main'), '')

    def test_a_git_command_inside_another_shell_is_judged(self):
        cwd = self.on('main')
        encoded = base64.b64encode('git merge card-7'.encode('utf-16-le')).decode('ascii')
        for c in ['bash -c "git merge card-7"', "sh -c 'git merge card-7'", 'bash -lc "cd . && git reset --hard"',
                  'powershell -Command "git merge card-7"', 'pwsh -NoProfile -c git merge card-7',
                  'powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "git commit --amend --no-edit"',
                  'powershell -EncodedCommand %s' % encoded, 'powershell -enc %s' % encoded,
                  'bash -c "bash -c \'git merge card-7\'"']:
            with self.subTest(command=c):
                self.deny(self.run_guard(cwd, c))
        self.deny(self.run_guard(self.on('main', ['grill']), 'bash -c "bash -c \'git push\'"'), r'release skill')
        self.deny(self.run_guard(cwd, 'powershell -Command "git merge card-7"', 'PowerShell'))
        for c in ['bash -c "git status"', 'powershell -Command "git log -1"', 'bash script.sh',
                  'bash -c "echo git push"']:
            with self.subTest(command=c):
                self.assertEqual(self.run_guard(cwd, c), '')

    def test_a_git_c_alias_invocation_is_refused_as_unresolvable(self):
        cwd = self.on('card-7')
        for c in ['git -c alias.p=push p', 'git -c alias.st=status st', 'git -c ALIAS.m=merge m main',
                  'git --config-env=alias.p=CMD p']:
            with self.subTest(command=c):
                self.deny(self.run_guard(cwd, c), r'alias')
        self.assertEqual(self.run_guard(cwd, 'git -c core.autocrlf=false status'), '')
        self.assertEqual(self.run_guard(self.on('card-7', ['release']), 'git -c alias.p=push p'), '')
        self.assertEqual(self.run_guard(self.on('card-7', profile=None), 'git -c alias.p=push p'), '')

    def test_a_checkout_or_switch_earlier_in_the_command_sets_the_branch_later_parts_are_judged_against(self):
        card = self.with_history('card-7', others=('main', 'parent-12'))
        for c in ['git checkout main && git merge card-7', 'git switch main; git merge --ff-only card-7',
                  'git checkout parent-12\ngit reset --hard', 'git checkout - && git checkout main && git merge x',
                  'git checkout -B main && git commit --amend']:
            with self.subTest(command=c):
                self.deny(self.run_guard(card, c))
        main = self.with_history('main', others=('card-7',))
        for c in ['git checkout card-7 && git merge main', 'git switch card-7 && git reset --hard HEAD~1',
                  'git checkout -b card-9 && git merge card-7', 'git switch --detach && git merge card-7',
                  'git checkout HEAD~1 && git merge card-7']:
            with self.subTest(command=c):
                self.assertEqual(self.run_guard(main, c), '')
        for c in ['git checkout -- a.txt && git merge card-7', 'git checkout a.txt && git merge card-7',
                  'git checkout card-7 a.txt && git merge card-7']:
            with self.subTest(command=c):
                self.deny(self.run_guard(main, c), r'integration branch')

    def test_a_build_session_gains_nothing_from_release_or_coordinate_in_another_root(self):
        target = self.on('main', ['coordinate'])
        build = self.on('card-7', ['build'])
        self.deny(self.run_guard(build, 'git -C "%s" merge --ff-only card-7' % target), r'integration branch')
        self.deny(self.run_guard(build, 'git -C "%s" reset --hard' % target))
        self.deny(self.run_guard(build, 'git -C "%s" push' % self.on('main', ['release'])), r'never pushes')
        # A coordinator's or release's own agents, with no build marker in their root, work as today.
        self.assertEqual(self.run_guard(self.on('card-7'), 'git -C "%s" merge --ff-only card-7' % target), '')
        self.assertEqual(self.run_guard(self.on('card-7', ['grill']), 'git -C "%s" reset --hard' % target), '')
        self.assertEqual(self.run_guard(self.on('main', ['build', 'coordinate']), 'git merge card-7'), '')

    def test_curate_may_commit_or_fast_forward_onto_the_integration_branch_and_nothing_else(self):
        cwd = self.on('main', ['curate'])
        self.assertEqual(self.run_guard(cwd, 'git commit -m "profile: standing answer"'), '')
        self.assertEqual(self.run_guard(cwd, 'git merge --ff-only curate-1'), '')
        for c in ['git merge curate-1', 'git reset --hard HEAD', 'git commit --amend --no-edit', 'git push']:
            with self.subTest(command=c):
                self.deny(self.run_guard(cwd, c))
        self.deny(self.run_guard(self.on('parent-12', ['curate']), 'git merge --ff-only curate-1'))

    def test_check_ready_may_commit_or_fast_forward_onto_the_integration_branch_and_nothing_else(self):
        cwd = self.on('main', ['check-ready'])
        self.assertEqual(self.run_guard(cwd, 'git commit -m "specs: re-stamped"'), '')
        self.assertEqual(self.run_guard(cwd, 'git merge --ff-only ready-12'), '')
        for c in ['git merge ready-12', 'git reset --hard HEAD', 'git push']:
            with self.subTest(command=c):
                self.deny(self.run_guard(cwd, c))
        self.deny(self.run_guard(self.on('parent-12', ['check-ready']), 'git merge --ff-only ready-12'))

    def test_git_push_without_any_marker_is_allowed_silently(self):
        self.assertEqual(self.run_guard(self.on('card-7'), 'git push origin card-7'), '')
        self.assertEqual(self.run_guard(self.on('main'), 'git push origin main'), '')
        self.assertEqual(self.run_guard(self.on('main'), 'git status && git -C . push'), '')
        self.assertEqual(self.run_guard(self.on('main', [('build', 13)]), 'git push'), '')

    def test_git_push_from_a_root_without_a_marker_into_one_with_a_card_skill_running_is_denied(self):
        target = self.on('main', ['grill'])
        self.deny(self.run_guard(self.on('card-7'), 'git -C "%s" push' % target), r'grill is running')

    def test_git_push_with_a_release_or_coordinate_marker_is_allowed_silently(self):
        self.assertEqual(self.run_guard(self.on('main', ['release']), 'git push origin main'), '')
        self.assertEqual(self.run_guard(self.on('main', ['coordinate']), 'git push origin main'), '')

    def test_git_push_under_build_or_grill_is_denied(self):
        self.deny(self.run_guard(self.on('card-7', ['build']), 'git -C . push'), r'never pushes')
        self.deny(self.run_guard(self.on('main', ['grill']), 'git push'), r'grill is running')

    def test_push_only_counts_as_the_command_token_not_as_a_word_in_another_argument(self):
        cwd = self.on('card-7', ['grill'])
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

    def path_forms(self, target):
        """Every spelling of target a command may use, by name."""
        forward = target.replace('\\', '/')
        forms = {'native': target, 'forward slashes': forward}
        if os.name == 'nt' and len(target) > 1 and target[1] == ':':
            rest = forward[2:]
            forms['MSYS /c/'] = '/%s%s' % (target[0].lower(), rest)
            forms['Cygwin /cygdrive/c/'] = '/cygdrive/%s%s' % (target[0].lower(), rest)
            forms['other case'] = target.swapcase()
        return forms

    def test_every_spelling_of_a_git_c_target_reaches_the_protected_branch(self):
        session = self.on('card-7')
        target = self.on('main')
        for name, path in self.path_forms(target).items():
            with self.subTest(form=name):
                self.deny(self.run_guard(session, 'git -C "%s" merge --ff-only card-7' % path),
                          r'integration branch')
        with self.subTest(form='relative'):
            rel = os.path.relpath(target, session)
            self.deny(self.run_guard(session, 'git -C "%s" merge --ff-only card-7' % rel), r'integration branch')

    def test_every_spelling_of_a_cd_target_reaches_the_protected_branch(self):
        session = self.on('card-7')
        target = self.on('main')
        for name, path in self.path_forms(target).items():
            with self.subTest(form=name):
                self.deny(self.run_guard(session, 'cd "%s" && git merge card-7' % path), r'integration branch')

    def test_git_dir_and_work_tree_targets_reach_the_protected_branch_in_every_spelling(self):
        session = self.on('card-7')
        target = self.on('main')
        for name, path in self.path_forms(target).items():
            with self.subTest(form=name):
                git_dir = path.rstrip('/\\') + '/.git'
                self.deny(self.run_guard(session, 'git --git-dir="%s" merge card-7' % git_dir), r'integration branch')
                self.deny(self.run_guard(session, 'git --git-dir "%s" --work-tree "%s" merge card-7' % (git_dir, path)),
                          r'integration branch')
        self.assertEqual(self.run_guard(target, 'git --git-dir="%s/.git" merge main' % session.replace('\\', '/')), '')

    def test_a_target_the_guard_cannot_resolve_fails_closed_in_a_guarded_session(self):
        session = self.on('card-7')
        missing = os.path.join(session, 'no-such-dir')
        for c in ['git -C "%s" merge card-7' % missing, 'git -C "%s" rebase main' % missing,
                  'git -C "/z/no/such/place" merge --ff-only card-7']:
            with self.subTest(command=c):
                self.deny(self.run_guard(session, c), r'cannot resolve')
        self.assertEqual(self.run_guard(self.on('card-7', ['release']), 'git -C "%s" merge card-7' % missing), '')
        self.assertEqual(self.run_guard(self.on('card-7', profile=None), 'git -C "%s" merge card-7' % missing), '')
        self.assertEqual(self.run_guard(session, 'git -C "%s" status' % missing), '')

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
        self.deny(self.run_guard(self.on('main', [('release', 13)]), 'git merge card-7'))
        longer = PROFILE.replace('- Git guard: on', '- Git guard: on\n- Marker lifetime: 48h')
        self.assertEqual(self.run_guard(self.on('main', [('release', 13)], longer), 'git merge card-7'), '')

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
