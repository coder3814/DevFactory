---
name: check-ready
description: Check that a card, or a parent issue and every sub-issue not yet released, is still Ready to build without a single further question — catch any card that changed since its spec was stamped, have the readiness checker measure the specs together, settle every question and owner step with the requester one at a time, and fix the work order. It has two callers — grill's parent path, as its last step when a parent's set is first grilled or a card is added to it (at creation), and coordinate at development start, after it has started every session briefed to wait and before it sets any going.
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
  - Bash(git rev-parse *)
  - Bash(git merge-base *)
---

# Check readiness

Paths below are relative to this skill's directory. `devfactory` below means running the
plugin's script with `python`: the script is `${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`;
if that variable is empty in your shell, it is `../../scripts/devfactory.py` relative to
this skill's folder.

**Markers.** Run `devfactory begin check-ready` as your first action and
`devfactory end check-ready` as your last, including when you stop to ask the requester or
to report, and `devfactory begin check-ready` again when you resume. A marker expires
after the profile's Marker lifetime (12 hours by default), and `begin` refreshes it.
Markers and the profile are found at the repository (worktree) root, wherever the shell's
working directory is. When `begin` prints `plugin-changed`, load this skill again before you
continue.

Read these first, in full:

A file you have already read in full in this session, under the plugin version `begin`
printed, need not be read again.

- `../../references/definition-of-ready.md` — the conditions being checked.
- `../../references/decision-line.md` — who answers each question.
- `../../references/spec-template.md` — the spec folder, the records folder, the stamp and
  the gap record.
- `../../references/spec-procedure.md` — the review rule, dispatching the checker, asking the
  requester, folding an answer, a card-changing answer, the ready receipt and landing a
  commit, used here as written.
- `../../references/events.md` — the event you fire.
- `../../references/profile-template.md`
- `../../references/working-a-card.md` — loading the profile and reading a card.
- `../../agents/readiness-checker.md`, its Inputs section only — the `readiness-checker`
  agent you start.

This is the readiness check on its own, over specs that `grill` has already written. It has
two callers. `grill`'s parent path runs it as its last step, at creation, whenever a parent's
set is first grilled and whenever a card is added to it, re-checking every sub-issue and not
only the new one, because a new card can raise questions for the others. `coordinate` runs
it at development start, before any session begins work: the coordinator has already
started every session, briefed to wait for this check. A spec it measures has usually earned
Ready already, so it should find nothing, and anything it does find against a Ready spec is
a readiness miss, recorded as a gap.

A parent issue has no spec. What the check judges across the set, Ready 8.2 included, is
judged from the parent card and the sub-issues' specs, and the set's receipt and its gap
entries about the work order live in the parent's records folder,
`<specs path>/<parent id>/`.

1. **Load the profile** as "Load the project profile" in `working-a-card.md` says.
2. **Gather the cards.** Take the card named, and for a parent issue the parent itself and
   every sub-issue not yet closed; a sub-issue that is itself a parent brings its own
   sub-issues in the same pass. Read each in full with its comments, as "Read a card" in
   `working-a-card.md` says, and each sub-issue's or standalone card's spec folder under the
   profile's specs path. When a parent card still carries acceptance criteria, supporting
   information or a spec line, stop: report that it goes through `re-evaluate-card` first,
   which restructures it to the card standard, and check nothing.
3. **Check each stamp first.** For each card with a spec, run
   `devfactory stamp-check --card <n> --spec <spec dir>` from a checkout of the branch the
   spec lives on. `changed` is reported as "the card changed since Ready", and
   `not-ancestor` as "the stamped commit is not in this branch's history". Either sends that
   card to `grill` re-derive, telling it this check runs the readiness check itself. A card
   with no spec yet is reported as such and goes to `grill` new, which earns its Ready before
   this check continues; for a parent, `grill` works the set as "A parent issue" in that
   skill says.
4. **Compare the ready receipt.** List, one per line, the folder of every spec gathered, and
   compare the receipt as "The ready receipt" in `spec-procedure.md` says, from the same
   checkout, in the folder of the card this check was run for: for a parent issue, the
   parent's records folder, with `--parent <parent id>`. When every stamp in step 3 matched
   and this prints `match`, the specs, the parent card, the gap sources, the profile, the
   standard and the code are all as a passing check last found them: skip steps 5 to 7 and
   start no checker; step 8 reports "nothing open". Otherwise go on.
5. **Check, fresh.** Dispatch the readiness checker as "Dispatching the checker" in
   `spec-procedure.md` says, linting each spec first and passing every input it lists, kind
   fresh, over every card gathered, at the moment this run is: at creation when `grill`
   runs it, at development start when `coordinate` runs it. Checking the cards together is
   what finds a gap they share, and a work-order fault between them.
6. **Settle each item with the requester**, one question at a time, with the options and
   your recommendation first, as "Asking the requester" in `spec-procedure.md` says; a gap
   several cards share is asked once, as the rule. Each answer for a stamped spec is
   recorded as a gap at the stage the work is at, against the condition the checker named,
   written `Ready <id>`, and as a request change when the requester changed their mind
   rather than answered a miss. It takes one of two routes:
   - An answer that leaves the card as it is goes into the spec through `grill` amend, given
     the question, the answer and that condition. For each owner step without a moment, the
     agreed moment goes under the spec's "Owner steps" this way, against `Ready 8.1`.
   - An answer that changes the card (its outcome, a criterion, its scope or the work order)
     takes the route "A card-changing answer" in `spec-procedure.md` gives: `add-to-card` in
     settled mode, then `grill` re-derive, told that this check runs the readiness check
     itself. Each work-order fault's agreed fix goes onto the parent card this way, against
     `Ready 8.2`, its gap entry in the parent's records folder; so does a change to what one
     sub-issue waits on or which may run alongside it, whenever an answer brings one.
7. **Check, follow-up.** Dispatch the readiness checker once more, kind follow-up, with the
   fresh check's report and the spec versions it measured, over the cards that changed.
   Settle whatever it still finds with the requester as step 6 says, without another check.
8. **Report** "nothing open", or what is open and on which card: a question unanswered, an
   owner step with no moment, a work-order fault not fixed, a card whose spec is not Ready.
   An owner step scheduled for later in the run is settled, not open. At development start,
   when this check reports a card whose spec status is `Ready` or `approved` as not Ready and
   stops for the requester, fire `readiness-lost` for it with `devfactory event
   readiness-lost --card <n>`, as `events.md` says, once for this stop, unless a `grill`
   re-derive this check started already fired it for this stop. The check is done only when
   nothing is open. When a checker ran and nothing is open, write the ready receipt as "The
   ready receipt" in `spec-procedure.md` says, the folder and `--parent` of step 4 and
   `--commit` the head the last check reported reading, once every amendment and re-derivation is committed,
   and commit `receipts.md` on its own on the branch the specs live on, as "Landing a commit"
   there says.
