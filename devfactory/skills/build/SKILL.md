---
name: build
description: Build one card in one session from its approved spec — check the stamp, make the delegated calls up front, build to the criteria with the tests and evidence the spec requires, stop on a question the spec does not answer, and have a separate reviewer pass the result before reporting. Entered from a coordinator's brief, for a sub-issue in a parent issue run, or from `start`, for a standalone card.
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
  - Bash(git diff *)
  - Bash(git status *)
  - Bash(git rev-parse *)
  - Bash(git merge-base *)
  - SendMessage
---

# Build a card

One session builds one card from its spec, in its own worktree, without asking anything the
card, the spec, the profile, the repository or the decision line already answers. It
never reviews or accepts its own work: a separate reviewer passes it, and the requester
accepts it. A session comes here in one of two ways: a coordinator's brief hands it a
sub-issue of a parent issue run, or `start` hands it a standalone card.

In a parent issue run the session reports to the coordinator, which its brief names; every
question and report goes there. The coordinator decides when the session merges and fires
every event for the run but the two this session fires for its own card,
`development-started` and `readiness-lost`. A standalone card reports to the requester
directly and fires its own events; after its review passes it hands to `accept`, and
`release` merges it once. In a parent issue run the coordinator has already fired
`work-started` for this card. "Report" below means to whichever applies. This skill never
moves a card on the board: it fires the events in `../../references/events.md` with
`devfactory event <name> --card <n>`, and the project's hooks move cards as the project
wants. A hook that fails is reported with its output, and the work carries on.

**Reporting to the coordinator.** In a parent issue run, every report, question and stop
goes to the coordinator by message, the turn's closing message is one line saying the
report was sent, and the session ends a turn only to wait for the coordinator, as
[`../../references/reporting-to-the-coordinator.md`](../../references/reporting-to-the-coordinator.md)
says. That reference also says what each report carries and how to wait inside the turn.

`devfactory` below means running the plugin's script with `python`: the script is
`${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`; if that variable is empty in your shell, it
is `../../scripts/devfactory.py` relative to this skill's folder.

**Markers.** Run `devfactory begin build` as your first action, and keep the marker for
the whole build: through every question, wait, review round and the merge, since the tracker
guard allows your card writes only under it. Run `devfactory end build` as
your last action: in a parent issue run after the merge is reported, and for a standalone
card once you hand to `accept`, or when you stop with nothing left to do. A marker expires
after the profile's Marker lifetime (12 hours by default), and `begin` refreshes it, so
run `devfactory begin build` again whenever you resume after a wait, and when you are
messaged again to fix a finding or a refusal, before the first change. Markers and the
profile are found at the repository (worktree) root, wherever the shell's working
directory is.
When `begin` prints `plugin-changed`, load this skill again before you continue.

**Tests while building.** Run the tests the change touches as you build, with the
profile's Test gate `Affected tests` command where it names one, and run no full gate
before a review: the full gate's run before a merge is the change reviewer's own. The gate
after the rebase for a merge runs as
[`../../references/test-gate.md`](../../references/test-gate.md) says under "When the gate
runs".

## Read these first, in full

A file you have already read in full in this session, under the plugin version `begin`
printed, need not be read again.

- [`../../references/working-a-card.md`](../../references/working-a-card.md): loading the
  profile and reading a card.
- [`../../references/spec-template.md`](../../references/spec-template.md): the spec, the
  delegated-decisions log, `gaps.md` and `evidence/`.
- [`../../references/decision-line.md`](../../references/decision-line.md): what is yours to
  decide and what is the requester's.
- [`../../references/definition-of-ready.md`](../../references/definition-of-ready.md): the
  conditions a question names.
- [`../../references/definition-of-done.md`](../../references/definition-of-done.md): what
  the result is judged against.
- [`../../references/test-gate.md`](../../references/test-gate.md): when the gate runs and
  what a Recorded gate prints.
- [`../../references/reporting-to-the-coordinator.md`](../../references/reporting-to-the-coordinator.md):
  how a session in a parent issue run reports, asks, stops and waits.

## Steps

1. **Begin, and start from current code.** Run `devfactory begin build`, then load the
   profile as `working-a-card.md` says, with the binding it names. With no profile, start
   nothing and report it. In a parent issue run, rebase this branch onto the parent branch
   the coordinator named. A standalone card is built on its own branch in its own worktree,
   named as the profile's Branches and merging `Card branch` entry says; a standalone
   session that finds itself on the integration branch creates that branch and worktree and
   works there from then on. For a standalone card, rebase its branch onto the integration
   branch. Then,
   for a standalone card, fire `work-started`, before any check.

2. **Read the card and its spec.** Read the card in full as `working-a-card.md` says. Read
   its spec folder at the path the card's spec line gives: `spec.md` with its amendments,
   `gaps.md`, any wireframe, and any evidence already there. Read every profile entry the
   spec's Project bindings used names, and the recorded decisions where the profile says
   they are.

