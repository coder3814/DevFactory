---
name: grill
description: Specification grilling. Turn a card that meets the Definition of Request into a Ready spec without changing the card — check the card against the Definition of Request first, draft the specification folder from the card, the code, the recorded decisions and the data population, have the readiness checker measure it, ask the requester each question that only the spec settles, hand back any that would change the card, stamp and commit it, point the card at it and fire the ready and approved events; for a parent issue, which has no spec, every sub-issue not yet Ready and then the set check through check-ready — or bring an existing spec back in line after the card changed, or amend it for an answer given after Ready that leaves the card as it is. Use when a card needs its spec, when a card with a spec has changed or its stamp no longer matches, and when a dispatcher hands over an answered question for a Ready spec.
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
repository (worktree) root, wherever the shell's working directory is. When `begin` prints
`plugin-changed`, load this skill again before you continue.

Read these first, in full:

A file you have already read in full in this session, under the plugin version `begin`
printed, need not be read again.

- `../../references/definition-of-request.md` — what the card must meet before you start,
  and why you never change it.
- `../../references/definition-of-ready.md` — the conditions the spec must meet.
- `../../references/events.md` — the events you fire.
- `../../agents/card-reviewer.md`, its Inputs section only — the `card-reviewer` agent you
  start at the request gate.
- `../../references/decision-line.md` — who decides what; it sorts every decision you meet.
- `../../references/spec-template.md` — the folder you write, the stamp and the gap entry.
- `../../references/spec-procedure.md` — the passages this skill shares with `check-ready`:
  dispatching the checker, asking the requester, folding an answer, a card-changing answer,
  the ready receipt and landing a commit.
- `../../references/profile-template.md` — what the profile holds and where.
- `../../references/card-standard.md` and every module under `../../references/modules/`;
  "The spec line" there is the line you write.
- `../../references/card-process.md` — "The spec" and "Updating a card".
- `../../references/working-a-card.md` — loading the profile and reading a card.
- `../../agents/readiness-checker.md`, its Inputs section only — the `readiness-checker`
  agent you start.

This skill is **specification grilling**. The spec is what development reads; the card
stays the request, and this skill never changes it. Grilling earns Ready, which
means a fresh agent could build the card to Done without asking anything. It does not earn
approval: the requester approves the Ready spec once, at the Approval stage, and judges
intent once at acceptance.

## Modes

The dispatcher, or the state of the card, says which mode runs:

- **New**: the card has no spec yet. A parent issue has no spec of its own: `grill` run for
  one works its set, as "A parent issue" says.
- **Re-derive**: the card has a spec, and the card changed: the dispatcher names the card
  parts that changed, or the spec's stamp no longer matches the card. A card-changing answer,
  once `add-to-card` has folded it, is brought along here.
- **Amend**: the spec has earned Ready, and the dispatcher hands over a question the spec did
  not answer, the requester's answer, which leaves the card as it is, and the condition that
  let it through; or a developer-side finding past the review limit, in the form Amend's
  opening gives.

## Rules that hold in every mode

**The scope rule.** The spec asks for nothing beyond the card, as condition 3.4 of the
Definition of Ready says, in every mode. Grilling never changes the profile.

**The card rule.** Specification grilling never writes the card: no fold, no comment, no
field. Its one write to the card is the spec line, which is not part of the request. A
question whose answer would change the card (its outcome, a criterion, its scope or the
work order) is a **request question**: the request was not complete, so it is not yours to
ask. Hand it back, as "Handing back a request question" says. A change the card needs
reaches it only through `add-to-card` in settled mode: a requester's answer as "A
card-changing answer" in `spec-procedure.md` says, and a breach of the card's own
consistency as the request gate says.

**The request gate.** Before you draft, revise or amend anything for a card, check that it
meets the Definition of Request. First compare its request receipt: write the card facts
file from the card as you read it, as step 1 of "Write the request receipt" in
`working-a-card.md` says, and run `devfactory receipt check <spec dir> --check request
--card <n> --facts <file>`. When it prints `match`, the card has not changed since a
reviewer found it meets the definition: go on, starting no reviewer. Otherwise start the
`card-reviewer` agent by name with the Agent tool, kind fresh, with every input its Inputs
section lists, as "Measure" in `working-a-card.md` describes; it runs on its own model, so
pass none.

