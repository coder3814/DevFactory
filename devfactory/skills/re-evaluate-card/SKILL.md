---
name: re-evaluate-card
description: Re-evaluate an existing card against the card standard — check its title, description and acceptance criteria, fold in whatever in its comments changes the outcome, grill the user about any gap, say when the card has moved on since its spec was stamped, and re-derive the spec for whatever changed. Use when the user asks to re-evaluate, check, review or audit a card against the standard, for instance after editing it by hand or after others have commented on it.
---

# Re-evaluate a card

Paths below are relative to this skill's directory.

Read these first, in full:

- `../../references/card-standard.md` and every module it lists
- `../../references/card-process.md` — the "Re-evaluating a card", "Folding"
  and "The spec" sections are the procedure you are carrying out.
- `../../references/working-a-card.md`
- `../../references/card-template.md`

Re-evaluation runs only because someone asked for it, and it checks the card as
it stands, whatever has changed on it and however. It does not try to work out
what was edited, and it records nothing about a direct edit to the card's
details: the edit is itself the change.

1. **Read the card** in full, comments included, as "Read a card" describes,
   after loading the profile as "Load the project profile" describes. If it has
   a spec line, read the spec's stamp and compare it with the card as Ready
   condition 9.2 in `../../references/definition-of-ready.md` does. If the card
   no longer matches the stamp, tell the user, before measuring, that the card
   has changed since its spec was stamped Ready.
2. **Measure** it against the standard, including whether the description and
   criteria carry what in the comments changes the outcome and contradict none
   of them. This first review is fresh. If it finds no breach, no question and
   no decision for the user, tell the user the card meets the standard, with
   any suggestions it made, change nothing on the card, and go to step 8.
   Otherwise carry on with the steps below.
3. **Fold in** any comment whose outcome-changing content is missing. The
   comment is already the record, so add no comment of your own for it. If the
   card is outside the profile's fold columns, each such comment is instead the
   user's decision, as "Fold" describes. Keep every criterion's ID as "Fold"
   describes.
4. **Grill** the user about each remaining gap. Their answers are new additions:
   record each question and answer as a comment, then fold the answer in.
5. **Measure again** as "Measure" describes — one follow-up review, with
   whatever it still finds going to the user at acceptance.
6. **Accept.** Show the user the rewritten sections, any changed team field
   with its reason, the review's decisions for the user, the verdict, anything
   the follow-up still found and the suggestions you left, and get their
   acceptance or changes. A change they ask for that carries new information is
   a new addition: record it as a comment, then fold it in. Changes the user
   asks for are folded in and shown to them again; they do not reopen the
   review.
7. **Write and verify.** Once accepted, write the sections and read the card back
   to confirm every write landed.
8. **Re-derive the spec.** If the card has a spec line and any part changed —
   in this re-evaluation, or since the stamp when step 1 found the card ahead
   of it — hand off to `grill` in re-derive mode as "Re-derive the spec"
   describes, naming each part that changed, and say when the interface
   determination or a scope boundary is among them. Report what changed in the
   spec. If nothing changed, leave the spec alone.
