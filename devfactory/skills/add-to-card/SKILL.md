---
name: add-to-card
description: Add new information to an existing card that follows the card standard — an answer to one of its open questions, a new fact, a decision, or a file — by recording it as a comment and folding it into the description and acceptance criteria, keeping every criterion's ID, then re-deriving the card's spec for the parts that changed. Runs interactive by default, with the user accepting the rewrite, or settled when its caller says the requester has already answered. Use when the user gives you something for a card that already exists ("add this to card N", "the stakeholder answered the question on N", "attach this screenshot to the card"), or when another DevFactory skill hands it the requester's answer for a card.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(python *devfactory.py*)
  - Bash(gh issue view *)
  - Bash(gh project item-list *)
  - Bash(gh api -X GET *)
  - Bash(az boards work-item show *)
  - Bash(git log *)
---

# Add to a card

Paths below are relative to this skill's directory. `devfactory` below means running the
plugin's script with `python`: the script is `${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`;
if that variable is empty in your shell, it is `../../scripts/devfactory.py` relative to
this skill's folder. Read the tracker with `gh issue view`, `gh project item-list`,
`gh api -X GET` or `az boards work-item show`, as the profile's binding says; those reads
and the script run without a permission prompt.

**Markers.** Run `devfactory begin add-to-card` as your first action and
`devfactory end add-to-card` as your last. Whenever you end your turn to wait for the
user's acceptance or decision, or stop for any reason, such as finding no profile, run
`devfactory end add-to-card` first, and `devfactory begin add-to-card` again when you
resume. The tracker guard allows your card writes only while the marker is there. A marker
expires after the profile's Marker lifetime (12 hours by default), and `begin` refreshes
it. Markers and the profile are found at the repository (worktree) root, wherever the
shell's working directory is. When `begin` prints `plugin-changed`, load this skill again
before you continue.

Read these first, in full. A file you have already read in full in this session, under
the plugin version `begin` printed, need not be read again.

- `../../references/card-standard.md` and every module it lists
- `../../references/card-process.md` — the "Updating a card", "Additions
  through an agent", "Folding" and "The spec" sections are the procedure you
  are carrying out.
- `../../references/working-a-card.md`

The skill runs in one of two modes, and its caller names which:

- **Interactive**, the default, and the mode whenever the user starts this skill
  directly: you record and fold, show the user the result, and write only once
  they accept it.
- **Settled**, as "Settled mode" below says.

## Settled mode

Any answer the requester has already given that changes a card comes here in settled
mode, whichever skill received it, and so does a fix to a card's own consistency that
needs no one's answer. These skills hand one over:

- `grill`: a request question it handed back, once the requester has answered it; a
  change the requester asks for at approval that would change the card; and a breach of
  the card's own consistency that its request gate found and that needs no one's answer,
  such as a stale model-and-effort reason or a sub-issue missing from the work order;
- `check-ready`;
- `build`;
- `coordinate`;
- `accept`.

No other skill hands this skill a settled answer, and `re-evaluate-card` takes none. The
requester's answer is the acceptance: you write the fold without a further round on its
wording, and the requester may object afterwards.

Every skill that hands this skill a settled answer passes **no-rederive**, which skips
step 6, and then runs `grill` Re-derive for the changed card itself, as "A card-changing
answer" in `../../references/spec-procedure.md` says; `grill`'s request-gate fix passes it
too and measures the card again instead. Run directly by the user, without
`no-rederive`, this skill hands to Re-derive itself in step 6.

## Steps

1. **Begin.** Run `devfactory begin add-to-card`.
2. **Read the card** in full, as "Read a card" describes, after loading the
   profile as "Load the project profile" describes.
3. **Record first.** Add what you were given to the card as a comment, in the
   giver's words and with its source where they gave one: interactive, the
   user's words; settled, the requester's answer as the caller passed it, with
   the question it answers where the caller gives one, or the consistency fix
   as the caller states it. Attach any file provided,
   and say in the comment what it shows. Recording happens before anything is
   folded in.
4. **Fold** the addition into the card's parts, wherever the card sits on the
   board. If it answers an open question, the question
   leaves open questions and its answer lands where it changes the card. Keep
   every criterion's ID as "Fold" describes. Revise the work order and the
   suggested model and effort where the change calls for it, and apply again
   each team module whose field the change could affect. When the criteria
   changed, write the folded card to a scratch file, the title on the first line
   and the description below it, and run `devfactory criteria-ids --text <file>`;
   fix any duplicate ID it reports before going on.
5. **Accept, write and verify.**
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
   In either mode, when the criteria changed, the read-back includes
   `devfactory criteria-ids --card <id>` (on a tracker `gh` does not reach,
   `--text` with the card as read back).
6. **Re-derive the spec.** Skip this step when the caller passed no-rederive, as
   "Settled mode" says.
   Otherwise, if the card has a spec line and any part of the card changed,
   hand to `grill` Re-derive as "Re-derive the spec" describes, naming each part
   that changed, and say when the interface determination or a scope boundary
   is among them; `grill` fires whatever event its outcome calls for. Report
   what changed in the spec. A comment that changed no part changes nothing in
   the spec. A parent issue has no spec line: when its work order changed and
   any of its sub-issues has a spec line, hand to `grill` for the parent, which
   brings the set along.
7. **End.** Run `devfactory end add-to-card`.

This skill never writes the card's spec line, in either mode. `grill` writes it
directly, as "The spec line" in `../../references/card-standard.md` describes.

Adding to a card does not re-evaluate it. Checking the whole card against the
standard happens only when someone asks for it, through `re-evaluate-card`.
