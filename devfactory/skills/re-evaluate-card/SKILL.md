---
name: re-evaluate-card
description: Re-evaluate an existing card against the card standard — check its title, description and acceptance criteria, fold in whatever in its comments changes the outcome, grill the user about any gap, say when the card has moved on since its spec was stamped, and re-derive the spec for whatever changed — or restructure a parent issue that still carries criteria, supporting information or any other part beyond its four. Use when the user asks to re-evaluate, check, review or audit a card against the standard, for instance after editing it by hand or after others have commented on it, or when another skill says a parent issue goes through re-evaluate-card first.
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

# Re-evaluate a card

Paths below are relative to this skill's directory. `devfactory` below means running the
plugin's script with `python`: the script is `${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`;
if that variable is empty in your shell, it is `../../scripts/devfactory.py` relative to
this skill's folder. Read the tracker with `gh issue view`, `gh project item-list`,
`gh api -X GET` or `az boards work-item show`, as the profile's binding says; those reads
and the script run without a permission prompt.

**Markers.** Run `devfactory begin re-evaluate-card` as your first action and
`devfactory end re-evaluate-card` as your last. Whenever you end your turn to wait for the
user's answer, decision or acceptance, or stop for any reason, such as finding no profile,
run `devfactory end re-evaluate-card` first, and `devfactory begin re-evaluate-card` again
when you resume. The tracker guard allows your card writes only while the marker is there.
A marker expires after the profile's Marker lifetime (12 hours by default), and `begin`
refreshes it. Markers and the profile are found at the repository (worktree) root,
wherever the shell's working directory is. When `begin` prints `plugin-changed`, load this
skill again before you continue.

Read these first, in full. A file you have already read in full in this session, under
the plugin version `begin` printed, need not be read again.

- `../../references/card-standard.md` and every module it lists
- `../../references/card-process.md` — the "Re-evaluating a card", "Folding"
  and "The spec" sections are the procedure you are carrying out.
- `../../references/working-a-card.md`
- `../../references/card-template.md`
- the "Inputs" section of `../../agents/card-reviewer.md`, and only that section — what
  you give the `card-reviewer` agent you start.
- `../../references/definition-of-request.md` — what the card must meet before a
  spec is written from it.
- `../../references/events.md` — the `request-met` event you fire.

This skill is for two things only: an audit of a card that the user asks for, and
restructuring a parent issue that still carries criteria, supporting information or any
other part beyond its four, as "A parent issue to restructure" below says. It takes no answer handed over
by another skill; an answer the requester has already given goes through `add-to-card`.

Re-evaluation checks the card as it stands, whatever has changed on it and however. It
does not try to work out what was edited, and it records nothing about a direct edit to
the card's details: the edit is itself the change.

1. **Begin.** Run `devfactory begin re-evaluate-card`.
2. **Read the card** in full, comments included, as "Read a card" describes,
   after loading the profile as "Load the project profile" describes, and run
   `devfactory criteria-ids --card <id>` (on a tracker `gh` does not reach,
   `--text` with the card as read); a duplicate ID it reports counts as a breach
   in step 3 whatever the review finds. When the card is a parent issue that
   carries anything beyond the parts "Parent issues" in the card standard lists,
   follow "A parent issue to restructure" instead of the steps below. A parent
   has no spec: leave a spec line still on it where it is, since `grill`, run for
   the parent, removes it with the old spec files. If the card is not a parent and
   has a spec line, run
   `devfactory stamp-check --card <id> --spec <spec folder>`, which decides Ready
   condition 9.2 in `../../references/definition-of-ready.md`. If it prints
   `changed`, tell the user, before measuring, that the card has changed since its
   spec was stamped Ready, quoting the line.
3. **Measure** it against the standard, including whether the description and
   criteria carry what in the comments changes the outcome and contradict none
   of them: start the `card-reviewer` agent by name with the Agent tool, as
   "Measure" describes. This first review is fresh, and the follow-up in step 6
   is a second `card-reviewer`; each runs on its own model, so pass none. If it
   finds no breach, no question and no open question, tell the user the card
   meets the standard and the Definition of Request, with any suggestions it
   made, change nothing on the card, and go to step 9. Otherwise carry on with
   the steps below.