- When its verdict is that the card meets the Definition of Request, write the request
  receipt with `devfactory receipt write`, the same arguments; it is committed with the spec
  folder, or, for a parent card, on its own as "Landing a commit" in `spec-procedure.md`
  says. When the card has no spec line, fire `request-met` for it. Then go on.
- A breach that needs no one's answer, such as a stale reason for the suggested model and
  effort or a sub-issue missing from the work order, is the card's own consistency: fix it
  through `add-to-card` in settled mode, stating the fix and passing `no-rederive`, and
  measure the card once more, as above, without entering Re-derive a second time.
- Only a breach that needs the requester's answer stops the card. Do nothing more for it:
  report each such breach, question and open question the reviewer found, and hand them
  back as "Handing back a request question" says.

Where the card sits on the board never matters. For a parent issue, check the parent card
and every sub-issue this run grills.

**Handing back a request question.** Collect every request question you meet; ask none and
fold none. Instead of stamping, leave the spec `drafting` and commit nothing, report each
request question with the options you know and your recommendation, and say that the
requester's answer changes the card. When the requester answers, the skill that receives the
answer takes it as "A card-changing answer" in `spec-procedure.md` says, which brings the
spec along by Re-derive, or, for a spec never yet committed, by New from step 2 on the
changed card.

**Firing an event.** Fire each event `events.md` gives this skill with
`devfactory event <name> --card <id>`, for each card it applies to, at the moment the step
below names, and no other. A hook that fails is reported to the requester with its output,
and the work carries on.

**The passages shared with `check-ready`.** "The criteria file", "The card revision",
"Dispatching the checker", "The review rule", "Asking the requester", "Folding an answer",
"A card-changing answer", "The ready receipt" and "Landing a commit" are in
`../../references/spec-procedure.md`, and are followed as written there.

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
that, every time you commit the spec folder, write the line again with that commit. A parent
card carries no spec line: one still on an old parent card is removed, through the tracker
binding under this marker, as "A parent issue" step 2 says, and that removal is the parent
path's one card write.

## The status

A spec's Status row moves `drafting`, then `Ready`, then `approved`. It is `drafting` while
anything is open: a question, an owner step without a moment, a failing condition or a
request question handed back. It becomes `Ready` when the last check found nothing open, or
when the requester settled everything it found, and `approved` when the requester approves
the Ready spec.

A re-derive or an amend keeps the status it found when every change it made is either the
requester's recorded answer folded as given, or on the developer's side of the decision
line: the requester's answer approves the change it makes. Otherwise the status returns to
`Ready`, and approval is asked again; with anything still open it is `drafting`. A status
below what it was, with the work stopped, is the case in which Re-derive fires
`readiness-lost`, as its step 7 says.

## New

1. **Load the profile** as "Load the project profile" in `working-a-card.md` says, with its
   specs path, recorded decisions path, environments, data access, concern extensions,
   owner-step types, wireframe fidelity, branches and merging, sessions and standing
   answers. Leave the card wherever it is on the board.
2. **Read the card** in full, every comment with its date and author included, as "Read a
   card" in `working-a-card.md` says. For a sub-issue, read its parent too. Then apply the
   request gate, and go on only when the card meets the Definition of Request.
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
     checker runs. Under design-card fidelity a development card produces none: it cites
     the design card's approved artifact by its path in the profile's Design artifacts
     folder, and a design card's own artifact is written there, not beside `spec.md`.
     Record under "Interface surface" the approval with the blob id of the revision it
     approved (`git hash-object <file>`) and its date. When the artifact changes after its
     approval, put it to the requester again before the checker runs and cite the new
     approval; a cited approval whose blob id is not the artifact's as it stands fails
     Ready 6.2. Treat per-item content the artifact shows that no stored field holds as
     sample data: name the stored field behind each piece and where its values come from,
     and where none holds it, note what persisted data should hold as a question for
     step 7.
   Commit nothing yet.
