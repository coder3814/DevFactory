---
name: release
description: Release accepted work as the project profile says — rebase and run the test gate, make the records commit that appends the released cards' gap entries and review records to the project's ledgers, writes the post-release plans and deletes the spec folders and the parent's records folder, merge and ship by the project's own release procedure, close the cards and fire their released events, capture post-release evidence read-only once the release is live, curate the gap records, and reap every session (marked completed, then archived without asking), worktree, branch and review checkout, ending with each step's outcome; run again for the same cards, it skips what is already done. Use only when the requester says in the conversation to release a card or a parent issue run they have accepted; never on an agent's own judgment.
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
  - Bash(git cherry *)
---

# Release accepted work

The plugin ships no release mechanics. How work reaches the integration branch and goes
live is the profile's Branches and merging, with its Release entry (the release procedure:
the project's steps, or the skill that holds them), and its standing answers; this skill
follows them and adds only what every release does. This is the one merge onto the
integration branch: a parent run's parent branch, or a standalone card's own branch, which
`build` left unmerged. Under a coordinator, every command, write and event below is done by
a session or an agent it starts, as `coordinate` says. This skill runs only on the
requester's explicit instruction in the conversation, never on an agent's own judgment, as
"What an authorisation covers" says.

`devfactory` below means running the plugin's script with `python`: the script is
`${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`; if that variable is empty in your shell, it
is `../../scripts/devfactory.py` relative to this skill's folder.

**Markers.** Run `devfactory begin release` as your first action and keep the marker for
the whole release, through every wait and question: the git guard allows the push, and the
merge onto the integration branch, only while it is there. Run `devfactory end release` as
your last action, after step 9, or when you stop and report with the release abandoned. A
marker expires after the profile's Marker lifetime (12 hours by default), and `begin`
refreshes it, so run `devfactory begin release` again whenever you resume after a wait.
Markers and the profile are found at the repository (worktree) root, wherever the shell's
working directory is. When `begin` prints `plugin-changed`, load this skill again before
you continue.

**Before asking anything**, apply "Before anything is asked" in
[`../../references/decision-line.md`](../../references/decision-line.md): read the profile's
Standing answers and its Branches and merging, and when one of them answers the question,
act on it and cite it. Only what neither answers, and is the requester's to decide, is
asked: one question at a time, the recommended option first with a one-line reason.

## What an authorisation covers

`release` runs only once the requester has said to release, in the conversation. Their word
may come ahead of time, in their starting instruction for the run or the card, or in their
acceptance answer, such as `accept`'s accept-and-release option; a release so authorised is
not asked about again. An authorisation to release starts the `release` skill and nothing
more. A question the project's release procedure asks is answered only by a profile
standing answer; otherwise it is asked, whatever authorised the release. An owner step the
release procedure gives the requester, such as a production write, is still theirs to take
when its moment comes. The steps below that this skill settles itself, the reap included,
ask nothing.

## Running release again

`release` can be run again at any time for the same cards. Each step first looks whether its
result is already there and skips it when it is: the rebase and gate, when the integration
branch's head is an ancestor of the branch being merged (`git merge-base --is-ancestor`) and
the gate passed on its tree, the spec folders already gone from the branch, the work already on the integration branch, a
card already closed, a capture already committed, a curation already committed after this
release, a session already archived. Work held rather than released keeps its cards
accepted and open, and is released by running `release` again.

## Read these first, in full

A file you have already read in full in this session, under the plugin version `begin`
printed, need not be read again.

- [`../../references/working-a-card.md`](../../references/working-a-card.md): loading the
  profile, and moving and closing a card through the binding.
- [`../../references/profile-template.md`](../../references/profile-template.md): Branches
  and merging with the release procedure, the gap ledger, and Standing answers.
- [`../../references/spec-template.md`](../../references/spec-template.md): the gap entry's
  form.
- [`../../references/decision-line.md`](../../references/decision-line.md): what is asked,
  what a standing answer or the developer's side settles, and how a proposal is classified.
- [`../../references/test-gate.md`](../../references/test-gate.md): "When the gate runs"
  and "Recorded gates".

## Steps

1. **Load and confirm.** Load the profile as `working-a-card.md` says, with its release
   procedure and every project skill it names for merging or releasing. Confirm that the
   requester's acceptance is recorded on each card to release. No board column is read.

2. **Settle what the profile leaves open.** When none of the profile's release procedure,
   its Standing answers, the project instructions (`CLAUDE.md`) and the project's skills
   say how this work is released (where it merges, what ships
   it), ask the requester, once, for each thing they leave open. What is checked once the
   release is live is the evidence plan's post-release rows, which step 7 captures, and is
   never asked. Before proposing anything, classify the answer as `decision-line.md` says
   under "Classifying a proposal" and drop it when the plugin, the recorded decisions, the project instructions or a project
   skill already hold it. An answer the project instructions or a project skill own is
   proposed there, by name, and not written. Otherwise propose it for the release
   procedure, as a pointer where the project already records it, or as a standing answer,
   and, when the requester accepts, write it to the profile as the rule alone with one
   short citation of the card numbers it came from.

