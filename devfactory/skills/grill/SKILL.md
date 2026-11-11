---
name: grill
description: Specification grilling. Turn a card that meets the Definition of Request into a Ready spec without changing the card — check the card against the Definition of Request first, draft the specification folder from the card, the code, the recorded decisions and the data population, have the readiness checker measure it, ask the requester each question that only the spec settles, hand back any that would change the card, stamp and commit it, point the card at it and fire the ready and approved events; for a parent issue, every sub-issue not yet Ready and then the parent itself — or bring an existing spec back in line after the card changed, or amend it for a question answered after Ready. Use when a card needs its spec, when a card with a spec has changed or its stamp no longer matches, and when a dispatcher hands over an answered question for a Ready spec.
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
  - Bash(git diff *)
  - Bash(git status *)
  - Bash(git rev-parse *)
  - Bash(git merge-base *)
---

# Grill a card into a Ready spec

Paths below are relative to this skill's directory. `devfactory` below means running the
plugin's script with `python`: the script is `${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`;
if that variable is empty in your shell, it is `../../scripts/devfactory.py` relative to
this skill's folder.

**Markers.** Run `devfactory begin grill` as your first action and `devfactory end grill`
as your last. Whenever you end your turn to wait for the requester's answer, or to report,
run `devfactory end grill` first, and `devfactory begin grill` again when you resume. The
tracker guard allows your card writes only while the marker is there, and the git guard
allows your spec commit onto the integration branch, and its fast-forward there, only
under it; so hold the marker through each spec commit and the spec line written after it,
and end it only once both are done. A marker expires after the profile's Marker lifetime
(12 hours by default), and `begin` refreshes it. Markers and the profile are found at the
repository (worktree) root, wherever the shell's working directory is.

Read these first, in full:

- `../../references/definition-of-request.md` — what the card must meet before you start,
  and why you never change it.
- `../../references/definition-of-ready.md` — the conditions the spec must meet.
- `../../references/events.md` — the events you fire.
- `../../agents/card-reviewer.md` — the `card-reviewer` agent you start at the request
  gate, its inputs and its report.
- `../../references/decision-line.md` — who decides what; it sorts every decision you meet.
- `../../references/spec-template.md` — the folder you write, the stamp and the gap entry.
- `../../references/profile-template.md` — what the profile holds and where.
- `../../references/card-standard.md` and every module under `../../references/modules/`;
  "The spec line" there is the line you write.
- `../../references/card-process.md` — "The spec" and "Updating a card".
- `../../references/working-a-card.md` — loading the profile and reading a card.
- `../../agents/readiness-checker.md` — the `readiness-checker` agent you start, its inputs
  and its report.

This skill is **specification grilling**. The spec is what development reads; the card
stays the request, and this skill never changes it. Grilling earns Ready, which
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

**The scope rule.** The spec asks for nothing beyond the card, as condition 3.4 of the
Definition of Ready says, in every mode. Grilling never changes the profile.

**The card rule.** Specification grilling never changes the card: no fold, no comment, no
field. Its one write to the card is the spec line, which is not part of the request. A
question whose answer would change the card (its outcome, a criterion, its scope or the
work order) is a **request question**: the request was not complete, so it is not yours to
ask. Hand it back to request grilling, as "Handing back a request question" says.

**The request gate.** Before you draft, revise or amend anything for a card, check that it
meets the Definition of Request. First compare its request receipt: write the card facts
file from the card as you read it, as step 1 of "Write the request receipt" in
`working-a-card.md` says, and run `devfactory receipt check <spec dir> --check request
--card <n> --facts <file>`. When it prints `match`, the card has not changed since a
reviewer found it meets the definition: go on, starting no reviewer. Otherwise start the
`card-reviewer` agent by name with the Agent tool, kind fresh, with every input its
definition lists, as "Measure" in `working-a-card.md` describes; it runs on its own model,
so pass none. Go on only when its verdict is that the card meets the Definition of Request,
and then write the request receipt with `devfactory receipt write`, the same arguments; it
is committed with the spec folder. Otherwise do nothing for that card: report each breach, question and open question the reviewer found, say the card goes
back to request grilling through `re-evaluate-card`, and stop work on it. Where the card
sits on the board never matters. For a parent issue, check the parent and every sub-issue
this run grills.

**Handing back a request question.** Collect every request question you meet; ask none and
fold none. Instead of stamping, leave the spec `drafting` and uncommitted, report each
request question with the options you know and your recommendation, and say that request
grilling settles them: the user answers them through `re-evaluate-card`, which records and
folds each answer, re-measures the card and fires `request-met` once it meets the
Definition of Request, and then runs `grill` again on the changed card.

**Firing an event.** Fire each event `events.md` gives this skill with
`devfactory event <name> --card <id>`, for each card it applies to, at the moment it says.
A hook that fails is reported to the requester with its output, and the work carries on.

**The review rule.** The readiness checker measures a spec once fresh, then at most once in
a follow-up. Whatever the follow-up still finds goes to the requester; there is no third
check, because a fresh checker finds something different every time and repeated rounds
never converge. Never measure a spec yourself.

