---
name: release
description: Release accepted work as the project profile says — merge and ship by the project's own conventions, delete the released cards' spec folders in the release, move the cards to Release and close them, curate the gap records, and reap every session, worktree and branch. Use after the requester accepts a card or a parent issue run.
---

# Release accepted work

The plugin ships no release mechanics. How work reaches the integration branch and goes
live is the profile's Branches and merging and its standing answers, and the project's own
skills where the profile names them; this skill follows them and adds only what every
release does. Under a coordinator, every command, write and board move below is done by a
session or an agent it starts, as the runtime file says.

The requester is asked one question at a time, the recommended option first with a
one-line reason.

## Read these first, in full

- [`../../references/working-a-card.md`](../../references/working-a-card.md): loading the
  profile, and moving and closing a card through the binding.
- [`../../references/profile-template.md`](../../references/profile-template.md): Branches
  and merging, and Standing answers.

## Steps

1. **Load and confirm.** Load the profile as `working-a-card.md` says, with every project
   skill it names for merging or releasing. Confirm that each card to release is in
   Acceptance with the requester's acceptance recorded on it.

2. **Settle what the profile leaves open.** When the profile does not say how this work is
   released (where it merges, what ships it, what is checked once it is live), ask the
   requester, once, for each thing it leaves open. Then propose the answer as a standing
   answer and, when the requester accepts, write it to the profile's Standing answers with
   where it came from.

3. **Delete the spec folders.** Delete the spec folder of every card this release carries,
   the parent's and each sub-issue's in a run, in the release commit: the commit that brings
   the work onto the integration branch, or one of its own just before the work goes out
   when it is already there. History keeps them.

4. **Merge and release** as the profile and the project's skills say: rebase, rerun the
   test gate, merge into the integration branch, and ship. When the project's conventions
   ask the requester something at this point, the recorded acceptance answers it where the
   profile says so; otherwise ask. Work held rather than released keeps its cards in
   Acceptance until the held release goes out.

5. **Move and close.** Once the release is live, move each released card to Release and
   close it. A parent issue, nested ones included, moves and closes only when every one of
   its sub-issues is released.

6. **Curate.** Run `curate`.

7. **Stop and reap.** Stop every session and agent the work started, remove every worktree
   and delete every branch it left, the parent's included, as the profile's Branches and
   merging says. Report anything you cannot confirm is gone.
