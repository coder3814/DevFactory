---
name: add-to-card
description: Add new information to an existing card that follows the card standard — an answer to one of its open questions, a new fact, a decision, or a file — by recording it as a comment and folding it into the description and acceptance criteria, keeping every criterion's ID, then re-deriving the card's spec for the parts that changed. Runs interactive by default, with the user accepting the rewrite, or settled when its caller says the requester has already answered. Use when the user gives you something for a card that already exists ("add this to card N", "the stakeholder answered the question on N", "attach this screenshot to the card"), or when another DevFactory skill hands it the requester's answer for a card.
---

# Add to a card

Paths below are relative to this skill's directory.

Read these first, in full:

- `../../references/card-standard.md` and every module it lists
- `../../references/card-process.md` — the "Updating a card", "Additions
  through an agent", "Folding" and "The spec" sections are the procedure you
  are carrying out.
- `../../references/working-a-card.md`

The skill runs in one of two modes, and its caller names which:

- **Interactive**, the default, and the mode whenever the user starts this skill
  directly: you record and fold, show the user the result, and write only once
  they accept it.
- **Settled**, named by a skill that hands you an answer the requester has
  already given: a readiness question answered during grilling, a question
  relayed during a development run, the requester's words on an acceptance
  not given, or a change the requester asks for during a run. The requester's
  answer is the acceptance: you write the fold
  without a further round on its wording, and the requester may object
  afterwards.

A caller may also pass **no-rederive**, which skips step 5. `grill` always calls
this skill settled with no-rederive, because it carries the spec forward
itself. Every other caller leaves step 5 to run.

1. **Read the card** in full, as "Read a card" describes, after loading the
   profile as "Load the project profile" describes.
2. **Record first.** Add what you were given to the card as a comment, in the
   giver's words and with its source where they gave one: interactive, the
   user's words; settled, the requester's answer as the caller passed it, with
   the question it answers where the caller gives one. Attach any file provided,
   and say in the comment what it shows. Recording happens before anything is
   folded in.
3. **Fold** the addition into the card's parts, if the card is in one of the
   profile's fold columns; otherwise the user decides, as "Fold" describes. In
   settled mode fold whatever the column, as "Where folding happens" says. If it
   answers an open question, the question
   leaves open questions and its answer lands where it changes the card. Keep
   every criterion's ID as "Fold" describes. Revise the work order and the
   suggested model and effort where the change calls for it, and apply again
   each team module whose field the change could affect.
4. **Accept, write and verify.**
   - **Interactive:** show the user the rewritten sections and any changed
     team field with its reason, and get their acceptance or changes. A change
     they ask for that carries new information is itself an addition: record it
     as a comment, then fold it in. Once accepted, write the sections and read
     the card back to confirm every write landed, as "Write and verify"
     describes.
   - **Settled:** the requester's answer is the acceptance, as "Accept"
     describes. Write the fold without asking, read the card back to confirm
     every write landed, then report the folded text to the caller as done and
     say the requester may object. An objection is a new addition, recorded and
     folded like any other.
5. **Re-derive the spec.** Skip this step when the caller passed no-rederive.
   Otherwise, if the card has a spec line and any part of the card changed,
   hand off to `grill` in re-derive mode as "Re-derive the spec" describes,
   naming each part that changed, and say when the interface determination or a
   scope boundary is among them. Report what changed in the spec. A comment
   that changed no part changes nothing in the spec.

This skill never writes the card's spec line, in either mode. `grill` writes it
directly, as "The spec line" in `../../references/card-standard.md` describes.

Adding to a card does not re-evaluate it. Checking the whole card against the
standard happens only when someone asks for it, through `re-evaluate-card`.