**The criteria file.** The scripts that check criteria take them as a file of IDs, one per
line. Write it with `devfactory criteria-ids --card <n>` into a file outside the
repository; a non-zero exit means a duplicate criterion ID, a breach of the card standard:
stop work on that card and send it back to request grilling, as the request gate does.

**The card revision.** A card's revision is what `devfactory stamp --card <n>` prints,
never a hash you compute or a reading of the card. For a card the script cannot read with
`gh`, write its text to a file as "The stamp" in `spec-template.md` lays it out (the title on
the first line, then the body, then each other field the profile writes a part to) and pass
`--text <file>` in place of `--card <n>`.

**Dispatching the checker.** First run `devfactory spec-lint <spec dir> --criteria <file>`
on every spec the check covers, and fix every finding it reports before going on. Then start
the `readiness-checker` agent by name with the Agent tool; it carries its own definition,
tools and model. Pass every input that definition requires:

- the path to the plugin's references folder (`../../references/`);
- the repository path, the branch to read and its head commit: the integration branch
  before development, the card's own branch during it;
- for each card checked, its ID, its current text as the tracker holds it, its revision
  from `devfactory stamp`, and its stage, which is the point the work is at (Grilling before
  approval, Development during a build), never its board column; for a parent issue, the
  parent and every
  sub-issue, saying which are released;
- each card's spec folder path, and the profile path;
- the gap sources to read first: the project ledger `.devfactory/gaps.md` and every live
  `gaps.md` under the profile's specs path;
- the moment: at creation, or at development start;
- the kind: **fresh**, with nothing about earlier checks; **follow-up**, with the fresh
  check's report and the spec version it measured, re-checking those findings and the
  changed text only; or **re-derive**, with the conditions this re-derivation re-runs.

**Asking the requester.** A question first passes "Before anything is asked" in
`../../references/decision-line.md`: a standing answer that settles it is followed and
cited, and one on the developer's side is delegated, not asked. Ask one question at a
time. Each question says what you need to
know and why the spec needs it, gives the options, and puts your recommendation first with a
one-line reason. When several cards share a gap, ask for the rule once, not the case per card.
Never invent an answer. A question the requester cannot answer yet stays open in your report
and keeps the spec `drafting`; it is never written onto the card.

**Folding an answer.** Every answer you take goes into the spec section it settles, and
only there. You ask only questions whose answers leave the card as it is: edge behaviour the
card leaves to the tests, an owner step's moment, a choice between ways of delivering the
same outcome. Any other is a request question, handed back as the card rule says.

**The stamp.** Its three header rows are defined in `../../references/spec-template.md`
under "The stamp". The Card revision is the output of `devfactory stamp`, run after the last
write to the card, since every fold changes the text. The Repo commit is the branch head the
last check reported reading; Amend, which runs no check, keeps the Repo commit it found. Run
`devfactory spec-lint <spec dir> --criteria <file>` after stamping and before every commit of
the spec folder, and fix every finding first.

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
   answers. Leave the card wherever it is on the board.
2. **Read the card** in full, every comment with its date and author included, as "Read a
   card" in `working-a-card.md` says. For a sub-issue, read its parent too; for a parent,
   read every sub-issue. Then apply the request gate, and go on only when the card meets
   the Definition of Request.
3. **Read where the card's subject lives**: the code, configuration and data the change
   touches in the repository, and the recorded decisions the profile points to that bear on
   it. This is grounding for how to deliver the card, not material for the card or a
   source of further work for the spec.
4. **Read the gap sources**: the project ledger `.devfactory/gaps.md`, whose entries carry
   the released card's ID, and every live `gaps.md` under the profile's specs path. Note
   each class of question that recurs, and settle that class for this card up front rather
   than letting it reach development.
5. **Draft `spec.md`** from `spec-template.md` at `<specs path><card>/`, filling every
   section; a section the template allows to drop goes only when it has nothing to say.
   Cite criteria by their IDs on the card. Version 1 covers everything up to the spec's
   first commit, and the status is `drafting`. While drafting:
   - Stay inside the card. Before adding anything, ask whether it goes beyond what the card
     asks for; if it does, leave it out. The spec never expands scope, and never asks the
     requester whether to.
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
     something already answers it, so note it as a question; it is a request question
     unless the card already says what such rows end up as. When the profile states no
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
   noted in step 5, merged where they are the same question, as "Asking the requester" says,
   except each request question, which you collect as the card rule says. For each owner
   step the checker reports without a moment, agree its moment with the requester the same
   way. Fold each answer as "Folding an answer" says. Fix every finding that needs no one's
   answer in the spec, cutting or narrowing text before adding any. A work-order fault, and
   any finding only a change to the card would fix, is a request question. None of these
   answers is a gap: the spec has not yet earned Ready.
8. **Check, follow-up.** Dispatch the readiness checker once more, kind follow-up. Ask the
   requester about whatever it still finds, and fold the answers, without another check.
