---
name: check-ready
description: Check that a card, or a parent issue and every sub-issue not yet released, is still Ready to build without a single further question — catch any card that changed since its spec was stamped, have the readiness checker measure the specs together, settle every question and owner step with the requester one at a time, and fix the work order. Use when a parent issue is created, when a card is added to one, and at development start, when the coordinator runs it before starting any session.
---

# Check readiness

Paths below are relative to this skill's directory.

Read these first, in full:

- `../../references/definition-of-ready.md` — the conditions being checked.
- `../../references/decision-line.md` — who answers each question.
- `../../references/spec-template.md` — the spec folder, the stamp and the gap record.
- `../../references/profile-template.md`
- `../../references/working-a-card.md` — loading the profile and reading a card.
- `../grill/SKILL.md` — the review rule, dispatching the checker, asking the requester and
  folding an answer are defined there and used here as written.
- `../../agents/readiness-checker.md` — the agent you dispatch, its inputs and its report.

This is the readiness check on its own, over specs that `grill` has already written. It runs
at three moments: when a parent issue is created; when a card is added to a parent issue,
re-checking every sub-issue and not only the new one, because a new card can raise questions
for the others; and at development start, when `coordinate` runs it before any session
starts. A spec it measures has usually earned Ready already, so it should find nothing, and
anything it does find against a Ready spec is a readiness miss, recorded as a gap.

1. **Load the profile** as "Load the project profile" in `working-a-card.md` says.
2. **Gather the cards.** Take the card named, and for a parent issue the parent itself and
   every sub-issue not in the Release stage's column or closed; a sub-issue that is itself a
   parent brings its own sub-issues in the same pass. Read each in full with its comments, as
   "Read a card" in `working-a-card.md` says, and each card's spec folder under the profile's
   specs path, the parent's own spec included.
3. **Check each stamp first.** Compute each card's revision as "The stamp" in
   `spec-template.md` says and compare it with the spec's stamp. A mismatch is reported as
   "the card changed since Ready" and sends that card to `grill` re-derive, telling it this
   check runs the readiness check itself. A card with no spec yet is reported as such and
   goes to `grill` new, which earns its Ready before this check continues; for a parent, that
   grills every sub-issue not yet Ready and then the parent, as "A parent issue" in `grill`
   says.
4. **Check, fresh.** Dispatch the readiness checker as "Dispatching the checker" in `grill`
   says, on the model it names and with every input it lists, kind fresh, over every card
   gathered, at the moment this run is: at creation for a
   parent's creation or an added card, at development start when `coordinate` runs it. Its
   gap sources are the project ledger `.devfactory/gaps.md` and every live `gaps.md` under
   the profile's specs path. Checking the cards together is what finds a gap they share, and
   a work-order fault between them.
5. **Settle each item with the requester**, one question at a time, with the options and
   your recommendation first, as "Asking the requester" in `grill` says; a gap several cards
   share is asked once, as the rule. Every answer for a stamped spec takes one route: `grill`
   amend, given the question, the answer and the condition the checker named. Amend writes the
   spec, records the gap at the card's current stage, and writes the card through
   `add-to-card` when the answer changes it. Re-derive is for card changes, never for answers.
   - For each owner step without a moment, the agreed moment goes under the spec's "Owner
     steps" through `grill` amend, against condition 8.1.
   - For each work-order fault, the agreed fix goes onto the parent card through `grill`
     amend on the parent's spec, against condition 8.2; so does a change to what one
     sub-issue waits on or which may run alongside it, whenever an answer brings one.
6. **Check, follow-up.** Dispatch the readiness checker once more, kind follow-up, with the
   fresh check's report and the spec versions it measured, over the cards that changed.
   Settle whatever it still finds with the requester as step 5 says, without another check.
7. **Report** "nothing open", or what is open and on which card: a question unanswered, an
   owner step with no moment, a work-order fault not fixed, a card whose spec is not Ready.
   An owner step scheduled for later in the run is settled, not open. The check is done only
   when nothing is open.