3. **Check the status and the stamp.** A build starts only on a spec whose status is
   `approved`, wherever the card sits on the board. Run
   `devfactory stamp-check --card <n> --spec <spec dir>` in this worktree (Ready condition
   9.2). When the status is not `approved` or the check fails, start nothing: report the
   stop, with the status and the check's output (`changed <old> <new>`, `not-ancestor`),
   as `reporting-to-the-coordinator.md` says under "What each report carries", and wait.
   When the card's spec status is `Ready` or `approved`, fire `readiness-lost` for the card
   once, as the session stops to wait; for a stop `grill` already fired it on (step 7's
   re-derive), fire nothing again. A stale spec is re-derived through `grill`, never
   worked around. When the session resumes, run this step again; once it passes, step 4
   fires `development-started`, the event for where the card now stands.

4. **Fire `development-started`** for the card, before the first change.

5. **Make the delegated calls up front.** For each decision the spec delegates, make the
   call now, grounded in a recorded decision, the profile, a design system or an existing
   pattern in the code where one answers it, and log it in the spec's delegated-decisions
   log: the call, the choice, the reason. A developer's call that only comes to light later
   is made and logged the same way when it arises. The log is committed with the work.

6. **Build to the criteria.** Work in this session's worktree and commit as each piece is
   done. In a parent issue run, work on the branch the brief names; when the app started
   the session on another branch, keep that branch and name it to the coordinator in the
   first report. For a standalone card, work on the card's branch from step 1.
   - Build what the criteria and the spec ask for and nothing beyond them (Done 5.1).
   - Write the tests the request types require (Done 1.2). Each test cites the criterion ID
     it exercises and asserts an observable outcome (Done 2.2).
   - Produce each evidence row's artifact at the row's checkpoint, into `evidence/<ID>/`,
     with its sidecar as `spec-template.md` says, once the code it shows is final: after
     the last commit that changes the code, since `evidence-check` refuses an artifact
     whose revision is older than a change to the code the card touches. Capture the
     artifacts together as the last step before a review, and after a review fix recapture
     only those the check names stale, each by its row's Generated by command. Boot each
     environment once per capture pass and capture every row it serves before moving on;
     restart it only after a change to code it serves.
   - Run the tests the change touches as you go, as "Tests while building" says. Follow
     the project's own rules for anything else a change carries.

7. **A question.** When the work needs a decision the spec does not record:
   1. Apply "Before anything is asked" in `decision-line.md` and the spec's delegations
      first. A question a standing answer in the profile settles is followed, and the entry
      cited in the log. A question on the developer's side is decided and logged as step 5
      says, not asked. A question on the requester's side that a recorded decision, the
      profile or the spec already answers is followed, and the answer is cited in the log.
   2. A question that survives stops this card's work. Report it in the shape
      `reporting-to-the-coordinator.md` gives under "What each report carries", to the
      coordinator by message in a parent issue run and to the requester for a standalone
      card, and wait.
   3. When the answer arrives and it changes the card (its outcome, a criterion, its scope
      or the work order), it takes the route that "A card-changing answer" in
      `../../references/spec-procedure.md` gives: put it on the card through `add-to-card`
      in settled mode, passing `no-rederive`, the answer being the requester's acceptance,
      and then run `grill` Re-derive yourself, giving it the question, the answer word for
      word, the stage (Development), the Ready condition that failed (`Ready <id>`) and
      whether the requester changed their mind rather than answered a miss, so that it
      writes the gap entry on this card's branch. When the answer leaves the card as it
      is, run `grill` Amend with the question, the answer, the stage (Development) and the
      condition, which writes the spec amendment and the gap entry on this card's branch.
      In a parent issue run, every question for the requester the Re-derive or the Amend
      raises goes to the coordinator, as `reporting-to-the-coordinator.md` says. When the
      re-derive stopped to wait for the requester, `grill` has fired `readiness-lost`:
      report the stop as `reporting-to-the-coordinator.md` says under "What each report
      carries", wait, and on resuming run step 3 again. When it returned the status to
      `Ready` and Re-derive step 8 had the spec approved again, `grill` has fired
      `readiness-lost` too: report nothing further, run step 3 again, and step 4 fires
      `development-started`. Report whether the change to the spec changes what
      another card depends on, then continue from the spec as it now stands.

