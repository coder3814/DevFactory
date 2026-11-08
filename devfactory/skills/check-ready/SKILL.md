---
name: check-ready
description: Check that a card, or a parent issue and every sub-issue not yet released, is still Ready to build without a single further question — catch any card that changed since its spec was stamped, have the readiness checker measure the specs together, settle every question and owner step with the requester one at a time, and fix the work order. Use when a parent issue is created, when a card is added to one, and at development start, when the coordinator runs it before starting any session.
---

# Check readiness

Paths below are relative to this skill's directory.

Read these first, in full:

- `../../references/definition-of-ready.md` — the conditions being checked.
- `../../references/decision-line.md` — who answers each question.
- `../../references/spec-template.md` — the spec folder and its gap record.
- `../../references/profile-template.md`
- `../../references/working-a-card.md` — loading the profile and reading a card.
- `../grill/SKILL.md` — the stamp, the review rule, asking the requester and folding an
  answer are defined there and used here as written.
- `../../agents/readiness-checker.md` — the agent you dispatch, its inputs and its report.

This is the readiness check on its own, over specs that `grill` has already written. It runs
when a parent issue is created; when a card is added to a parent issue, re-checking every
sub-issue and not only the new one, because a new card can raise questions for the others;
and at development start, when `coordinate` runs it before any session starts. By then it
should usually find nothing, and anything it does find is a readiness miss, recorded as a gap.

1. **Load the profile** as "Load the project profile" in `working-a-card.md` says.
2. **Gather the cards.** Take the card named, and for a parent issue every sub-issue not in
   the Release stage's column or closed; a sub-issue that is itself a parent brings its own
   sub-issues in the same pass. Read each in full with its comments, as "Read a card" in
   `working-a-card.md` says, and each card's spec folder under the profile's specs path.
3. **Check each stamp first.** Recompute each card's revision hash as "The stamp" in
   `grill` says and compare it with the spec's stamp. A mismatch is reported as "the card
   changed since Ready" and sends that card to `grill` re-derive, telling it this check
   runs the readiness check itself. A card with no spec yet is reported as such and goes to
   `grill` new, which earns its Ready before this check continues.
4. **Check, fresh.** Dispatch the readiness checker as a fresh check, as the review rule in
   `grill` says, telling it to follow `../../agents/readiness-checker.md` exactly, with the
   repository path, every card's ID, every spec path, the profile path, every gap record
   (`gaps.md`) under the profile's specs path to read first, and whether the run is at
   creation or at development start. Checking the cards together is what finds a gap they
   share, and a work-order fault between them.
5. **Settle each item with the requester**, one question at a time, with the options and
   your recommendation first, as "Asking the requester" in `grill` says; a gap several cards
   share is asked once, as the rule.
   - Each answer is folded as "Folding an answer" in `grill` says. Into a spec that has
     earned Ready, it goes through `grill` amend, with the question, the answer and the
     condition the checker named; at development start every such answer is a gap. When the
     answer changes the card, `add-to-card` writes it first and `grill` re-derive brings the
     spec along, as this check's caller.
   - For each owner step without a moment, agree the moment with the requester and record it
     under the spec's "Owner steps" through `grill` amend, against condition 8.1.
   - Fix each work-order fault on the parent card through `add-to-card`, and revise the work
     order whenever an answer changes what one sub-issue waits on or which may run alongside
     it.
6. **Check, follow-up.** Dispatch the readiness checker once more, as the follow-up, over
   the cards that changed. Settle whatever it still finds with the requester as step 5 says,
   without another check.
7. **Report** "nothing open", or what is open and on which card: a question unanswered, an
   owner step with no moment, a work-order fault not fixed, a card whose spec is not Ready.
   An owner step scheduled for later in the run is settled, not open. The check is done only
   when nothing is open.
