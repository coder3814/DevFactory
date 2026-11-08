---
name: grill
description: Turn a card into a Ready spec — draft the specification folder from the card, the code, the recorded decisions and the data population, have the readiness checker measure it, ask the requester each open question once, stamp and commit it and point the card at it; for a parent issue, every sub-issue not yet Ready and then the parent itself — or bring an existing spec back in line after the card changed, or amend it for a question answered after Ready. Use when a card needs its spec, when a card with a spec has changed or its stamp no longer matches, and when a dispatcher hands over an answered question for a Ready spec.
---

# Grill a card into a Ready spec

Paths below are relative to this skill's directory.

Read these first, in full:

- `../../references/definition-of-ready.md` — the conditions the spec must meet.
- `../../references/decision-line.md` — who decides what; it sorts every decision you meet.
- `../../references/spec-template.md` — the folder you write, the stamp and the gap entry.
- `../../references/profile-template.md` — what the profile holds and where.
- `../../references/card-standard.md` and every module under `../../references/modules/`;
  "The spec line" there is the line you write.
- `../../references/card-process.md` — "The spec" and "Updating a card".
- `../../references/working-a-card.md` — loading the profile and reading a card.
- `../../agents/readiness-checker.md` — the agent you dispatch, its inputs and its report.

The spec is what development reads; the card stays the request. Grilling earns Ready, which
means a fresh agent could build the card to Done without asking anything. It does not earn
approval: the requester approves the Ready spec once, at the Approval stage, and judges
intent once at acceptance.

## Modes

The dispatcher, or the state of the card, says which mode runs:

- **New**: the card has no spec yet. On a parent issue, New runs as "A parent issue" says.
- **Re-derive**: the card has a spec, and either the dispatcher names the card parts that
  changed or the spec's stamp no longer matches the card. Re-derive is for card changes, not
  for answers.
- **Amend**: the spec has earned Ready, and the dispatcher hands over a question the spec did
  not answer, the requester's answer, and the Ready condition that let it through.

## Rules that hold in every mode

**The review rule.** The readiness checker measures a spec once fresh, then at most once in
a follow-up. Whatever the follow-up still finds goes to the requester; there is no third
check, because a fresh checker finds something different every time and repeated rounds
never converge. Never measure a spec yourself.

**Dispatching the checker.** Start it as a separate agent, with read-only tools where you can
limit them, on the model the card's Suggested model and effort names (for a parent issue, the
parent's), or the profile's default model and effort when the card names none. Tell it to
follow `../../agents/readiness-checker.md` exactly, and pass every input that definition
requires:

- the path to the plugin's references folder (`../../references/`);
- the repository path, the branch to read and its head commit: the integration branch
  before development, the card's own branch during it;
- for each card checked, its ID, its current text as the tracker holds it, its revision
  computed as "The stamp" in `spec-template.md` says, and its stage; for a parent issue, the
  parent and every sub-issue, saying which are released;
- each card's spec folder path, and the profile path;
- the gap sources to read first: the project ledger `.devfactory/gaps.md` and every live
  `gaps.md` under the profile's specs path;
- the moment: at creation, or at development start;
- the kind: **fresh**, with nothing about earlier checks; **follow-up**, with the fresh
  check's report and the spec version it measured, re-checking those findings and the
  changed text only; or **re-derive**, with the conditions this re-derivation re-runs.

**Asking the requester.** Ask one question at a time. Each question says what you need to
know and why the spec needs it, gives the options, and puts your recommendation first with a
one-line reason. When several cards share a gap, ask for the rule once, not the case per card.
Never invent an answer. A question the requester cannot answer yet becomes an open question
on the card, which keeps the spec short of Ready (condition 2.3).

**Folding an answer.** Every answer goes into the spec section it settles. It goes into the
card as well only when it changes observable behaviour or scope, as `decision-line.md`
draws them, or the work order. Every card write you make goes through the `add-to-card`
skill in **settled** mode with **no-rederive**: the requester's answer is the acceptance, so
it records the answer as the comment, folds, writes, verifies and reports the folded text,
and the requester may object afterwards; no-rederive, because you carry the spec forward
yourself. Say which answers were folded into the card and which only into the spec.

**The stamp.** Its three header rows, and how the card revision is computed, are defined in
`../../references/spec-template.md` under "The stamp"; every skill and agent that compares a
card with a stamp uses that definition. The Card revision is the card's revision after the
last write to the card, since every fold changes the text. The Repo commit is the branch head
the last check reported reading; Amend, which runs no check, keeps the Repo commit it found.