6. **Check, fresh.** Dispatch the readiness checker as "Dispatching the checker" in
   `spec-procedure.md` says, kind fresh, at creation. At creation the spec has no stamp, so
   the checker marks 9.2 not applicable and reports the card revision and branch head it
   checked.
7. **Ask.** Put to the requester every question the checker reported and every question you
   noted in step 5, merged where they are the same question, as "Asking the requester" in
   `spec-procedure.md` says, except each request question, which you collect as the card
   rule says. For each owner step the checker reports without a moment, agree its moment
   with the requester the same way. Fold each answer as "Folding an answer" there says. Fix
   every finding that needs no one's answer in the spec, cutting or narrowing text before
   adding any. A work-order fault, and any finding only a change to the card would fix, is a
   request question. None of these answers is a gap: the spec has not yet earned Ready.
8. **Check, follow-up.** Dispatch the readiness checker once more, kind follow-up. Ask the
   requester about whatever it still finds, and fold the answers, without another check.
9. **Lint and stamp.** Steps 9 to 11 run in one stretch under the `grill` marker you
   already hold: lint, stamp, commit, spec line, and only then `end`. Run
   `devfactory spec-lint <spec dir> --criteria <file>` and fix every finding. Then stamp
   the spec as "The stamp" says: the Card revision from `devfactory stamp`, the Repo commit
   the follow-up reported, today's date. Set its status as "The status" says: `Ready` when
   the follow-up found nothing open, or when the requester settled everything it found;
   otherwise `drafting`. When you collected any request question, stamp and commit nothing:
   hand them back as "Handing back a request question" says, and go to step 12. Otherwise,
   when the status is `Ready`, write the ready receipt as "The ready receipt" in
   `spec-procedure.md` says, over every spec the follow-up measured, with `--commit` the
   head the follow-up reported reading.
10. **Commit** the spec folder, and nothing else, as its own commit, once the lint "The
    stamp" requires is clean, landing it as "Landing a commit" in `spec-procedure.md` says.
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
    gap, at stage Approval, against the condition that let it through, and a request change
    when the requester changed their mind rather than answered a miss:
    - When it changes only the spec, it is an Amend with no re-check: the requester's words
      are the answer, Amend writes the amendment and the gap entry, and approval is asked
      again.
    - When it would change the card, it takes the route "A card-changing answer" in
      `spec-procedure.md` gives, this skill being the caller that runs Re-derive, at stage
      Approval; Re-derive writes the gap entry, and approval is asked again.

## A parent issue

A parent issue has no spec, no stamp, no spec line, no status and no evidence: its outcome is
that every sub-issue is done. Its folder under the specs path, `<specs path>/<parent id>/`,
is the run's records folder, holding only `receipts.md` and `gaps.md`, each created when
first written. `grill` run for a parent works its set:

1. **Check the parent card.** Load the profile and read the parent card and every sub-issue
   as New steps 1 and 2 say. When the parent card carries any part beyond its four (title,
   purpose, work order, and suggested model and effort), such as acceptance criteria or
   supporting information, stop and do nothing more: report that it goes through
   `re-evaluate-card` first, which restructures it to the card standard with the requester.
   A spec line alone does not stop it; step 2 removes it. Otherwise apply the request gate
   to the parent card.
2. **Clear an old parent folder and spec line.** When the parent's folder still holds
   `spec.md`, remove `spec.md`, `evidence/` and any wireframe in one commit, landing it as
   "Landing a commit" in `spec-procedure.md` says, and keep `receipts.md` and `gaps.md`.
   Nothing is ledgered. When the parent card still carries a spec line, remove it in this
   step, directly through the tracker binding under the `grill` marker, and read the card
   back to confirm it is gone; this is the parent path's one card write.
3. **Each sub-issue not yet Ready** gets its own spec, by New steps 1 to 12, or by Re-derive
   when it has a spec whose stamp no longer matches. Ask a gap several sub-issues share once,
   as the rule, and dispatch the checker over several sub-issues together where that finds
   what they share. `ready` fires for each sub-issue as its spec is made Ready.