9. **Lint and stamp.** Steps 9 to 11 run in one stretch under the `grill` marker you
   already hold: lint, stamp, commit, spec line, and only then `end`. Run
   `devfactory spec-lint <spec dir> --criteria <file>` and fix every finding. Then stamp
   the spec as "The stamp" says: the Card revision from `devfactory stamp`, the Repo commit
   the follow-up reported, today's date. Set its status to `Ready` when the follow-up found
   nothing open, or when the requester settled everything it found; otherwise it stays
   `drafting`. When you collected any request question, stamp and commit nothing: hand
   them back as "Handing back a request question" says, and go to step 12. Otherwise, when
   the status is `Ready`, write the ready receipt: list, one per line, the folder of every
   spec the follow-up measured, and run `devfactory receipt write <spec dir> --check ready
   --specs <file>`.
10. **Commit** the spec folder, and nothing else, as its own commit, once the lint "The
    stamp" requires is clean. The commit lands directly on the integration branch when the
    profile's branches and merging allows a direct commit there; otherwise it is made on a
    branch that is then fast-forwarded onto the integration branch, which the git guard
    allows under `grill`'s marker.
11. **Point the card at the spec.** When the spec is Ready, write the spec line with that
    commit, as "The spec line" says, then fire `ready`. Only now may you run
    `devfactory end grill` to report or ask.
12. **Report** that the spec is Ready, with its path and commit, or name each thing still
    open: a request question handed back, a question, an owner step without a moment, or
    a failing condition.
13. **Approval.** Once Ready, ask the requester to approve the Ready spec, once, as one
    question: approve it, or say what to change. On approval, set the status to `approved`,
    commit that change on its own, landing as step 10 says, write the spec line with the
    new commit, under the marker, and fire `approved`. A change asked for at approval is a
    gap, at stage Approval. When it changes only the spec, handle it through Amend: the
    requester's words are the answer, the amendment and gap entry are written, the affected
    conditions are re-checked as Amend says, and approval is asked again. When it would
    change the card, it is a request question: write nothing, end this run, and report it
    with the requester's words, saying that request grilling folds it into the card
    through `re-evaluate-card`, after which `grill` re-derives the spec from the changed
    card and asks for approval again.

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
3. **Approval covers the set.** Approval is asked only when every sub-issue is Ready and the
   parent is Ready, and one approval question covers them all. On approval, set every spec
   in the set to `approved`, commit, write each card's spec line and fire `approved` for
   each card, as New step 13 says. `ready` fires for each card as its spec is made Ready.

## Re-derive

1. **Load the profile and read the card** as New steps 1 and 2 say, the request gate
   included, and read the spec folder in full.
2. **Find what changed.** Take the changed parts from the dispatcher. When only
   `devfactory stamp-check --card <n> --spec <spec dir>` says the card changed, compare the card's current text with the revision the stamp
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
   follow-up as New steps 7 and 8 say, handing back any request question as the card rule
   says. When the caller runs the readiness check itself, as
   `check-ready` does, skip this step and leave the check to it; the caller passes the
   branch head its check reported, and the re-stamp records that head.
6. **Re-stamp, record and commit.** Bump the version and add a row to "Amendments" naming the
   changed card parts that drove it. Re-stamp as "The
   stamp" says, the Card revision from `devfactory stamp`. When step 5's own check found the
   spec Ready, write the ready receipt as New step 9 says. Commit the spec folder on its own on the branch it lives on: the
   integration branch before development, landing as New step 10 says, the card's own
   branch during it. Write the spec line with that commit, under the marker. Before
   development, when the re-stamped spec's status is `Ready`, fire `ready` for the card.
   During development fire nothing: the work has not changed hands.
7. **Report** what changed in the spec and whether it is still Ready.

## Amend

Amend runs only after the spec has earned Ready. A question answered before then is folded
by New or Re-derive and is not a gap.

1. **Load the profile** and read the card and the spec folder in full, on the branch the
   spec lives on now. When the answer changes the card, its dispatcher has already put it
   there through `add-to-card`, as request grilling's fold: apply the request gate to the
   changed card, and when the card does not carry the answer, stop and report it.
2. **Write the amendment**: the answer goes into the spec section it settles. Never write
   the card.
3. **Add the gap entry** with `devfactory gaps add <spec dir> --stage <stage> --question
   <question> --condition <condition> --resolved <version>`, each value quoted as one
   argument: the stage the work is at (Approval, Development, Done or Acceptance), the
   question as asked, the condition the dispatcher named as having let it through, and the
   new version as what resolved it. The script writes the date and the form
   `spec-template.md` lays out; never write the entry by hand.
4. **Bump the version** and add the "Amendments" row, driven by the gap.
5. **Re-stamp** the Card revision, from `devfactory stamp`, and the date, as "The stamp"
   says, commit the spec folder on its own on the current branch, and write the spec line
   with that commit.
6. **Report** the amendment, its version, whether the card had changed, and whether the answer
   changes what another card depends on, so the work order is re-checked.
