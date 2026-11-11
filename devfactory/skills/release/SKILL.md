---
name: release
description: Release accepted work as the project profile says — merge and ship by the project's own release procedure, append the released specs' gap entries to the project's gap ledger and delete their spec folders in the release, close the cards and fire their released events, curate the gap records, and reap every session, worktree and branch. Use only when the requester says in the conversation to release a card or a parent issue run they have accepted; never on an agent's own judgment.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(python *devfactory.py*)
  - Bash(gh issue view *)
  - Bash(gh project item-list *)
  - Bash(az boards work-item show *)
  - Bash(git log *)
  - Bash(git show *)
  - Bash(git status *)
  - Bash(git rev-parse *)
  - Bash(git merge-base *)
  - Bash(git worktree list *)
  - Bash(git branch --list *)
---

# Release accepted work

The plugin ships no release mechanics. How work reaches the integration branch and goes
live is the profile's Branches and merging, with its Release entry (the release procedure:
the project's steps, or the skill that holds them), and its standing answers; this skill
follows them and adds only what every release does. This is the one merge onto the integration branch: a parent run's
parent branch, or a standalone card's own branch, which `build` left unmerged. Under a
coordinator, every command, write and event below is done by a session or a subagent
it starts, as `coordinate` says. This skill runs only on the requester's explicit instruction
in the conversation, never on an agent's own judgment: a session may invoke it once the
requester has said to release, and never otherwise. The instruction may come ahead of
time, in the requester's starting instruction for the run or the card, or in their
acceptance answer, as `accept` step 6 says; a release so authorised is not asked about
again.

`devfactory` below means running the plugin's script with `python`: the script is
`${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`; if that variable is empty in your shell, it
is `../../scripts/devfactory.py` relative to this skill's folder.

**Markers.** Run `devfactory begin release` as your first action and keep the marker for
the whole release, through every wait and question: the git guard allows the push, and the
merge onto the integration branch, only while it is there. Run `devfactory end release` as
your last action, after step 7, or when you stop and report with the release abandoned. A
marker expires after the profile's Marker lifetime (12 hours by default), and `begin`
refreshes it, so run `devfactory begin release` again whenever you resume after a wait.
Markers and the profile are found at the repository (worktree) root, wherever the shell's
working directory is.

**Before asking anything**, apply "Before anything is asked" in
[`../../references/decision-line.md`](../../references/decision-line.md): read the profile's
Standing answers and its Branches and merging, and when one of them answers the question,
act on it and cite it. Only what neither answers, and is the requester's to decide, is
asked: one question at a time, the recommended option first with a one-line reason. An
owner step the release procedure gives the requester, such as a production write, is still
theirs to take when its moment comes, whatever authorised the release.

## Read these first, in full

- [`../../references/working-a-card.md`](../../references/working-a-card.md): loading the
  profile, and moving and closing a card through the binding.
- [`../../references/profile-template.md`](../../references/profile-template.md): Branches
  and merging with the release procedure, the gap ledger, and Standing answers.
- [`../../references/spec-template.md`](../../references/spec-template.md): the gap entry's
  form.
- [`../../references/decision-line.md`](../../references/decision-line.md): what is asked,
  and what a standing answer or the developer's side settles.

## Steps

1. **Load and confirm.** Load the profile as `working-a-card.md` says, with its release
   procedure and every project skill it names for merging or releasing. Confirm that each
   card to release is in Acceptance with the requester's acceptance recorded on it.

2. **Settle what the profile leaves open.** When neither the profile's release procedure
   nor its Standing answers say how this work is released (where it merges, what ships it,
   what is checked once it is live), ask the requester, once, for each thing they leave
   open. Then propose the answer
   for the release procedure or as a standing answer and, when the requester accepts, write
   it to the profile with where it came from.

3. **Keep the gap records, then delete the spec folders.** For every card this release
   carries, the parent's and each sub-issue's in a run, first append every entry in its
   spec's `gaps.md` to the project ledger with `devfactory gaps ledger <spec dir> --card <n>
   --types <the spec's request types> --ledger .devfactory/gaps.md`, which writes the
   headings `spec-template.md` lays the ledger out with; then delete the spec folder.
   Both go in the release commit: the commit that brings the work onto the integration
   branch, or one of its own just before the work goes out when it is already there.
   History keeps the folders; the ledger keeps the gaps.

4. **Merge and release** as the profile's release procedure and the project's skills say:
   rebase, rerun the test gate, merge into the integration branch, and ship. When the
   project's conventions ask the requester something at this point, a standing answer, the
   release authorisation, or the recorded acceptance where the profile says so, answers
   it; otherwise ask. Work held rather than released
   keeps its cards accepted and open until the held release goes out.

5. **Close and fire.** Once the release is live, close each released card and fire
   `released` for it with `devfactory event released --card <n>`, as
   `../../references/events.md` says; a hook that fails is reported with its output. A
   parent issue, nested ones included, closes and fires only when every one of its
   sub-issues is released.

6. **Curate.** Run `curate`.

7. **Stop and reap.** Stop every session and agent the work started, the sub-issue
   sessions a parent run kept until acceptance included, remove every worktree and delete
   every branch it left, the parent's included, as the profile's Branches and merging says.
   Stop each session with `stop_session` before its worktree goes. A session cannot remove
   the worktree it works in, so have a subagent working from another checkout remove each
   one, then archive the session with `archive_session` once its worktree and branch are
   gone. Reaping asks nothing a standing answer or this step settles:
   - A branch whose work reached the integration branch by a rebase, so that `git branch
     -d` refuses it, is removed the way the profile's Branches and merging or a standing
     answer (such as "How is a finished branch removed?") says, force-deletion included,
     once its commits' changes are confirmed on the integration branch. Ask only when
     neither says.
   - A reaped worktree whose only uncommitted changes are regenerated build output (files
     the project's build or test gate writes, such as compiled assets, caches or test
     reports) is removed with that output discarded, without asking. Any other uncommitted
     change is reported and its worktree kept.
   Report anything you cannot confirm is gone.