4. **Check the set.** As the last step, run `check-ready` over the parent and its sub-issues,
   at creation. It judges Ready 8.2 from the parent card, and what the set shares from the
   sub-issues' specs, settles what it finds with the requester, and writes the set's ready
   receipt in the records folder with `--parent`. When it reports nothing open, fire `ready`
   for the parent. Whenever a card is added to the parent, grill it by step 3 and run this
   step again.
5. **Approval covers the set.** Ask for approval only when every sub-issue is Ready and the
   set check reported nothing open, as one question covering the set. On approval, set every
   sub-issue's spec to `approved`, commit each as New step 10 says, write each sub-issue's
   spec line, and fire `approved` for each sub-issue and for the parent. A change asked for
   at approval is handled as New step 13 says, and approval of the set is asked again.

## Re-derive

1. **Load the profile and read the card** as New steps 1 and 2 say, the request gate
   included, and read the spec folder in full; when the gate stops the card, go to step 7. A
   parent card has no spec of its own: check it first as "A parent issue" step 1 says, and
   the specs re-derived for a change to it are those of the sub-issues the table below names.
2. **Find what changed.** Take the changed parts from the dispatcher. When only
   `devfactory stamp-check --card <n> --spec <spec dir>` says the card changed, compare the
   card's current text with the revision the stamp records, from the tracker's revision
   history where it keeps one, and otherwise treat every part as changed. When the change
   came from a card-changing answer, also take from the dispatcher what "A card-changing
   answer" in `spec-procedure.md` says the caller gives: the question, the answer, the stage
   the work is at, the condition that let it through, whether the requester changed their
   mind rather than answered a miss, and whether the caller runs the readiness check itself.
3. **Choose the conditions to re-run.** A change to a scope boundary, or one that changes the
   interface determination, re-grounds the whole spec: run New steps 3 to 5 on the existing
   spec, keeping its version history and its criterion IDs, then continue at step 5 below.
   Otherwise re-run only the conditions the changed parts feed:

   | Changed part | Ready conditions it feeds |
   |---|---|
   | Title, summary, the issue or request | 1, 9.3 |
   | What needs to be achieved, acceptance criteria | 1.2, 2, 3.2, 3.3, 3.4, 4.2, 4.3, 5, 6.1, 7, 9.3 |
   | Scope | 3.3, 3.4, and the whole spec when a boundary moved, as above |
   | Supporting information | 3.2, 4.2, 9.1, 9.3 |
   | Open questions | 2.3, and whatever the answered question changed |
   | Work order, or a sub-issue added or removed, on the parent card | 8.2 over the set, judged from the parent card; 3.2, 4.2, 9.3 for each sub-issue whose spec cites a wait the change adds or drops |
   | Suggested model and effort | none |

   A work-order change re-derives every sub-issue spec that cites a wait it adds or drops,
   such as a Release sequencing disposition or an edge row that relies on another
   sub-issue merging first: the revised waits replace the old ones outright, and nothing
   in a spec may still rely on a wait the work order no longer gives. Its check covers the
   parent card with every sub-issue, so 8.2 is judged across the set. A sub-issue added is
   grilled as "A parent issue" says. Condition 6.1 is re-derived on every criterion change,
   never carried over. Condition 9.2 is not applicable in a re-derive check, because the
   card has changed against the old stamp by definition; the new stamp replaces it.
4. **Revise** the spec sections those conditions read, as New step 5 says.
5. **Check.** Dispatch the readiness checker as "Dispatching the checker" in
   `spec-procedure.md` says, kind re-derive, naming the conditions this re-derivation
   re-runs; ask, fold and run the one follow-up as New steps 7 and 8 say, handing back any
   request question as the card rule says. When the caller runs the readiness check itself,
   as `check-ready` does, skip this step and leave the check to it.
