---
name: create-card
description: Create a work-tracking card that meets the card standard, either from scratch from the user's idea or by restructuring an existing card in place, with stable criterion IDs, the parent line on a sub-issue, the work order on a parent issue and the suggested model and effort on every card. Use when the user wants to raise, write, draft or create a card, story, ticket, work item, parent issue or sub-issue, or to bring an existing card up to the card standard ("restructure", "rewrite to standard", "convert this card").
---

# Create a card

Paths below are relative to this skill's directory.

Read these first, in full:

- `../../references/card-standard.md` and every module it lists — what the
  finished card must be.
- `../../references/card-process.md` — the "Creating a card" section is the
  procedure you are carrying out, and "The spec" says what follows a write to a
  card that has one.
- `../../references/working-a-card.md` — how to load the profile, shape a
  draft, measure, grill, fold, get acceptance, write and verify, and re-derive
  the spec.
- `../../references/card-template.md` — the skeleton to fill.

Load the profile as "Load the project profile" describes. Then decide which way
in applies. If the user names an existing card (an id, a link, or "this card"),
restructure it. Otherwise create one from scratch.

## From scratch

1. Take what the user gives you — the idea, whatever they know, links, files.
   Ask for the basic idea if you do not have it; do not ask for more yet.
2. If it holds more than one outcome, propose the set of cards, one outcome line
   each, and let the user decide the set before you draft any. Where the set is
   a parent issue and its sub-issues, say so. Work through the remaining steps
   for each card.
3. Shape it into a draft from the template, as "Shape a draft" describes: the
   criteria numbered from `C1`, the parent line on a sub-issue, the work order
   on a parent issue, the suggested model and effort, and the values the
   profile's team modules recommend. Leave out what you do not know rather than
   inventing it.
4. Measure the draft as "Measure" describes: one fresh review, grilling the
   user for each question it raises, then at most one follow-up. During
   creation nothing is recorded as comments; answers go straight into the
   draft.
5. Show the user the whole card, with each team field's value and reason, the
   verdict, anything the follow-up still found and the suggestions you left,
   and get their acceptance or changes. Changes the user asks for are folded in
   and shown to them again; they do not reopen the review.
6. Once accepted, create the card on the profile's board exactly as accepted,
   in the column the profile's stages map Request to, each part in the field
   the profile maps it to, marked as a parent issue or a sub-issue as the
   binding says, with a parent's sub-issue order set to match its work order.
   Attach any files the user provided, and verify it by reading it back. A new
   sub-issue of an existing parent changes that parent's work order: make that
   change through `add-to-card` on the parent.
7. If the card's column is the one the profile's stages map Grilling to, tell
   the user the next step is `grill`. Do not run it.

## From an existing card

1. Read the existing card in full, as "Read a card" describes.
2. Reshape everything already on it — description, criteria and comments — into
   the template, as "Shape a draft" describes. That existing content is treated
   as creation: it is not recorded as new comments. Write the criteria afresh
   from the outcome; do not edit the old ones into shape, and give them IDs as
   "From an existing card" in `card-process.md` says. Read each part from
   wherever the card holds it now, and fold everything in whatever column the
   card is in. Apply the profile's team modules to the reshaped card.
3. Measure the reshaped card as "Measure" describes: one fresh review,
   grilling the user for each question it raises, then at most one follow-up.
   Each question you ask and the user's answer are new additions to an
   existing card: record the question and the answer, in the user's own words,
   as a comment on the card, then fold the answer in.
4. Show the user the rewritten card, with each team field's value and reason,
   the verdict, anything the follow-up still found and the suggestions you
   left, and get their acceptance or changes. A change they ask for that
   carries new information is a new addition too: record it as a comment, then
   fold it in. Changes the user asks for are folded in and shown to them again;
   they do not reopen the review.
5. Once accepted, write it to the same card exactly as accepted — never create
   a replacement — with each part in the field the profile maps it to, clearing
   any field a part has moved out of; attach any files the user provided, and
   verify it by reading it back.
6. If the card has a spec line, re-derive the spec as "Re-derive the spec"
   describes, naming each part that changed.
7. Otherwise, if the card's column is the one the profile's stages map Grilling
   to, tell the user the next step is `grill`. Do not run it.
