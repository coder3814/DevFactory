# The test gate

The test gate proves that existing behaviour still holds. The profile's Test gate section
names it: the Command, and optionally an Affected tests command, a Recorded gate and its
Forced rerun, as [`profile-template.md`](profile-template.md) lays them out. This file says
when the gate runs, who runs it and what a recorded pass is worth. `build`, `release`, the
change reviewer and the Done judge follow it.

The full gate is the Recorded gate run with no selection where the profile names one, and
the Command otherwise.

## When the gate runs

- **While building**, the builder runs the tests its change touches, with the profile's
  Affected tests command where the Test gate names one. It runs no full gate before a
  review.
- **Before a PASS or a DONE**, the change reviewer or the Done judge runs the full gate
  fresh on the revision under review, as "The independent run" says. That is the full
  gate's run before a merge.
- **After the rebase for a merge**, of a sub-issue into the parent branch (`build`) or of
  the work onto the integration branch (`release`), the session that merges runs the
  Recorded gate with no selection. It prints the record when the rebase left the tree
  unchanged, and runs fresh otherwise. With no Recorded gate the session runs the Command.
  The merge goes ahead only on a pass.

The full gate runs at no other point. Before each run, commit, so the working tree is clean.

A gate with a precondition, such as a container runtime, names it in the profile. A run
whose named precondition was unavailable proves nothing either way: it is unchecked, not
failed, and the fix is to restore the precondition and run again.

## Recorded gates

A Recorded gate is optional. It is a command the project supplies and owns that runs the
gate and keeps a record of each pass, so that a tree already proven is not tested again.
The plugin ships none; it defines only what the command must guarantee:

- A record is keyed to the git tree the run tested, `git rev-parse HEAD^{tree}`, and the
  tests it passed, such as the test projects. A record is written only for a pass.
- A record is written by the command itself, after its own run passed.
- No record is written when the working tree is dirty (`git status --porcelain` prints
  anything), because then the tree that ran is not the tree the key names. On a dirty tree
  the command never prints a record either: it runs the selected tests and reports their
  result.
- Run on a tree that has a passing record covering the selected tests, the command prints
  that record instead of running them.
- The output says whether it is a fresh run or a record, and names the tree, the tests
  covered and, for a record, when and at which commit it was made, so a reader can check
  the record belongs to the revision in hand. It exits 0 on a pass, fresh or recorded, and
  non-zero on a failure.
- The records are stored outside the tracked tree, where every worktree of the repository
  and a reviewer's clean checkout read the same store, such as a folder under
  `git rev-parse --git-common-dir`.

The Forced rerun is required with a Recorded gate. It runs the tests again on a tree that
already has a record and records the new pass.

A printed record counts as a pass only when the tree it names is the tree in hand
(`git rev-parse HEAD^{tree}`) and it covers the full gate. A record from any other tree, one
that covers only some of the tests, or a claim of a pass in a report or a prompt, never
counts.

Nobody writes or edits a record by hand: no session, agent or person. Only the Recorded
gate's own command, or its Forced rerun, writes one, after its own pass.

## The independent run

The change reviewer and the Done judge decide every other condition first. Only when
nothing else fails do they run the full gate fresh on the revision under review, before
giving PASS or DONE: the Forced rerun where the profile names a Recorded gate, else the
Command. A FAIL or NOT DONE verdict needs no gate run. The checkout they run in is a
worktree of the same repository, so the pass a Forced rerun records there is the record the
gate after the rebase reads.

When that fresh run fails, the reviewer reruns the failing tests once. A pass on the rerun
is a pass, and the report names each such test as unstable, under condition Done 1.1. A
failure on the rerun is a Done 1.1 finding with the failing tests named.