6. **Re-stamp, record and commit.** When you hand back a request question, commit nothing and
   go to step 7. Otherwise bump the version and add a row to "Amendments" naming the changed
   card parts that drove it, and the gap when there is one. When the change came from an
   answer given after the spec had earned Ready, add the gap entry with
   `devfactory gaps add <dir> --stage <stage> --question <question> --condition <condition>
   --resolved <what resolved it>`, each value quoted as one argument: the stage and question
   the dispatcher gave, the condition written `Ready <id>` or `Done <id>`, and `--kind
   request-change` added when the requester changed their mind. `<dir>` is the spec folder,
   and the resolution its new version; for a change to a parent card it is the parent's
   records folder, and the resolution names each sub-issue spec and the version that
   resolved it, or `parent card` when no spec changed. When the caller runs the readiness
   check itself, stop here and go to step 7: the stamp, the status, the receipt, the commit
   and the spec line are the caller's, and steps 8 and 9 with them. Otherwise set the status
   as "The status" says, and re-stamp as "The stamp" says, the Card revision from
   `devfactory stamp`. When step 5's own check found the spec
   Ready, or the requester settled everything it found, write the ready receipt as "The
   ready receipt" in `spec-procedure.md` says, with `--commit` the head that check reported
   reading; for a check over a parent's set, in the records folder with `--parent`. Commit
   the spec folder on its own, as "Landing a commit" says, and write the spec line with that
   commit, under the marker.
7. **Fire `readiness-lost` by the outcome.** For a card whose spec was `Ready` or
   `approved`: when this re-derivation stops to wait for the requester, or ends with the
   status below what it found, fire `readiness-lost` for the card, once for this stop.
8. **Approval after a change.** When the status returned to `Ready`, ask the requester to
   approve the spec, as New step 13's approval question does; in a sub-issue's session the
   question goes through the coordinator, as "Asking the requester" in `spec-procedure.md`
   says. On approval, set the status to `approved`, commit that change on its own as
   "Landing a commit" says, and write the spec line with the new commit, under the marker. A
   change asked for here is handled as New step 13 says, and approval is asked again.
9. **Fire the event for where the card now stands.** Whenever a `readiness-lost` has fired
   for the card since its status was last reached (in step 7, by an earlier stop of this
   skill, or by the skill that dispatched this run, which says so), fire, once the spec is
   committed: before development, `ready` for status `Ready` and `approved` for status
   `approved`. During development fire nothing: `build` fires `development-started` when the
   build resumes. A re-derivation that ends with the status it found, after no
   `readiness-lost`, fires nothing.
10. **Report** what changed in the spec and whether it is still Ready.

## Amend

Amend runs only after the spec has earned Ready, and only for an answer that leaves the card
as it is. A question answered before then is folded by New or Re-derive and is not a gap. An
answer that would change the card is no amendment: it takes the route "A card-changing
answer" in `spec-procedure.md` gives.

Amend also takes a finding on the developer's side of the decision line that a build carries
past its review limit, handed over in this form: the finding's text as the question, the
correction as the answer, stage Done, and the finding's `Done <id>` as the condition.

1. **Load the profile** and read the card and the spec folder in full, on the branch the
   spec lives on now, and apply the request gate. Run `devfactory stamp-check --card <n>
   --spec <spec dir>`: when it reports the card changed, stop and report it, since the spec
   is brought along by Re-derive first. When the answer would change the card, stop and
   report that it takes the card-changing route.
2. **Write the amendment**: the answer goes into the spec section it settles. Never write
   the card.
3. **Add the gap entry** with `devfactory gaps add <spec dir> --stage <stage> --question
   <question> --condition <condition> --resolved <version>`, each value quoted as one
   argument: the stage the work is at (Approval, Development, Done or Acceptance), the
   question as asked, the condition the dispatcher named as having let it through, written
   `Ready <id>` or `Done <id>`, and the new version as what resolved it. Add `--kind
   request-change` when the dispatcher says the requester changed their mind rather than
   answered a miss. The script writes the date and the form `spec-template.md` lays out;
   never write the entry by hand.
4. **Bump the version** and add the "Amendments" row, driven by the gap. Set the status as
   "The status" says.
5. **Re-stamp** the date, as "The stamp" says; the Card revision, from `devfactory stamp`,
   is the one the stamp holds, since the card has not changed. Commit the spec folder on its
   own on the current branch, and write the spec line with that commit.
6. **Report** the amendment, its version, and whether the answer changes what another card
   depends on, so the work order is re-checked.