3. **Rebase and run the gate.** Rebase the branch being merged (the parent branch, or a
   standalone card's own branch) onto the integration branch, and run the test gate as
   `test-gate.md` says under "When the gate runs": the Recorded gate, which prints the
   record when the rebase left the tree unchanged and runs fresh otherwise, or with no
   Recorded gate the Command. Go on only on a pass. A rebase that conflicts is aborted
   (`git rebase --abort`) and reported with the conflicting files, and the release stops
   with the work held. The conflict is fixed as a Done finding is, by the kept session of a
   parent run or a standalone card's build session, reviewed and, in a parent run, judged
   again; then `release` is run again.

4. **Make the records commit**, on the branch being merged, once the gate has passed. It
   changes no code path, so no further gate run follows it. For every card this release
   carries, each sub-issue's in a run, and for a parent run the parent's records folder
   (`<specs path>/<parent id>/`, holding `receipts.md` and `gaps.md`):
   - append every gap entry to the project ledger with `devfactory gaps ledger <dir>
     --card <n> --types <the spec's request types> --ledger .devfactory/gaps.md`, which
     writes the headings `spec-template.md` lays the ledger out with, and for the parent's
     records folder `--card <parent id> --types "parent issue"`;
   - append every card's review record, and the parent's in a run, to the review ledger
     with `devfactory reviews ledger --card <id> --ledger .devfactory/reviews.md`, which
     also removes the card's stored record;
   - when a spec's evidence plan has rows marked post-release, write
     `.devfactory/post-release/<card>/plan.md` holding those rows under an `## Evidence
     plan` heading, as `spec-template.md` says under `evidence/`, and a `Request type(s):`
     line with the spec's request types, which step 7 gives the ledger;
   - delete the spec folder, the parent's records folder, and every
     `.devfactory/post-release/<card>/` folder an earlier release captured and committed;
     one whose capture is not committed stays and is reported.

   Both ledger commands skip what the ledger already holds. History keeps the folders; the
   ledgers keep the gaps and the reviews.

5. **Merge and ship** as the profile's release procedure and the project's skills say:
   merge into the integration branch, and ship. A question the project's conventions ask at
   this point is answered as "What an authorisation covers" says.

6. **Close and fire.** Once the release is live, close each released card and fire
   `released` for it with `devfactory event released --card <n>`, as
   `../../references/events.md` says; a hook that fails is reported with its output. A
   parent issue, nested ones included, closes and fires only when every one of its
   sub-issues is released.

7. **Check after release.** For each `.devfactory/post-release/<card>/plan.md` step 4
   wrote, once the deploy is live, capture every row read-only at the environment it
   names, reached as the profile's Environments entry says, by the row's Generated by
   procedure, into `evidence/<ID>/` beside the plan, each artifact with its sidecar naming
   the released commit and the environment. Boot each environment once and capture every
   row it serves before moving on. When only the requester can reach the environment, the
   capture is the owner step the spec scheduled after the deploy: ask them to take it now
   and record what they return. Commit the folder on the integration branch, in the
   worktree that has it checked out, and push nothing: it goes out with the next release,
   which deletes it. Then write the criterion IDs to a file outside the repository and run
   `devfactory evidence-check .devfactory/post-release/<card> --criteria <that file>
   --post-release`, which needs the capture committed; fix what it reports and commit
   again. Show the requester each artifact with what its row promised. When one shows its
   criterion does not hold, add a gap entry with `devfactory gaps add
   .devfactory/post-release/<card> --stage Release --question <what it showed> --condition
   "Ready 7.4"`, since no checkpoint before release could show it, then run `devfactory gaps
   ledger .devfactory/post-release/<card> --card <n> --types <the types the plan's
   Request type(s): line names> --ledger .devfactory/gaps.md`, which appends only the new entry and skips the ones step
   4 already ledgered, commit both, and report it: the card is already closed, and whether
   the failure becomes a new card is the requester's to decide.

8. **Curate.** Run `curate`.

9. **Stop and reap.** Once the release is live and the cards are closed, end every
   session and agent the work started: each sub-issue's session kept until acceptance, or
   a standalone card's build session. The reap asks nothing: archiving the sessions and
   removing what they leave is part of the release the requester authorised, so it never
   asks "archive these sessions?". For each session, in this order:
   1. Stop it with `stop_session` when it is mid-turn, and stop every agent it started.
   2. Check its worktree: have an agent working from another checkout read `git status`
      there. When the only uncommitted changes are regenerated build output (files the
      project's build or test gate writes, such as compiled assets, caches or test
      reports), carry on and discard it. When anything else is uncommitted, such as a
      change note under `docs/_intake/`, report it and leave that session, its worktree
      and its branch alone; the next steps skip it.
   3. Mark it completed with `mark_completed`, the sidebar's flag that it is done.
   4. Archive it with `archive_session`. Archiving stops the session and lets the app
      remove its worktree, which an idle session otherwise holds open: removing the
      folder first fails with "Permission denied" or hangs.

   Only after those sessions are archived, have an agent working from another checkout
   delete every branch the run left, the parent's included, remove any worktree still
   there, as the profile's Branches and merging says, and remove every detached review or
   judge checkout the run left (`git worktree list` shows each as detached; `git worktree
   remove --force <path>`). A parent branch or worktree a kept session still holds stays.
   In a standalone card the session running `release` is the build session, and archiving
   it ends its turn, so it does this last: it reports, runs `devfactory end release`,
   detaches its worktree's HEAD (`git switch --detach`) and deletes its own branch, then
   marks itself completed and archives itself. Reaping asks nothing a standing answer or
   this step settles:
   - A branch whose work reached the integration branch by a rebase, so that `git branch
     -d` refuses it, is confirmed by content and then removed with `git branch -D`,
     without asking: `git cherry <integration branch> <branch>` lists no commit marked
     `+`, so every commit of it has one carrying the same change on the integration
     branch, the check `coordinate` step 5 uses. Ask only when the check lists a `+`
     commit, naming each.
   - A reaped worktree whose only uncommitted changes are regenerated build output is
     removed with that output discarded, without asking. Any other uncommitted change is
     reported and its worktree kept.

   End by listing each of steps 1 to 9 as done, skipped as already done, or not done with
   the reason, and report anything you cannot confirm is gone: a session not archived, a
   worktree kept, a branch not deleted.
