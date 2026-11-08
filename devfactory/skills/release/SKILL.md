---
name: release
description: Release accepted work as the project profile says — merge and ship by the project's own release procedure, append the released specs' gap entries to the project's gap ledger and delete their spec folders in the release, move the cards to Release and close them, curate the gap records, and reap every session, worktree and branch. Use after the requester accepts a card or a parent issue run.
---

# Release accepted work

The plugin ships no release mechanics. How work reaches the integration branch and goes
live is the profile's Branches and merging, with its Release entry (the release procedure:
the project's steps, or the skill that holds them), and its standing answers; this skill
follows them and adds only what every release does. This is the one merge onto the integration branch: a parent run's
parent branch, or a standalone card's own branch, which `build` left unmerged. Under a
coordinator, every command, write and board move below is done by a session or an agent it
starts, as the runtime file says. Every agent this skill starts runs on the model and effort
the card's Suggested model and effort names (the parent's, in a parent run), or the
profile's default under Sessions when it names none.

The requester is asked one question at a time, the recommended option first with a
one-line reason.

## Read these first, in full

- [`../../references/working-a-card.md`](../../references/working-a-card.md): loading the
  profile, and moving and closing a card through the binding.
- [`../../references/profile-template.md`](../../references/profile-template.md): Branches
  and merging with the release procedure, the gap ledger, and Standing answers.
- [`../../references/spec-template.md`](../../references/spec-template.md): the gap entry's
  form.

## Steps

1. **Load and confirm.** Load the profile as `working-a-card.md` says, with its release
   procedure and every project skill it names for merging or releasing. Confirm that each
   card to release is in Acceptance with the requester's acceptance recorded on it.

2. **Settle what the profile leaves open.** When the profile's release procedure does not
   say how this work is released (where it merges, what ships it, what is checked once it
   is live), ask the requester, once, for each thing it leaves open. Then propose the answer
   for the release procedure or as a standing answer and, when the requester accepts, write
   it to the profile with where it came from.

3. **Keep the gap records, then delete the spec folders.** For every card this release
   carries, the parent's and each sub-issue's in a run, first append every entry in its
   spec's `gaps.md` to the project ledger `.devfactory/gaps.md`, each prefixed with the
   card's id and the spec's request types, as `spec-template.md` lays the ledger out; then delete the spec folder.
   Both go in the release commit: the commit that brings the work onto the integration
   branch, or one of its own just before the work goes out when it is already there.
   History keeps the folders; the ledger keeps the gaps.

4. **Merge and release** as the profile's release procedure and the project's skills say:
   rebase, rerun the test gate, merge into the integration branch, and ship. When the
   project's conventions ask the requester something at this point, the recorded acceptance
   answers it where the profile says so; otherwise ask. Work held rather than released
   keeps its cards in Acceptance until the held release goes out.

5. **Move and close.** Once the release is live, move each released card to Release and
   close it. A parent issue, nested ones included, moves and closes only when every one of
   its sub-issues is released.

6. **Curate.** Run `curate`.

7. **Stop and reap.** Stop every session and agent the work started, the sub-issue
   sessions a parent run kept until acceptance included, remove every worktree and delete
   every branch it left, the parent's included, as the profile's Branches and merging says,
   stopping each session before its worktree goes, in the way the profile's runtime file
   says. Report anything you cannot confirm is gone.
