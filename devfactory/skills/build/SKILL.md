---
name: build
description: Build one card in one session from its approved spec — check the stamp, make the delegated calls up front, build to the criteria with the tests and evidence the spec requires, stop on a question the spec does not answer, and have a separate reviewer pass the result before reporting. Use when a session is briefed to build a card, as a sub-issue in a parent issue run or as a standalone card.
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
---

# Build a card

One session builds one card from its spec, in its own worktree, without asking anything the
card, the spec, the profile, the repository or the decision line already answers. It
never reviews or accepts its own work: a separate reviewer passes it, and the requester
accepts it.

In a parent issue run the session reports to the coordinator, which its brief names; every
question and report goes there, and the coordinator owns merging and every event but
`development-started`. A standalone card reports to the requester directly and fires its
own events; after its review passes it hands to `accept`, and `release` merges it once.
In a parent issue run the coordinator has already fired `work-started` for this card.
"Report" below means to whichever applies. This skill never moves a card on the board: it
fires the events in `../../references/events.md` with `devfactory event <name> --card
<n>`, and the project's hooks move cards as the project wants. A hook that fails is
reported with its output, and the work carries on.

`devfactory` below means running the plugin's script with `python`: the script is
`${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`; if that variable is empty in your shell, it
is `../../scripts/devfactory.py` relative to this skill's folder.

**Markers.** Run `devfactory begin build` as your first action, and keep the marker for
the whole build: through every question, wait, review round and the merge, since the git
guard allows the parent branch's fast-forward only under it. Run `devfactory end build` as
your last action: in a parent issue run after the merge is reported, and for a standalone
card once you hand to `accept`, or when you stop with nothing left to do. A marker expires
after the profile's Marker lifetime (12 hours by default), and `begin` refreshes it, so
run `devfactory begin build` again whenever you resume after a wait, and when you are
messaged again to fix a finding or a refusal, before the first change. Markers and the
profile are found at the repository (worktree) root, wherever the shell's working
directory is.

## Read these first, in full

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

## Steps

1. **Begin, and start from current code.** Run `devfactory begin build`. In a parent issue
   run, rebase this branch onto the parent branch the coordinator named; for a standalone
   card, rebase onto the integration branch. Then load the profile as `working-a-card.md`
   says, with the binding it names. With no profile, start nothing and report it. Then,
   for a standalone card, fire `work-started`, before any check.

2. **Read the card and its spec.** Read the card in full as `working-a-card.md` says. Read
   its spec folder at the path the card's spec line gives: `spec.md` with its amendments,
   `gaps.md`, any wireframe, and any evidence already there. Read every profile entry the
   spec's Project bindings used names, and the recorded decisions where the profile says
   they are.

3. **Check the status and the stamp.** A build starts only on a spec whose status is
   `approved`, wherever the card sits on the board. Run
   `devfactory stamp-check --card <n> --spec <spec dir>` in this worktree (Ready condition
   9.2). When the status is not `approved` or the check fails, fire `readiness-lost` for
   the card when its spec status is `Ready` or `approved`, and start nothing: report the
   status and the check's output (`changed <old> <new>`, `not-ancestor`), and wait. A stale
   spec is re-derived through `grill`, never worked around.

4. **Fire `development-started`** for the card, before the first change.

5. **Make the delegated calls up front.** For each decision the spec delegates, make the
   call now, grounded in a recorded decision, the profile, a design system or an existing
   pattern in the code where one answers it, and log it in the spec's delegated-decisions
   log: the call, the choice, the reason. A developer's call that only comes to light later
   is made and logged the same way when it arises. The log is committed with the work.

6. **Build to the criteria.** Work in this session's worktree, on the branch the profile's
   Branches and merging names (its Sub-issue branch entry in a parent issue run), and
   commit as each piece is done.
   - Build what the criteria and the spec ask for and nothing beyond them (Done 5.1).
   - Write the tests the request types require (Done 1.2). Each test cites the criterion ID
     it exercises and asserts an observable outcome (Done 2.2).
   - Produce each evidence row's artifact at the row's checkpoint, into `evidence/<ID>/`,
     with its sidecar as `spec-template.md` says.
   - Run the profile's test gate before review, and follow the project's own rules for
     anything else a change carries.

