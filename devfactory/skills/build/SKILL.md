---
name: build
description: Build one card in one session from its approved spec — check the stamp, make the delegated calls up front, build to the criteria with the tests and evidence the spec requires, stop on a question the spec does not answer, and have a separate reviewer pass the result before reporting. Use when a session is briefed to build a card, as a sub-issue in a parent issue run or as a standalone card.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(node *devfactory.js *)
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
question and report goes there, and the coordinator owns merging and every column move but
the move to Development. A standalone card reports to the requester directly and moves
its own card; after its review passes it hands to `accept`, and `release` merges it once.
"Report" below means to whichever applies.

`devfactory` below means `node "${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.js"`, the script
in the plugin's `scripts/` folder.

**Markers.** Run `devfactory begin build` as your first action, and keep the marker for the
whole build: through every question, wait, review round and the merge, since the git guard
allows the parent branch's fast-forward only under it. Run `devfactory end build` as your
last action: in a parent issue run after the merge is reported, and for a standalone card
once you hand to `accept`, or when you stop with nothing left to do. When you are messaged
again to fix a finding or a refusal, run `devfactory begin build` before the first change.

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

1. **Load the profile** as `working-a-card.md` says, with the binding it names. With no
   profile, start nothing and report it.

2. **Read the card and its spec.** Read the card in full as `working-a-card.md` says. Read
   its spec folder at the path the card's spec line gives: `spec.md` with its amendments,
   `gaps.md`, any wireframe, and any evidence already there. Read every profile entry the
   spec's Project bindings used names, and the recorded decisions where the profile says
   they are.

3. **Check the status and the stamp.** A build starts only on a spec whose status is
   `approved`, whatever column the card is in. Run
   `devfactory stamp-check --card <n> --spec <spec dir>` in this worktree (Ready condition
   9.2). When the status is not `approved` or the check fails, start nothing: report the
   status and the check's output (`changed <old> <new>`, `not-ancestor`), and wait. A stale
   spec is re-derived through `grill`, never worked around.

4. **Move the card to Development**, the column the profile's Stages map that stage to,
   through the binding, before the first change.

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
   1. Apply the decision line and the spec's delegations first. A question on the
      developer's side is decided and logged as step 5 says, not asked. A question on the
      requester's side that a recorded decision, the profile or the spec already answers is
      followed, and the answer is cited in the log.
   2. A question that survives stops this card's work. Report it in this shape and wait:

      ```text
      Question: <what must be decided, and why the work needs it now>
      Options: <each realistic option, and what it leads to>
      Recommendation: <one option, and why>
      Ready condition failed: <the condition that should have caught it, such as Ready 3.2>
      ```

   3. When the answer arrives, run `grill` in amend mode with the question, the answer word
      for word and the Ready condition that failed. It writes the spec amendment and the
      gap entry on this card's branch, and, when the answer changes observable behaviour
      or scope, the card through `add-to-card` in settled mode, the answer being the
      requester's acceptance. Report
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
   start a fresh review of the new revision. After a FAIL there are at most two further
   rounds: when the third review still fails, stop and report it with its findings, and
   wait. A finding that needs a
   decision the spec does not record is a question, handled as step 7 says.

9. **Report**: what was built, by criterion ID; the review verdict and how many rounds it
   took; the delegated calls made, from the log; the gaps raised, with their amendments;
   the branch and revision; the test gate's result; and anything left unverified.

10. **Finish.**
    - **In a parent issue run**, wait. Merge only when the coordinator says it is this
      card's turn, exactly as the brief says. Move the card to no other column, never merge
      into the integration branch, and never push. After the merge, report and wait again:
      this session, its worktree and its branch stay until `release` reaps them after
      acceptance.
    - **A standalone card**: the review's PASS is its Done verdict, since the change
      reviewer applies every Definition of Done condition but 6, which only a parent issue
      has. Move the card to Done and stop building without merging: follow `accept`, which
      hands to `release`, and `release` merges the work once.

Stop every agent you started before you finish, and tell each to stop its own.
