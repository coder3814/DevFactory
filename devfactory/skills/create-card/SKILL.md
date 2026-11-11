---
name: create-card
description: Create a work-tracking card that meets the card standard, either from scratch from the user's idea or by restructuring an existing card in place, with stable criterion IDs, the parent line on a sub-issue, the work order on a parent issue and the suggested model and effort on every card. Use when the user wants to raise, write, draft or create a card, story, ticket, work item, parent issue or sub-issue, or to bring an existing card up to the card standard ("restructure", "rewrite to standard", "convert this card").
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

# Create a card

Paths below are relative to this skill's directory. `devfactory` below means running the
plugin's script with `python`: the script is `${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`;
if that variable is empty in your shell, it is `../../scripts/devfactory.py` relative to
this skill's folder. Read the tracker with `gh issue view`, `gh project item-list`,
`gh api -X GET` or `az boards work-item show`, as the profile's binding says; those reads
and the script run without a permission prompt.

**Markers.** Run `devfactory begin create-card` as your first action and
`devfactory end create-card` as your last. Whenever you end your turn to wait for the
user's answer or acceptance, or stop for any reason, run `devfactory end create-card`
first, and `devfactory begin create-card` again when you resume. The tracker guard allows
your card writes only while the marker is there. A marker expires after the profile's
Marker lifetime (12 hours by default), and `begin` refreshes it. Markers and the profile
are found at the repository (worktree) root, wherever the shell's working directory is.

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
- `../../agents/card-reviewer.md` — the `card-reviewer` agent you start, its inputs
  and its report.
- `../../references/definition-of-request.md` — what the finished card must meet
  before a spec is written from it.
- `../../references/events.md` — the `request-met` event you fire.

After `begin`, load the profile as "Load the project profile" describes; if there is
none, run `devfactory end create-card` before you offer `configure-project` and stop.
Then decide which way in applies. If the user names an existing card (an id, a link, or
"this card"), restructure it. Otherwise create one from scratch.

## From scratch

1. Take what the user gives you — the idea, whatever they know, links, files.
   Ask for the basic idea if you do not have it; do not ask for more yet.
2. If it holds more than one outcome, propose the set of cards, one outcome line
   each, and let the user decide the set before you draft any. Where the set is
   a parent issue and its sub-issues, say so. Work through the remaining steps
   for each card.
3. Shape it into a draft from the template, as "Shape a draft" describes: the
   criteria numbered from `C1`, the parent line on a sub-issue, the work order
   on a parent issue with criteria only for what the combined result shows
   beyond its sub-issues' (never that every sub-issue is done, which is its
   outcome already), the suggested model and effort, and the values the
   profile's team modules recommend. Leave out what you do not know rather than
   inventing it. Write the draft to a scratch file, the title on the first line
   and the description below it, and run `devfactory criteria-ids --text <file>`;
   fix any duplicate ID it reports before measuring.
4. Measure the draft as "Measure" describes: start the `card-reviewer` agent by
   name with the Agent tool for one fresh review, then request grilling, asking
   the user each question it raises and each open question on the draft, then at
   most one follow-up by a second `card-reviewer`.
   The agent runs on its own model; pass none. During creation nothing is recorded
   as comments; answers go straight into the draft.
5. Show the user the whole card, with each team field's value and reason, the
   verdict, anything the follow-up still found and the suggestions you left,
   and get their acceptance or changes. Changes the user asks for are folded in
   and shown to them again; they do not reopen the review.
6. Once accepted, create the card on the profile's board exactly as accepted,
   wherever the board puts a new card, each part in the field
   the profile maps it to, marked as a parent issue or a sub-issue as the
   binding says, with a parent's sub-issue order set to match its work order.
   Attach any files the user provided, and verify it by reading it back, with
   `devfactory criteria-ids --card <id>` confirming its criterion IDs (on a
   tracker `gh` does not reach, `--text` with the card as read back). A new
   sub-issue of an existing parent changes that parent's work order: make that
   change through `add-to-card` on the parent.
7. If the card meets the Definition of Request, write the request receipt as
   "Write the request receipt" in `working-a-card.md` says, fire `request-met` as
   "Request grilling" there says, and tell the user the next step is `grill`; do
   not run it. Otherwise tell the user what keeps it short.
8. Run `devfactory end create-card`.

## From an existing card

1. Read the existing card in full, as "Read a card" describes.
2. Reshape everything already on it — description, criteria and comments — into
   the template, as "Shape a draft" describes. That existing content is treated
   as creation: it is not recorded as new comments. Write the criteria afresh
   from the outcome; do not edit the old ones into shape, and give them IDs as
   "From an existing card" in `card-process.md` says, then check them as step 3
   of "From scratch" does, with `criteria-ids --text`. Read each part from
   wherever the card holds it now, and fold everything in. Apply the profile's team modules to the reshaped card.
3. Measure the reshaped card as "Measure" describes: start the `card-reviewer`
   agent by name with the Agent tool for one fresh review, then request
   grilling, asking the user each question it raises and each open question on
   the card, then at most one follow-up by a second
   `card-reviewer`. The agent runs on its own model; pass none. Each question
   you ask and the user's answer are new additions to an existing card: record
   the question and the answer, in the user's own words, as a comment on the
   card, then fold the answer in.
4. Show the user the rewritten card, with each team field's value and reason,
   the verdict, anything the follow-up still found and the suggestions you
   left, and get their acceptance or changes. A change they ask for that
   carries new information is a new addition too: record it as a comment, then
   fold it in. Changes the user asks for are folded in and shown to them again;
   they do not reopen the review.
5. Once accepted, write it to the same card exactly as accepted — never create
   a replacement — with each part in the field the profile maps it to, clearing
   any field a part has moved out of; attach any files the user provided, and
   verify it by reading it back, with `devfactory criteria-ids --card <id>`
   confirming its criterion IDs.
6. If the card now meets the Definition of Request, write the request receipt as
   "Write the request receipt" in `working-a-card.md` says. If it also has no
   spec line, fire `request-met` as "Request grilling" there says. When it does
   not meet the definition, tell the user what keeps it short.
7. If the card has a spec line whose spec status is `Ready` or `approved` and
   any part changed, fire `readiness-lost` for it, as `../../references/events.md`
   says. If the card has a spec line, re-derive the spec as "Re-derive the spec"
   describes, naming each part that changed. Otherwise, when it meets the
   Definition of Request, tell the user the next step is `grill`; do not run it.
8. Run `devfactory end create-card`.