**The spec line.** The card carries exactly one spec line, the last line of its description
body, in the form `Spec: <path> @ <commit>`, where the commit is the spec folder's own
commit, as "The spec line" in `card-standard.md` says. The stamp excludes it. Write it
directly through the tracker binding, never through `add-to-card`: it is your one direct card
write, not an addition, so no comment is recorded, it folds into no section and it starts no
re-derivation. Replace any existing spec line rather than adding a second, and read the card
back to confirm the line landed. The line is first written once the spec is Ready; after
that, every time you commit the spec folder, write the line again with that commit.

## New

1. **Load the profile** as "Load the project profile" in `working-a-card.md` says, with its
   specs path, recorded decisions path, environments, data access, concern extensions,
   owner-step types, wireframe fidelity, branches and merging, sessions and standing
   answers. Move the card to the Grilling stage's column, unless it is already there.
2. **Read the card** in full, every comment with its date and author included, as "Read a
   card" in `working-a-card.md` says. For a sub-issue, read its parent too; for a parent,
   read every sub-issue.
3. **Read where the card's subject lives**: the code, configuration and data the change
   touches in the repository, and the recorded decisions the profile points to that bear on
   it. This is grounding for the spec, not material for the card.
4. **Read the gap sources**: the project ledger `.devfactory/gaps.md`, whose entries carry
   the released card's ID, and every live `gaps.md` under the profile's specs path. Note
   each class of question that recurs, and settle that class for this card up front rather
   than letting it reach development.
5. **Draft `spec.md`** from `spec-template.md` at `<specs path><card>/`, filling every
   section; a section the template allows to drop goes only when it has nothing to say.
   Cite criteria by their IDs on the card. Version 1 covers everything up to the spec's
   first commit, and the status is `drafting`. While drafting:
   - Sort every decision the work needs by `decision-line.md`. One a recorded decision, the
     profile, a design system or an existing pattern already answers is followed, and the
     source named. One on the developer's side goes under "Decisions delegated to the
     developer". One on the requester's side that nothing answers is not decided: note it
     as a question for step 7.
   - Follow every standing answer that applies, and list it under "Project bindings used".
   - When the card's rules act on existing data, run them read-only against that population
     through the access the profile's "Data access" section states for it, and record the
     population, the point in time, the count per rule, and each row or class of rows no
     rule covers. What an uncovered row ends up as is the requester's decision unless
     something already answers it, so note it as a question. When the profile states no
     access for the population, or the only access would write, run nothing; note it as a
     question for the requester, since the profile lacks the entry `configure-project` adds.
   - Derive the interface determination from the card as it now stands: non-trivial,
     trivial because, or not applicable because. When non-trivial, produce `wireframe.*`
     beside `spec.md` at the profile's wireframe fidelity, and get the requester's approval
     of it, in the project's own design-review way when the profile names one, before the
     checker runs. Record the approval date under "Interface surface".
   Commit nothing yet.
6. **Check, fresh.** Dispatch the readiness checker as "Dispatching the checker" says, kind
   fresh, at creation. At creation the spec has no stamp, so the checker marks 9.2 not
   applicable and reports the card revision and branch head it checked.
7. **Ask.** Put to the requester every question the checker reported and every question you
   noted in step 5, merged where they are the same question, as "Asking the requester" says.
   For each owner step the checker reports without a moment, agree its moment with the
   requester the same way. Fold each answer as "Folding an answer" says. Fix every finding
   that needs no one's answer, cutting or narrowing text before adding any. Put each
   work-order fault to the requester with the fix you propose, as a question; their
   agreement is the answer, and the fix goes through `add-to-card`, settled with
   no-rederive, recording the fault and the agreed fix. None of these answers is a gap: the spec has not
   yet earned Ready.
8. **Check, follow-up.** Dispatch the readiness checker once more, kind follow-up. Ask the
   requester about whatever it still finds, and fold the answers, without another check.
9. **Stamp** the spec as "The stamp" says, with the branch head the follow-up reported. Set
   its status to `Ready` when the follow-up found nothing open, or when the requester settled
   everything it found; otherwise it stays `drafting`.
10. **Commit** the spec folder, and nothing else, as its own commit, landing on the
    integration branch the way the profile's branches and merging section says work lands
    there.
11. **Point the card at the spec.** When the spec is Ready, write the spec line with that
    commit, as "The spec line" says.
12. **Report** that the spec is Ready, with its path and commit and the answers folded into
    the card, or name each thing still open: the question, the owner step without a moment,
    or the failing condition.