8. **Review.** When the card is built, write the criteria file with
   `devfactory criteria-ids --card <n>` into a file outside the repository and compute the
   base revision: the merge-base of this branch with the parent branch, or with the
   integration branch for a standalone card, computed at review time. Before each review:
   - Commit everything, then, at that exact revision, run `devfactory evidence-check <spec
     dir> --criteria <file> --base <base revision>` and `devfactory gaps check <spec
     dir>`. These are the checks a script can make, so no review round is spent on them:
     evidence folders, sidecars, evidence that a clean checkout would lack, a sidecar
     revision a rebase left behind with its change altered, evidence captured before a
     later change to the code the card touches, a checkpoint the evidence row does not
     name, and an open or malformed gap entry. Start no review while either reports
     anything: fix each finding (an artifact whose sidecar revision is stale is captured
     again at the current revision, and its sidecar names that revision), or, for an open
     gap, settle it as step 7 says, commit, and run both checks again. Make no commit
     between the check that comes back clean and the verdict.
   - Start the `change-reviewer` agent by name with the Agent tool; it carries its own
     definition ([`../../agents/change-reviewer.md`](../../agents/change-reviewer.md)),
     tools and model. Read that definition's Inputs section, not the whole definition.
     Give it the path to the plugin's `references/` folder, the card with its criteria,
     the spec path, the profile path, the base revision, the revision the clean checks ran
     at as the revision under review, and a clean checkout at that revision, made as a
     worktree of this repository (`git worktree add --detach <path> <revision>`) so it
     reads the same gate records; never how the work was built or what you think of it.
   - Wait for the verdict inside the turn, as `reporting-to-the-coordinator.md` says under
     "Waiting inside the turn". Do the same for any command you run in the background.
   - After each verdict, write the report's lines under Findings and under Unstable, each
     already in the form `<Done id> | <criterion ID or -> | <text>`, into a file outside
     the repository, run `devfactory reviews add --card <id> --round <n> --verdict <v>
     --findings <file>` (with no `--findings` when both headings say "none"), and then
     remove the reviewer's checkout with `git worktree remove --force <path>`. Commit
     nothing for the record: it is kept outside the tracked tree, so the tree the
     reviewer's gate run recorded stays the tree that is merged.
   - On a FAIL, fix each finding, commit, and start the next round from the checks above.
     A finding that needs a decision the spec does not record is a question, handled as
     step 7 says.

   After a FAIL there are at most two further rounds. When the third review still fails,
   sort its findings as "Findings after the review limit" in `decision-line.md` says,
   without asking anyone:
   - **Every finding on the developer's side** (a missing or weak test, an incomplete
     evidence record or sidecar, a gap entry not written, a spec that no longer matches the
     built code while the behaviour it describes is unchanged): fix them and carry on,
     handing each to `grill` Amend with the finding's text as the question, the correction
     as the answer, the stage Done and the finding's `Done <id>` as the condition, which
     writes its gap entry and amends a spec that no longer matches. Carry on to step 9
     without a further review only when every fix was a spec amendment made through `grill` and `devfactory spec-only <spec dir> --base <the
     failed revision>` prints `spec-only`; the report then says, in these words, "no
     review passed this revision", lists the last review's findings and the amendment that
     answers each, and never says the card passed. Otherwise run the checks and one more
     review; when it passes, go on to step 9.
   - **Any finding that changes what an observer sees or can do, what persisted data ends
     up as, or scope**, or the extra review still failing: stop and report the findings,
     in a parent issue run by message as `reporting-to-the-coordinator.md` says, and wait.

9. **Report** what `reporting-to-the-coordinator.md` says the build report carries, under
   "What each report carries": in a parent issue run to the coordinator by message, and
   for a standalone card to the requester.

10. **Finish.**
    - **In a parent issue run**, wait. Merge only when the coordinator says it is this
      card's turn, exactly as the brief says: rebase onto the parent branch, run the gate
      as `test-gate.md` says under "When the gate runs" (the Recorded gate, which prints
      the record when the rebase left the tree unchanged and runs fresh otherwise; the
      Command where there is no Recorded gate), and fast-forward only on a pass. Fire no
      other event, never merge into the integration branch, and never push. When the
      fast-forward refuses, report it by message and wait. After the merge, report it by
      message and wait again: this session, its worktree and its branch stay until
      `release` reaps them after acceptance.
    - **A standalone card**: the review's PASS is its Done verdict, since the change
      reviewer applies every Definition of Done condition but 6, which only a parent issue
      has; so is step 8's carrying on after spec-only amendments past the review limit.
      Fire `done` and stop building without merging: go straight into `accept`, asking
      nothing first, which hands to `release`, and `release` merges the work once and,
      when it reaps, marks this session completed and archives it.

## Fixing a finding or a refusal

In a parent issue run the coordinator may message a kept session with a Done-judge finding
or an acceptance refusal to fix, among them one that no single sub-issue owns. Run
`devfactory begin build`, rebase onto the parent branch, and fix only what the message
names, against the card and spec the message names. The session has already run steps 1
to 4 for its own card and runs them again only as far as reading anything changed; for a
card and spec the message names that are not its own, it reads them as step 2 says. Then
review the fix as step 8 says, with the card and spec the message names and the base
revision computed against the parent branch, report as step 9 says, and merge only when
the coordinator says it is your turn, as step 10 says. When the coordinator says the fix is
a spec-only amendment past the Done judge's limit, make it through `grill` Amend and report
it without a review; the coordinator runs the `spec-only` check. Every report here goes to
the coordinator by message, as `reporting-to-the-coordinator.md` says.

For a standalone card, a refusal `accept` sorts as a defect comes back to this session. Run
`devfactory begin build`, fix only what the refusal names, review the fix as step 8 says,
fire `done`, and return to `accept`.

A refused defect's gap entry is written by the session that fixes it, once the fix is
committed, through `grill` Amend: the refusal as the question, the fix and its commit as the
answer, the stage Acceptance, and the `Done <id>` that `accept` named as the condition.

Stop every agent you started before you finish, and tell each to stop its own.