4. **Fold in** any comment whose outcome-changing content is missing. The
   comment is already the record, so add no comment of your own for it. Keep
   every criterion's ID as "Fold" describes.
5. **Request grilling.** Ask the user about each remaining gap and each open
   question on the card, as "Request grilling" describes. Their answers are new
   additions: record each question and answer as a comment, then fold the
   answer in.
6. **Measure again** as "Measure" describes — one follow-up review by a second
   `card-reviewer`, with whatever it still finds going to the user at
   acceptance.
7. **Accept.** Show the user the rewritten sections, any changed team field
   with its reason, the verdict, anything
   the follow-up still found and the suggestions you left, and get their
   acceptance or changes. A change they ask for that carries new information is
   a new addition: record it as a comment, then fold it in. Changes the user
   asks for are folded in and shown to them again; they do not reopen the
   review.
8. **Write and verify.** Once accepted, write the sections and read the card back
   to confirm every write landed, with `devfactory criteria-ids --card <id>`
   confirming its criterion IDs when the criteria changed.
9. **Write the request receipt** when the card meets the Definition of Request,
   as "Write the request receipt" in `working-a-card.md` says.
   **Fire `request-met`** when the card has no spec line and meets the Definition
   of Request, whether or not this re-evaluation changed it, as "Request
   grilling" in `working-a-card.md` says. When it does not meet the definition,
   tell the user what keeps it short.
   **Re-derive the spec.** If the card has a spec line and any part changed —
   in this re-evaluation, or since the stamp when step 2 found the card ahead
   of it — hand to `grill` Re-derive as "Re-derive the spec" describes, naming
   each part that changed, and say when the interface determination or a scope
   boundary is among them; `grill` fires whatever event its outcome calls for.
   Report what changed in the spec. If nothing changed, leave the spec alone.
   A parent issue that still has a spec line is not re-derived: tell the user
   that `grill`, run for the parent, removes the line with the old spec files.
10. **End.** Run `devfactory end re-evaluate-card`.

## A parent issue to restructure

A parent issue that carries anything beyond its title, purpose, work order and
suggested model and effort is brought to "Parent issues" in the card standard with the
requester. Read every sub-issue too, as "Read a card" describes.

1. **Sort what the parent carries.** For each criterion, decide whether it states
   something only the combined result shows. Each that does moves to the sub-issue that
   completes it; each that only restates the outcome, that every sub-issue is done,
   merged, reviewed or passing the tests together, is dropped. Ask the user where the
   sort or the completing sub-issue is not clear from the cards, as "Request grilling"
   describes. Every other part beyond the four is dropped.
2. **Shape the parent** from the parent skeleton in the template: its title, a purpose
   drawn from what it held, a work order naming each sub-issue once by its number with
   its waits, a sub-issue that receives a moved criterion waiting on the ones it needs,
   and the suggested model and effort for the session that coordinates the run. Leave
   any spec line on it where it is: this skill never writes it, and `grill`, run for the
   parent in step 7, removes it with the old spec files.
3. **Shape each receiving sub-issue.** A moved criterion is a new addition to that
   sub-issue: record it there as a comment naming the parent it came from, then fold it
   in, with the next criterion ID above the highest that sub-issue has ever carried.
4. **Measure** the parent and each changed sub-issue as steps 3 and 6 above do, one
   fresh review and at most one follow-up each.
5. **Accept.** Show the user the restructured parent, what was dropped from it, and each
   changed sub-issue's rewritten sections, with the verdicts, and get their acceptance
   or changes, as step 7 above says. Each sub-issue's change is a card change the user
   accepts like any rewrite.
6. **Write and verify** every card as step 8 above says, then write the request receipt
   and fire `request-met` for each card as step 9 says.
7. **Hand to `grill`** for the parent. It removes the old spec files and any spec line still on the
   parent, and brings each
   changed sub-issue's spec along. Then run `devfactory end re-evaluate-card`.