13. **Approval.** Once Ready, move the card to the Approval stage's column and ask the
    requester to approve the Ready spec, once, as one question: approve it, or say what to
    change. On approval, set the status to `approved`, commit that change on its own and
    write the spec line with the new commit. A change asked for at approval is a gap, at
    stage Approval, handled through Amend: the requester's words are the answer, the
    amendment and gap entry are written, the card is folded through `add-to-card` where the
    change alters observable behaviour or scope, the affected conditions are re-checked as
    Amend says, and approval is asked again.

## A parent issue

`grill` on a parent issue grills the whole set:

1. **Each sub-issue not yet Ready** gets its own spec, by New steps 1 to 12, or by Re-derive
   when it has a spec whose stamp no longer matches. Ask a gap several sub-issues share once,
   as the rule, and dispatch the checker over several sub-issues together where that finds
   what they share.
2. **Then the parent's own spec**, by New steps 1 to 12, holding what no single sub-issue
   carries: its dispositions, an evidence row for each parent criterion, the owner steps of
   the run, and the project bindings it relies on. The checker measures the parent and every
   sub-issue together, which is what tests the work order (condition 8.2).
3. **Approval covers the set.** The parent and its sub-issues move to the Approval stage's
   column only when every sub-issue is Ready and the parent is Ready, and one approval
   question covers them all. On approval, set every spec in the set to `approved`, commit,
   and write each card's spec line, as New step 13 says.

## Re-derive

1. **Load the profile and read the card** as New steps 1 and 2 say, without moving the card,
   and read the spec folder in full.
2. **Find what changed.** Take the changed parts from the dispatcher. When only the stamp
   says the card changed, compare the card's current text with the revision the stamp
   records, from the tracker's revision history where it keeps one, and otherwise treat
   every part as changed.
3. **Choose the conditions to re-run.** A change to a scope boundary, or one that changes the
   interface determination, re-grounds the whole spec: run New steps 3 to 5 on the existing
   spec, keeping its version history and its criterion IDs, then continue at step 5 below.
   Otherwise re-run only the conditions the changed parts feed:

   | Changed part | Ready conditions it feeds |
   |---|---|
   | Title, summary, the issue or request | 1, 9.3 |
   | What needs to be achieved, acceptance criteria | 1.2, 2, 3.2, 4.2, 4.3, 5, 6.1, 7, 9.3 |
   | Supporting information | 3.2, 4.2, 9.1, 9.3 |
   | Open questions | 2.3, and whatever the answered question changed |
   | Work order, or a sub-issue added or removed | 8.2, 9.3 for the parent |
   | Suggested model and effort | none |

   Condition 6.1 is re-derived on every criterion change, never carried over. Condition 9.2
   is not applicable in a re-derive check, because the card has changed against the old
   stamp by definition; the new stamp replaces it.
4. **Revise** the spec sections those conditions read, as New step 5 says.
5. **Check.** Dispatch the readiness checker as "Dispatching the checker" says, kind
   re-derive, naming the conditions this re-derivation re-runs; ask, fold and run the one
   follow-up as New steps 7 and 8 say. When the caller runs the readiness check itself, as
   `check-ready` does, skip this step and leave the check to it; the caller passes the
   branch head its check reported, and the re-stamp records that head.
6. **Re-stamp, record and commit.** Bump the version and add a row to "Amendments" naming the
   changed card parts, or the change asked for at approval, that drove it. Re-stamp as "The
   stamp" says, and commit the spec folder on its own on the branch it lives on: the
   integration branch before development, the card's own branch during it. Write the spec
   line with that commit.
7. **Report** what changed in the spec and whether it is still Ready.

## Amend

Amend runs only after the spec has earned Ready. A question answered before then is folded
by New or Re-derive and is not a gap.

1. **Load the profile** and read the card and the spec folder in full, on the branch the
   spec lives on now.
2. **Write the amendment**: the answer goes into the spec section it settles, and into the
   card as "Folding an answer" says, when it changes observable behaviour, scope or the work
   order.
3. **Add the gap entry** to the spec's `gaps.md` as `spec-template.md` lays it out: the date,
   the card's current stage (Approval, Development, Done or Acceptance), the question as
   asked, the condition the dispatcher named as having let it through, and the new version
   as what resolved it.
4. **Bump the version** and add the "Amendments" row, driven by the gap.
5. **Re-stamp** the Card revision and date as "The stamp" says, commit the spec folder on
   its own on the current branch, and write the spec line with that commit.
6. **Report** the amendment, its version, whether the card changed, and whether the answer
   changes what another card depends on, so the work order is re-checked.