7. **A question.** When the work needs a decision the spec does not record:
   1. Apply "Before anything is asked" in `decision-line.md` and the spec's delegations
      first. A question a standing answer in the profile settles is followed, and the entry
      cited in the log. A question on the developer's side is decided and logged as step 5
      says, not asked. A question on the requester's side that a recorded decision, the
      profile or the spec already answers is followed, and the answer is cited in the log.
   2. A question that survives stops this card's work. Report it in this shape and wait:

      ```text
      Question: <what must be decided, and why the work needs it now>
      Options: <each realistic option, and what it leads to>
      Recommendation: <one option, and why>
      Ready condition failed: <the condition that should have caught it, such as Ready 3.2>
      ```

   3. When the answer arrives and it changes the card (its outcome, a criterion, its scope
      or the work order), first put it on the card through `add-to-card` in settled mode
      with no-rederive, the answer being the requester's acceptance: that is request
      grilling's fold, never `grill`'s. Then, for every answer, run `grill` in amend mode
      with the question, the answer word for word and the Ready condition that failed. It
      writes the spec amendment and the gap entry on this card's branch. Report
      whether the amendment changes what another card depends on, then continue from the
      amended spec.

8. **Review.** When the card is built, write the criteria file with
   `devfactory criteria-ids --card <n>` into a file outside the repository, then run
   `devfactory evidence-check <spec dir> --criteria <file>` and `devfactory gaps check <spec
   dir>`. Fix every finding they report, or, for an open gap, settle it as step 7 says,
   before any review starts. Then start the `change-reviewer` agent by name with the Agent
   tool; it carries its own definition
   ([`../../agents/change-reviewer.md`](../../agents/change-reviewer.md)), tools and model.
   Give it the path to the plugin's `references/` folder, the card with its criteria, the
   spec path, the profile path, the base revision (the merge-base of this branch with the
   parent branch, or with the integration branch for a standalone card, computed at review
   time), the revision under review, and a clean checkout at that revision; never how the
   work was built or what you think of it. Fix each finding, commit, rerun both checks, and
   start a fresh review of the new revision. A finding that needs a decision the spec does
   not record is a question, handled as step 7 says.

   After a FAIL there are at most two further rounds. When the third review still fails,
   sort its findings as "Findings after the review limit" in `decision-line.md` says,
   without asking anyone:
   - **Every finding on the developer's side** (a missing or weak test, an incomplete
     evidence record or sidecar, a gap entry not written, a spec that no longer matches the
     built code while the behaviour it describes is unchanged): fix them and carry on,
     recording each gap entry as usual. A spec that no longer matches is amended through
     `grill` in amend mode. After a code fix, run both checks and one more review; when it
     passes, go on to step 9. When every fix was a spec-only amendment, go on to step 9
     without a further review.
   - **Any finding that changes what an observer sees or can do, what persisted data ends
     up as, or scope**, or the extra review still failing: stop and report the findings,
     and wait.

9. **Report**: what was built, by criterion ID; the review verdict and how many rounds it
   took, and, when the review limit was passed, each developer-side finding fixed without
   asking and whether a further review ran; the delegated calls made, from the log; the gaps raised, with their amendments;
   the branch and revision; the test gate's result; and anything left unverified.

10. **Finish.**
    - **In a parent issue run**, wait. Merge only when the coordinator says it is this
      card's turn, exactly as the brief says. Fire no other event, never merge
      into the integration branch, and never push. After the merge, report and wait again:
      this session, its worktree and its branch stay until `release` reaps them after
      acceptance.
    - **A standalone card**: the review's PASS is its Done verdict, since the change
      reviewer applies every Definition of Done condition but 6, which only a parent issue
      has; so is step 8's carrying on after spec-only amendments past the review limit.
      Fire `done` and stop building without merging: go straight into `accept`, asking
      nothing first, which hands to `release`, and `release` merges the work once.

## Fixing a finding or a refusal

In a parent issue run the coordinator may message a kept session with a Done-judge finding
or an acceptance refusal to fix; the parent-fixes session the coordinator starts receives
the ones no single sub-issue owns, and its card and spec are the parent's. Run
`devfactory begin build`, rebase onto the parent branch, and fix only what the message
names, against the card and spec the brief gives. A sub-issue's session has already run
steps 1 to 4 and runs them again only as far as reading anything changed. The parent-fixes
session runs steps 1 to 3 for the parent the first time it is messaged, and skips step 4:
the coordinator fired `development-started` for the parent. Write any gap entry the message asks for.
Then review the fix as step 8 says, with the base revision computed against the parent
branch, report as step 9 says, and merge only when the coordinator says it is your turn,
as step 10 says. When the coordinator says the fix is a spec-only amendment past the Done
judge's limit, amend the spec through `grill` in amend mode and report without a review.

Stop every agent you started before you finish, and tell each to stop its own.
