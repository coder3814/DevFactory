# DevFactory design

> Status: **accepted 2026-11-07**. This is the design of record for what the DevFactory
> plugin is. When the plugin and this document disagree, one of them is wrong, and the
> disagreement is a finding.

DevFactory is one Claude Code plugin that carries a change from a request to an accepted
result with an agent doing the work unattended. It owns the request (a card on a board),
grills the request into a specification that a fresh agent can build from without asking
anything, runs the build (a parent issue as one session per sub-issue), handles the two
things that interrupt an unattended build (a question the spec did not answer, and an
acceptance not given), judges the result Done against the spec, and records every miss so
the grilling improves.

It is project-agnostic. Everything about one project lives in that project's **profile**,
which the plugin reads and never embeds.

## 1. Principles

1. **The card is the request. The spec is what development reads.** The card stays small
   and outcome-shaped under the card standard. Everything a builder needs beyond that is in
   the spec, which grilling produces beside the code.
2. **Ready means no further question.** A question asked mid-build is a readiness miss by
   definition, recorded as a gap and answered as a spec amendment, never as chat.
3. **Ready is a recorded state, not a memory.** The spec is stamped with the card revision
   and repo commit it was derived from, so staleness is a machine check anywhere, anytime.
4. **Ready is not approved; intent is not gated.** The checker judges completeness. The
   owner approves once at Ready and judges intent once at acceptance. No per-edit approval
   of wording.
5. **The requester decides observable behaviour and the end state of persisted data. The
   developer decides internal structure and anything a recorded decision, convention or
   existing pattern already answers,** and records the call rather than asking.
6. **Silence is not a disposition.** Every fixed concern is answered on the spec, and
   "not applicable, because X" is an answer.
7. **No agent accepts its own work.** Reviews are by a separate agent given what should be
   true, never how it was built.
8. **The process lives in the plugin; the project's facts live in the profile.** A question
   that recurs across runs is a missing profile entry, and the process says so.
9. **Claude Code's mechanisms are used fully:** scripts for machine checks, hooks for
   enforcement, agents with their models and tools, and skill frontmatter for permissions
   and context. Portability to another agent system is not a goal.
10. **Each thing is judged once.** A check runs in the stage that produces what it judges,
    and a passing check leaves a receipt: a fingerprint of everything it read. A later stage
    compares the fingerprint instead of judging again, and re-runs the check only when
    something it reads has changed.
11. **The process keeps its records in its own files.** Evidence, gap records, receipts
    and check results live in DevFactory's files in the repository, under the spec folder
    or `.devfactory/`, or, for a review record before release, under the repository's git
    directory, even when a record is temporary and cleaned up later; never on a card or
    anywhere else outside the repository. As the owner put it (the owner,
    2026-11-11): "I don't ever want to use an external resource, such as cards, for this
    type of information. This should be internal."

## 2. The objects

### 2.1 The card

A work item on the project's tracker, written to the card standard: title, summary, the
issue or request, what needs to be achieved, scope, supporting information, open questions,
acceptance criteria. Two further sections are core, because every run of sessions needs
them:

- **Suggested model and effort**, after the acceptance criteria. A build session runs on
  it, or on the profile's default when the card suggests none.
- **Work order**, on a parent issue only: its sub-issues by number alone, never by title or
  scope, in the order to work them, each saying what it waits on (one of: needs the
  other's result; changes the same files; both need something only one session can hold)
  and which may run alongside it. Sub-issues run in parallel by default. The work order on
  the card is the order: the tracker's own order of sub-issues is not kept in step with it,
  and nothing judges that order. A parent waits on another parent only for that parent's
  work, and the wait is met once that code is on the integration branch and the waiting
  parent's branch is rebased onto it, checked by content because a rebase changes commit
  ids; no release, board column or closed card is waited for.

**A parent issue** is a card with sub-issues. It holds a title, a purpose (one short
paragraph saying why these cards belong together), the work order, and the suggested model
and effort of the session that coordinates it, and nothing else: no issue or request, no
what needs to be achieved, no acceptance criteria, no supporting information, no scope and
no open questions. Its outcome is that every sub-issue is done, so it has no spec, no spec
line, no stamp, no status and no evidence. A requirement only the combined result can show
is a criterion on the sub-issue that completes it, and the work order has that sub-issue
wait on the ones it needs. The Done judge establishes the process facts under Done 6.1, so
a parent run captures no evidence for them: a criterion such as "every sub-issue of this
parent is done" asks for an evidence row nobody can capture. How a sub-issue is linked to
its parent on the tracker, unlinked and listed is the binding's, in its "Sub-issues"
section. A parent that carries a part beyond those four (criteria, supporting information
and so on) is not worked: `start`, `grill` and `check-ready` stop and say it goes through
`re-evaluate-card`, which restructures it with the requester, moving each criterion the
combined result shows to the sub-issue that completes it and dropping the rest as restating
the outcome. A spec line alone stops nothing. `re-evaluate-card` leaves a spec line on the
parent and says `grill` removes it. `grill`, run for the parent, removes the old `spec.md`,
`evidence/` and any wireframe in one commit and ledgers nothing, and in the same step
removes a spec line still on the parent card, through the tracker binding under its
marker, as that path's one card write.

A sub-issue carries a line naming its parent. Criteria carry **stable IDs** (`C1`, `C2`, …)
that survive amendment: a removed criterion's ID is never reused, and a new one takes the
next number. Work orders, comments, gap records and evidence cite the ID, never the
position.

### 2.2 The spec

One folder per card in the project repository, at the path the profile names (default
`specs/<card>/`), versioned with the code and outside any documentation system the project
runs. It holds:

- `spec.md`: the specification (section 2.3).
- `wireframe.*`: present when the interface determination is non-trivial and the design is
  not its own card.
- `gaps.md`: the gap record (section 2.7).
- `receipts.md`: the receipts (section 2.8). The card's first passing request check creates
  the folder to hold its receipt, so the folder can exist before `spec.md` does; a folder
  without `spec.md` is not a spec.
- `evidence/`: what the Done judge consumes, added during development, one folder per
  criterion ID, each artifact with a one-line sidecar recording its revision, checkpoint and
  what produced it. Evidence is captured after the last commit that changes the code it
  shows. `evidence-check`, given the base revision, refuses an artifact when a code file the
  change set touches differs between its revision and HEAD. It compares content rather than
  commit order, so a rebase that rewrote commit ids or brought in other work leaves evidence
  current, and so do commits that touch only the specs path, `.devfactory/` or the
  profile's Not code paths, such as change notes; a capture at the base is exempt. A fix
  still makes every artifact captured before it stale, because the script cannot tell which
  files an artifact depends on, so the build captures evidence together just before each
  review and recaptures only what the check names.

A parent issue's folder at the same path, `<specs path>/<parent id>/`, is the run's
**records folder**: it holds only `receipts.md` and `gaps.md`, each created when first
written. The set's ready receipt and the gap entries about the work order (Ready 8.2) go
there, and `release` ledgers and deletes it as it does a spec folder. Neither folder holds
a review record (section 2.9).

The card points at its spec with exactly one line, `Spec: <path> @ <commit>`, the last line
of the description body, where the commit is the spec folder's own commit. `grill` rewrites
that line after every commit of the spec folder, and the card revision the stamp hashes
excludes any line of that form, so writing it never makes the spec stale.

The spec is written before development starts, wherever the card sits on the board, and lands on the
integration branch through a commit of its own. During development it is amended on the
sub-issue's branch and merges with the work. At release its gap entries are appended to the
project's gap ledger, the card's review record to the review ledger, and the folder is
deleted, not archived; history keeps it, and the durable facts have already gone wherever
the project keeps decisions.

### 2.3 What the spec holds

In this order, general to specific:

1. **Header**: card, version, status (`drafting`, `Ready` or `approved`), Ready stamp (card
   revision hash, repo commit, date), request type(s).
2. **Decisions delegated to the developer**: the calls the grilling identified as the
   developer's under principle 5, listed so the builder knows they are its to make, and the
   log of the calls it made.
3. **Boundaries**: exclusions with reasons; deferrals with reasons; for each requirement, its
   edge behaviour either specified or named as excluded or delegated.
4. **Dispositions**: one line per fixed concern (section 4, condition 4).
5. **Interface surface**: the determination (non-trivial / trivial, because / not
   applicable, because) and, when non-trivial, the approved wireframe's path, or the design
   card whose approved mock-up it uses, and the pages or screens it covers.
6. **Data population**: when the card's rules act on existing data, the result of running
   them read-only against that population: counts per rule, and the rows no rule covers,
   each resolved.
7. **Evidence plan**: one row per criterion: how it is shown (test, image, log, query,
   output), what the artifact will show, under what condition, how it is generated, and the
   environment (checkpoint) it is captured in: a profile environment, or the built-in
   Repository checkpoint for command output from a clean checkout, git history and the
   card's comments, which shows nothing about a running system. A row only the live release can show is
   marked post-release, and only when no checkpoint before release could fail it.
8. **Owner steps**: each step only the requester can take (approve a mock-up, sign in
   somewhere, run something in production) with the moment in the run it happens.
9. **Project bindings used**: the profile entries this spec relies on, by name.
10. **Amendments**: version, date, what changed, and the gap or rejection that drove it.

**The status** moves `drafting`, then `Ready`, then `approved`, and is stated once, in
`grill` under "The status". It is `drafting` while anything is open, `Ready` when the last
check found nothing open or the requester settled everything it found, and `approved` when
the requester approves the Ready spec. A re-derive or an amend keeps the status it found
when every change it made is the requester's recorded answer folded as given or on the
developer's side of the decision line, since the requester's answer approves the change it
makes; otherwise the status returns to `Ready` and approval is asked again, or to `drafting`
with anything still open. A status below what it was, with the work stopped, is the case in
which `readiness-lost` fires (section 3).

### 2.4 The project profile

One folder per project, `.devfactory/` at the repository root:

- `profile.md`: the profile.
- `modules/`: the team modules the profile names.
- `gaps.md`: the gap ledger, the gap records of released cards (section 2.7).
- `reviews.md`: the review ledger, the review records of released cards (section 2.9).
- `post-release/`: one folder per released card with evidence rows only the live release
  can show, holding those rows and their capture until the next release deletes it. Its
  `plan.md` opens with a `Request type(s):` line, which `release` writes and reads for
  `gaps ledger --types`.
- `.active/`: the marker folder the hooks read (section 8), ignored by git.
- `hooks/`: the project's event hooks, one script per event it wants acted on (section 3).

`profile.md` holds, each as its own section:

- **The board**: the tracker binding and the entries it asks for; the field each part of a
  card is written to; any additional fields with the team module that works each one (a
  module may have no field and hold rules for the card as a whole). It names no board
  column: no skill reads a card's column or moves a card.
- **The work**: where specs live; where recorded decisions live, so the checker can read
  them (they are never kept in the profile); the test gate, the command or procedure that
  proves existing behaviour, optionally with an Affected tests command a build runs for the
  tests its change touches, and a recorded gate, a project-owned command that records each
  pass against the git tree it tested and prints that record instead of rerunning on the
  same tree, with the Forced rerun that runs it fresh (`references/test-gate.md` says when
  each runs); the environments available for checkpoints and what each can
  and cannot show; **Data access**, each population of existing data a card's rules might
  act on and how it is read without writing, which `grill` and the readiness checker run
  data rules through; the fixed-concern list extensions; the owner-step types the project
  has.
- **Wireframe fidelity**: what the approved design artifact fixes (section 2.5), with a
  **Design review** line saying how a wireframe is shown to the requester and approved,
  and, with a design card, a **Design artifacts** line naming where approved artifacts are
  kept.
- **Branches and merging**: the integration branch, the worktree layout, how a parent branch
  and a sub-issue branch are named, how a standalone card's branch and worktree are named
  (`Card branch`), who merges what and when, and the release procedure (the project's steps
  or the skill it names).
- **Sessions**: the default model and effort.
- **Hooks**: a line only for a hook that is off, all being on by default, and the Marker
  lifetime only when it is not 12 hours.
- **Standing answers** (section 7).

The profile records only departures from the defaults, and any entry may point to where
the project already records it (its instructions, a recorded decision, a skill) instead of
copying it, except in a field the plugin's script or hooks read as a value (the branch
names, the specs path and Not code paths, the Hooks lines). Permissions are not kept in it: the read-only allowlist entries
`configure-project` writes to the project's `.claude/settings.json` are their record. A
write to the tracker or to a branch is never pre-approved.

`configure-project` writes the profile from the board, the repository and the owner's
answers. It takes the answers its caller already holds and asks only the rest, commits the
profile or tells the owner to, and says that hook changes take effect in the next session.

### 2.5 Wireframe fidelity

The approved design artifact grounds Ready condition 6.2. The profile chooses what it fixes:

- **Wireframe**, the default: structure, fields, states and interaction, not aesthetics.
- **Finished mock-up**: the artifact is a complete design.
- **Design card**: the design is a card of its own, grilled and accepted first, and the
  development card's spec references that card's approved mock-up, which meets condition
  6.2 without a file in the spec folder. The profile names the folder approved design
  artifacts are kept in, outside the specs path, so the design card's release keeps them. As the owner put it (the owner, 2026-11-07): "When
  coming up with a design, that should be a card of its own. It can move from a wireframe
  but should have a full, fleshed-out, approved mockup in the equivalent of completed HTML
  for any interface change. That completed HTML would then be used in the implementation of
  a development card."

Fidelity is what the artifact fixes, never when one is required; conditions 6.1 and 6.2
decide that. Every approval names the revision of the artifact it approved by its git blob
id, the spec cites the approval of the revision the build follows, and a change after
approval goes back to the requester before Ready. Per-item content a wireframe shows is
sample data: the spec names the stored field behind it.

### 2.6 The definitions

`references/definition-of-ready.md` and `references/definition-of-done.md`: numbered
conditions, each tagged `[machine]`, `[rubric]` or `[judgment]`. Sections 4 and 5 are their
content. Every `[machine]` condition is decided by a command of the plugin's script,
`scripts/devfactory.py`, which the condition names, never by an agent reading. A machine
condition no command covers yet says so in its tag, and the definition lists it under
"Machine conditions without a script yet".

### 2.7 The gap record

`gaps.md` beside the spec: one entry per question asked from Ready onward, per refused
acceptance, and per Done-check miss, each naming exactly one Ready or Done condition that
let it through, written `Ready <id>` or `Done <id>`, which `gaps add` refuses unless the id
exists in the definition, a **Stage**, one of Approval, Development, Done, Acceptance and
Release (a gap `check-ready` finds at creation is stage Approval), and a **Kind**: `miss`,
the default, or `request-change` when the requester changed their mind rather than
answered a miss. A question answered before the spec first earns Ready is folded into the
spec, not recorded as a gap.

Gap records survive release: before a spec folder is deleted, its entries are appended to
the project ledger `.devfactory/gaps.md`, each under the card ID and the spec's request
types, by `gaps ledger`, which skips an entry the ledger already holds for that card. The
readiness checker reads the ledger and every live `gaps.md` before grilling, so a recurring
class is asked up front next time, and `curate` reads the same records.

### 2.8 The receipts

Without receipts every hand-off would re-judge what the stage before it had just judged:
`grill` would start a fresh card reviewer on a card `create-card` had just passed, and the
start of a parent issue run a fresh readiness checker on specs `grill` had just stamped.
Because a fresh reviewer finds something different every time, each re-judgment raises new
questions about content that has not changed.

A receipt records, field by field, the fingerprint of everything a passing check read, in
`receipts.md` in the card's spec folder, committed with the code. `devfactory receipt write`
writes it and `devfactory receipt check` compares it; nothing else reads or writes the file.

- **Request**, written when the card reviewer finds the card meets the Definition of Request
  and the card as written is exactly what it measured: the card revision, a hash of the card
  facts (each team field, each comment with its text, each attachment, the parent and the
  sub-issues, compared as a set, and the related data a team module names), the standard,
  a hash of the plugin's references and agents alone, so that a version bump alone leaves
  it matching, and a hash of the profile and its team modules. `create-card` and
  `re-evaluate-card` write it; `grill`'s request gate compares it and starts a reviewer only
  when it differs, writing a new one on a pass.
- **Ready**, written when `grill` stamps a spec Ready and when `check-ready` finds nothing
  open: the spec folders measured together, a hash of their files with the Status value and
  `receipts.md` left out so approval keeps it matching, a hash of
  the gap ledger and every live gap record, the standard, the profile, and the commit the
  checker reported reading, which `receipt write` takes as `--commit`. The commit matches
  while it is an ancestor of the head and nothing outside the specs path and `.devfactory/`
  has changed since, because everything under those is fingerprinted on its own. For a
  parent's set the receipt is written in the records folder with `--parent`, which also
  records the parent card's revision. `check-ready` compares it, after the stamps, and starts
  no checker when it matches.

A receipt never replaces the stamp. The stamp says the spec still answers the card; the
receipt says a check need not run again.

### 2.9 The review record

One record per card, kept outside the tracked tree, at
`<git common dir>/devfactory/reviews/<card id>.md` (`git rev-parse --git-common-dir`), so
every worktree shares it and nothing commits it. A review record committed on a branch would change the tree the reviewer's gate
run recorded, and the gate after the rebase could then never reuse that record. The record
holds one block per change review or Done judgment, headed with its date, round and verdict,
and one line per finding naming its Done condition, its criterion ID or `-`, and its text.
`devfactory reviews add --card <id> --round <n> --verdict <v> --findings <file>` appends it
after each verdict, from the report's findings and unstable tests, validating each Done
condition as `gaps add` does; nobody writes it by hand. A parent's Done judgments are
recorded under the parent's id. `reviews show --card <id>` prints a card's record, or
`no-reviews`. Nobody commits a review record before release: `release`'s records commit
runs `reviews ledger --card <id> --ledger .devfactory/reviews.md` for each card and the
parent, which appends the card's blocks under its heading in the ledger, skipping blocks
already there, and removes the card's stored record. `curate` reads the ledger only.

## 3. The lifecycle

| Stage | What happens | Who acts | Exit |
|---|---|---|---|
| Request | The card is created or restructured under the card standard, and request grilling asks the owner every question the card reviewer raises and every open question, until none is left. | `create-card`, `re-evaluate-card`, the card reviewer agent, the owner | The card meets the Definition of Request |
| Grilling | Specification grilling first checks the card against the Definition of Request, which a matching request receipt has already done, then drafts the spec from the card, the code, the recorded decisions and the data population; the readiness checker measures it; the owner answers each question only the spec settles. It never changes the card: a question whose answer would is handed back, and the answer reaches the card through `add-to-card` in settled mode. For a parent issue, every sub-issue not yet Ready is grilled, and then `check-ready` checks the set at creation. | `grill`, `check-ready`, the card reviewer and readiness checker agents, the owner | Ready earned and stamped |
| Approval | The owner approves the Ready spec. For a parent issue, one approval covers the set, once every sub-issue is Ready and the set check reports nothing open. | the owner | Spec status `approved` |
| Development | Work starts through `start`, which reads the card and hands a parent issue to `coordinate` and a standalone card to `build`. A build starts only on an approved spec. One session per sub-issue builds from the spec in its own worktree; questions go through the coordinator as gaps; each session's work is reviewed by a separate agent against the spec; results merge into the parent branch. | `start`, `coordinate`, `build`, the change reviewer agent | Every sub-issue merged |
| Done | The Done judge measures the parent branch against every sub-issue's card and spec and the Definition of Done; a standalone card's passing change review is its Done verdict. Past the review or judgment limit, a round whose findings were all fixed by spec-only amendments, which `spec-only` confirms (for a parent run, over the specs path on the parent branch once the amendments are merged), goes on to acceptance as Done, reported as "no review passed this revision". | the Done judge agent | Done verdict, or a spec-only round past the limit |
| Acceptance | The owner judges the result against the evidence: every criterion is shown with its artifact, and one question accepts them all or names the refused ones. A refusal is classified (section 6.2). | `accept`, the owner | Accepted |
| Release | Confirm the requester's acceptance is recorded on each card; rebase onto the integration branch and run the gate; one records commit appends the gap entries and review records to the ledgers, writes post-release plans to `.devfactory/post-release/<card>/` and deletes the spec folders and the parent's records folder; merge and ship by the profile's release procedure; close the cards; once live, capture the post-release rows read-only and commit them to go out with the next release, which deletes them; curate; mark the sessions completed and archive them, then remove worktrees, branches and review checkouts. | `release` | Cards closed |

Three definitions gate the work, one per hand-off: the Definition of Request
(`references/definition-of-request.md`) before a spec is written, the Definition of Ready
before a build, the Definition of Done before acceptance. Each is checked by an agent where
the work changes hands, never by where the card sits.

**The board is the project's.** Every skill works a card wherever it sits, and no skill
moves one. At each hand-off the skill fires an event — `request-met`, `ready`, `approved`,
`work-started`, `development-started`, `readiness-lost`, `done`, `refused`, `accepted`,
`released` — with `devfactory event`, which runs
the project's hook for it in `.devfactory/hooks/` if there is one and does nothing
otherwise (`references/events.md`, which is the one statement of when each fires and by
whom). A project that wants its cards moved, to whatever columns its board has, writes those
hooks; a failed hook is reported and never holds back the work. `request-met` fires on the
measure's verdict, whether or not the measuring skill changed the card. `readiness-lost`
fires on the outcome, never on the change behind it: when a card whose spec was Ready or
approved is left not Ready and the work on it has stopped, because a re-derive stops to wait
for the requester or ends below the status it found (`grill`), the build's status and stamp
check fails on a stop `grill` has not already fired for (`build`), or the readiness check
reports it not Ready and stops, at creation or at development start (`check-ready`).
A card change re-derived straight back to the status it had fires nothing, and the skill
that brings a card back fires the event for where it now stands.

**Work starts through `start`.** "Start work on card N", or `/devfactory:start N`, reaches
`start` and nothing else. It reads the card once and hands over in the same session and
turn: a card with sub-issues to `coordinate`, any other card to `build`. `build` is entered
only from a coordinator's brief or from `start`, and `coordinate` only from `start`. `build`
and `coordinate` check the spec's status before any work starts. A standalone card is built
on its own branch in its own worktree, named as the profile's `Card branch` says; a
standalone session that finds itself on the integration branch creates that branch and
worktree and works there. Results merge into the parent branch in the order they finish,
except that a card that waits on another merges after the card it waits on. A standalone
card is not merged when its review passes; `release` merges it once, after acceptance.

**The full gate's run before a merge is the reviewer's** (`references/test-gate.md`, the one
statement of when the gate runs). The builder runs the tests its change touches while it builds,
with the profile's Affected tests command where there is one, and runs no full gate before a
review. The change reviewer, and the Done judge, decide every other condition first, and
only when nothing else fails run the full gate fresh on the revision under review (the
Forced rerun where the profile names a Recorded gate, else the Command) before giving PASS
or DONE; a failing test that passes on its one rerun passes and is named unstable. After
the rebase for a merge, of a sub-issue into the parent branch or of the work onto the
integration branch, the merging session runs the Recorded gate, which prints the record
when the rebase left the tree unchanged and runs fresh otherwise, or the Command where there
is no Recorded gate. Nobody writes or edits a record by hand.

**Before each review**, the build commits, then runs `evidence-check --base` and `gaps check`
at that exact revision, starts no review while either reports anything, and makes no commit
between that check and the verdict. After each verdict it records the findings with
`reviews add --card <id>`, commits nothing for it, and removes the reviewer's checkout.
After each Done judgment the coordinator has an agent record it the same way under the
parent's id, and reads a session's record with `reviews show`.

**Loops are bounded.** After a change review or the Done judge fails, the work gets at most
two further rounds. A third failure asks nothing when every finding is on the developer's
side (a missing test, an incomplete evidence record, a spec that no longer matches the
built code with no change to what an observer sees): the findings are fixed and a code fix
gets one more review or judgment. A developer-side finding is handed to `grill` Amend with
the finding's text as the question, the correction as the answer, stage Done and the
finding's `Done <id>` as the condition. The work carries on without a further review only
when every fix is a spec amendment made through `grill` Amend and `devfactory spec-only
<spec dir> --base <the failed revision>` prints `spec-only`; the report then says, in these
words, "no review passed this revision", lists the last review's findings with the
amendment that answers each, and never says the card passed, and `accept` shows that line
in its question. Past the Done judge's limit the same rule holds: once the spec amendments
are merged, the coordinator has an agent run `devfactory spec-only <specs path> --base <the
judged revision>` on the parent branch, and only on `spec-only` does the run go to
acceptance, with that line, the last judgment's findings and their amendments.
Only findings that change what an observer sees or can do, what persisted data ends up as,
or scope stop the work and go to the requester, through the coordinator in a parent issue
run.

**Sessions are kept.** In a parent issue run, each sub-issue's session, worktree and branch
are kept until the run is accepted and released. A Done-judge finding or a refusal that
belongs to one sub-issue is fixed by that sub-issue's kept session, on its branch rebased
onto the parent branch; one no sub-issue owns goes to the kept session of the sub-issue
whose files it touches most, which fixes it against the card and spec the message names. No
session is started for a finding. Either fix is reviewed and merged as any sub-issue's work
is, and judged again. A standalone card's refusal is fixed by its build session, which
begins again, fixes, has the fix reviewed as any review is made, fires `done` and returns
to `accept`. `release` ends them: each is stopped, its worktree checked for
uncommitted work that is not regenerated output, marked completed and archived, with no
further question; only then are the branches, any worktree left and every detached review
or judge checkout removed. An idle session holds its worktree open, so removing the folder
before archiving fails or hangs.

**Every session starts in the requester's turn.** The Claude desktop app starts a session
only on a turn the requester's own message began. So, in the turn of the "start work"
message, the coordinator starts two agents, one reading the parent and every sub-issue
(number, model and effort, spec status, waits) and one firing `work-started` and creating
the parent branch and its worktree, says what it started and ends the turn. When both have
reported, it ends a turn with one question that names every session to start. The
requester's reply begins a turn of their own, and in it the coordinator starts every
session, each with its branch name and briefed to wait for the readiness check and for its
work-order waits, and then sets each going by message, which works from any turn. A
sub-issue added mid-run gets its session through the same single question. A session is
never proposed as a card.

**Sessions report by message.** Every report, question and stop a build session makes in a
parent issue run goes to the coordinator as a message the session sends to the
coordinator's session id (`references/reporting-to-the-coordinator.md`). The turn's closing
message is one line saying the report was sent, and the session ends a turn only to wait for
the coordinator. While it waits on its own work, a reviewer it started or a background
command, it keeps the turn open with a blocking wait in slices under the shell's limit. The
app's note that a session ended a turn carries nothing, and the coordinator does not act on
it. At each milestone (sessions started, a session set going, a merge, a finding sent, a
judgment) the coordinator says one line to the requester. A wait on another parent is
checked again by an agent at every wake while it is unmet.

**Stops are few.** Before any question reaches the requester it is tested against the
profile's Standing answers and the decision line (section 7). A step the process already
prescribes, such as going into acceptance after the Done judge's DONE, is not asked for.
The release is asked once, or not at all when the requester authorised it ahead of time,
in their starting instruction or their acceptance answer. An authorisation to release
starts the `release` skill and nothing more: a question the project's release procedure
asks is answered only by a profile standing answer and is otherwise asked, as `release`
says under "What an authorisation covers". `curate` asks once per pass,
with every proposal numbered, drops what the plugin, the project's own records or the
profile already hold or the requester has declined, and asks only about writes,
retirements and changes to a project document.

**Release runs in one order and can run again.** `release` loads the profile and confirms
that the requester's acceptance is recorded on each card, reading no board column; settles
what the profile leaves open; rebases and runs the gate; makes the records commit on the
branch being merged once the gate passes, with no further gate run since it changes no code
path; merges and ships; closes the cards and fires `released`; captures post-release
evidence; runs `curate`; and stops and reaps. A rebase that conflicts is aborted (`git
rebase --abort`) and reported with the conflicting files, and the release stops with the
work held. The conflict is fixed as a Done finding is, by the kept session or the
standalone build session, reviewed and, in a parent run, judged again; then `release` is
run again. It can be run again at any time for the same cards: each step first looks
whether its result is already there and skips it when it is, the rebase-and-gate step
counting as done when the integration branch's head is an ancestor of the branch and the
gate passed on its tree, and work held rather than released is released by running it
again. It ends by listing each step as done, skipped as already done, or not done with the
reason. A coordinator's last step confirms from that list that `curate` ran and
that every post-release plan was captured or reported.

## 4. Definition of Ready

A spec is Ready when every condition holds, evaluated over the card, the spec, the profile
and the repository. Presence checks come first; the end-to-end test is last.

**1. The request is classified**
1.1 The spec declares the request type(s): feature, bug fix, refactor, data correction,
    other. `[machine]`
1.2 The type fits the request. `[judgment]`
1.3 For a bug fix, the failing scenario at the base revision is stated. `[machine: presence]`
1.4 For a refactor, the observable surface that must not change is named. `[machine: presence]`

**2. The criteria are addressable and testable**
2.1 Every criterion carries a stable ID. `[machine]`
2.2 Every criterion names observable behaviour a test could exercise and a result could fail.
    `[judgment]`
2.3 No criterion is marked provisional, and the card has no open question. `[machine]`

**3. The boundaries are defined**
3.1 Exclusions and deferrals are listed, each with a reason. `[machine: presence; judgment:
    adequacy]`
3.2 Each requirement's edge behaviour is specified, excluded with a reason, or delegated to
    the developer. `[judgment]`
3.3 Scope moves since the last Ready are reflected in both the card and the spec. `[machine]`
3.4 The spec asks for nothing beyond the card; whatever does is cut, never asked about.
    `[judgment]`

**4. The fixed concerns are disposed**
4.1 Every concern on the list has a disposition; "not applicable, because X" is one.
    `[machine: presence]` The core list: existing data changed; security; performance;
    release sequencing (does the change need anything before or after the deploy); owner
    steps. The profile may extend it.
4.2 Each disposition is true of the request as specified. `[judgment]` A disposition
    about a figure only the build can measure (a read count, a load time, a bundle size)
    states the bound the change must stay within and the evidence row that measures it,
    and predicts no value; a bound exceeded as built is a Done 4.3 finding. Where several
    sub-issues move one figure, each states the bound for its own change, and the finished
    figure is an evidence row on the sub-issue the work order puts last among them.
4.3 A non-trivial disposition's demands appear in the spec's requirements or evidence rows
    under the criteria they bear on; a disposition adds no criterion. `[machine]`

**5. The data population is checked** (when the request's rules act on existing data)
5.1 The rules were run read-only, through the profile's Data access entry, against the
    population the spec names, with counts per rule. `[machine: presence]` A population
    with no Data access entry leaves the condition unchecked, never passed.
5.2 Every row no rule covers is resolved by a rule, an exclusion or a delegation. `[judgment]`

**6. The interface surface is grounded**
6.1 The determination is stated: non-trivial, trivial because, or not applicable because.
    `[machine]`
6.2 When non-trivial, the design artifact the profile's wireframe fidelity requires is
    present (or, for a design card, referenced) and approved, and grounds structure,
    fields, states and interaction. `[machine: presence; judgment: grounding]`

**7. The evidence plan is complete**
7.1 Every criterion has an evidence row naming artifact, what it shows, condition, how it is
    generated and the checkpoint. `[machine]`
7.2 Every row could be failed by a delivered artifact. `[judgment]`
7.3 Every checkpoint named is one the profile's environments can provide. `[machine]`
7.4 Every row uses the lightest artifact that could fail it, from what the project already
    has; the spec never asks for a profile change. `[judgment]`

**8. The owner's part is scheduled**
8.1 Every owner step has a moment in the run. `[machine: presence]`
8.2 For a parent issue, the work order's waits each cite an allowed reason, no pair marked
    parallel would collide, and no wait holds back work that could run. `[judgment]` It is
    judged from the parent card with its sub-issues' specs, and its gap entries go in the
    parent's records folder.

**9. The spec grounds the work**
9.1 Every project binding the spec relies on exists in the profile. `[machine]`
9.2 The spec is stamped with the card revision and the repo commit it was checked against,
    the commit being the branch head the checker read. The condition holds when the card's
    revision equals the stamp's and the stamped commit is an ancestor of the current head.
    It is not applicable when the spec has no stamp yet, or in a re-derive check.
    `[machine]`
9.3 A fresh agent could decompose and build the work from the card, the spec, the profile
    and the repository without a single new question, every decision either grounded in them
    or delegated under principle 5. `[judgment]` This is the purpose of the definition tested
    directly; conditions 1 to 8 catch its common failures before it.

The definition does not trace criteria through tags in commits, which needs a commit
discipline the plugin cannot enforce; does not require video evidence, since capture
capability is the project's; has no per-spec rubric set, since the profile binds the few
terms that vary; and keeps the existing-behaviour gate in the profile rather than in each
spec.

## 5. Definition of Done

A change is Done when every condition holds, evaluated over the spec, the base revision and
the revision under evaluation.

**1. The tests exist and pass**
1.1 The profile's test gate passes at the revision under evaluation. `[machine]` The pass
    is the change reviewer's or the Done judge's own fresh run of the full gate on that
    revision, made last when nothing else fails; a printed record never decides it. A test
    that fails on that run and passes on its one rerun passes, and is named unstable.
1.2 The test types the request type requires exist and pass: a feature has a test per
    criterion; a bug fix has a test that fails at base and passes now; a refactor shows the
    declared surface unchanged; a data correction has the dry run's counts matching the
    apply's. `[machine]`

**2. The tests test the spec**
2.1 Every criterion is exercised by at least one test or evidence artifact. `[machine]`
2.2 Each test asserts an observable outcome and would survive a reimplementation. `[judgment]`

**3. The evidence fulfils its promises**
3.1 Every evidence row has its artifact, showing what the row promised under the stated
    condition, captured at the stated checkpoint. `[rubric: the row]`
3.2 Each artifact records the revision, the checkpoint and the command or procedure that
    produced it. `[machine]` The artifact and its record are committed, the revision is an
    ancestor of the revision under evaluation or was rebased into it unaltered, no code file
    the change set touches has changed since that revision, and the checkpoint is one its
    evidence row names.

**4. The work is grounded**
4.1 Every decision embodied in the work is grounded in the spec or recorded as a delegated
    call in the spec's log. `[judgment]`
4.2 The gap record is closed: every gap has a resolving amendment. `[machine]`
4.3 Every disposition is still true of the delivered result. `[judgment]`

**5. Nothing beyond the request**
5.1 Every change in the change set serves a criterion, a delegated call or the work's own
    scaffolding. `[judgment]`

**6. For a parent issue**
6.1 Every sub-issue is done in the combined result. `[judgment]` A parent has no criteria
    of its own. The Done judge establishes this itself from the revision under evaluation:
    each sub-issue's change is merged and conditions 1 to 5 hold for it on the parent
    branch, looked at hardest for what no single review could see. No artifact is captured
    for these process facts; the judge's verdict is their record.

Exclusions: intent is not gated; the owner judges it at acceptance. Nothing is checked by
taste; every check carries a mode.

The change reviewer applies conditions 1 to 5 to one card's change; the Done judge applies
the whole definition to a parent branch.

## 6. Change handling

### 6.1 Before development

A card changes only through the plugin's card skills, which the tracker guard enforces
(section 8). After a card that has a spec is written, `grill` Re-derive runs: a card skill
the user runs directly hands to it, and a skill that handed `add-to-card` a settled answer
runs it itself (below). Re-derive re-runs the conditions the changed parts feed (3.3 and
3.4 whenever the criteria, what needs to be achieved or the scope changed), re-stamps, sets
the status as section 2.3 says, and reports what changed. When the status returned to
`Ready`, it asks the requester to approve as a new spec's approval is asked (in a
sub-issue's session, through the coordinator, which relays it like any other question),
then sets `approved`, commits, writes the spec line and fires the event for where the card
now stands. When its caller runs the readiness check itself, Re-derive revises the spec and
leaves the stamp, the status, the commit and the spec line to the caller: `check-ready`,
once nothing is open, re-stamps each re-derived spec with the commit its last check read,
sets its status, commits it and writes its spec line. A change to the interface
determination or to a scope boundary re-grounds the whole spec. A comment that changes no
part of the card changes nothing. An addition is folded wherever the card sits; a card with
a spec is protected by its stamp, not by a frozen column. A direct edit on the tracker is
caught by the stamp at the next check and handled the same way.

`add-to-card` runs in one of two modes, named by its caller:

- **Interactive**, the default: the addition is recorded and folded, and the requester
  accepts the rewritten wording or asks for changes. This holds for additions made outside
  a run and outside approval.
- **Settled**: the requester has already answered. The answer is the acceptance; the fold
  is written without a further round on its wording, and the requester may still object.

**One route for an answer that changes a card.** Any answer the requester has already given
that changes a card goes through `add-to-card` in settled mode, whichever skill received it:
`grill` handing back a request question or a change asked for at approval, `check-ready`,
`build`, `coordinate` or `accept`. The skill passes `no-rederive` and then runs `grill`
Re-derive itself, giving it the question, the answer, the stage, the condition (`Ready <id>`
or `Done <id>`), whether the requester changed their mind, and, when the caller runs the
readiness check itself, that fact; `references/spec-procedure.md`, "A card-changing
answer", is the one statement of this, and every caller points to it. Re-derive brings the
spec along, and when the answer came after the spec earned Ready, writes the gap entry,
with `--kind request-change` when the requester changed their mind rather than answered a
miss. `add-to-card` run directly by the user, without `no-rederive`, hands to Re-derive
itself. `grill` Amend is only for an answer that leaves the card as it is. A breach
`grill`'s request gate finds that needs no one's answer, the card's own consistency such as
a stale model-and-effort reason or a sub-issue missing from the work order, is fixed
through `add-to-card` in settled mode with `no-rederive` and measured once more, without
entering Re-derive a second time; only a breach that needs the requester's answer stops the
card. `re-evaluate-card` takes no handed-over answer: it is for an audit the user asks for
and for restructuring a parent issue that carries a part beyond its four.

### 6.2 During development

A card is not frozen when development starts: a request change is accepted as an amendment.
Only two things change a spec in development.

**A question the spec did not answer.** The session first applies principle 5 and the spec's
delegations; a question they answer is decided and logged, not asked. A surviving question
goes to the coordinator in a fixed shape: the question, the options, a recommendation, and
the Ready condition that failed. In a sub-issue's session every question for the requester,
a Re-derive's included, goes to the coordinator this way. When the owner's answer leaves
the card as it is, `grill` Amend writes it into the spec on the sub-issue's branch with a
gap entry. When it changes the card, it takes the one route above: onto the card through
`add-to-card` in settled mode with `no-rederive`, then `grill` Re-derive, given the stage
and the kind with the answer, which applies the request gate to the changed card,
re-derives the spec and writes the gap entry; `grill` itself never writes the card. A
changed dependency re-checks the work order. The session continues from the spec as it now
stands.

**An acceptance not given.** The refusal names the criterion the result fails or states the
outcome that is missing, and that sorts it:

- *Fails a stated criterion*: a defect, not a change. It is fixed as section 3 says, by the
  kept session that owns it, or, when no sub-issue owns it, by the kept session of the
  sub-issue whose files it touches most, or for a standalone card by its build session.
  `accept` sends the refusal with the Done condition that should have caught it and writes
  no gap entry itself. The session that fixes it writes the entry once the fix is
  committed, through `grill` Amend: the refusal as the question, the fix and its commit as
  the answer, stage Acceptance, and the `Done <id>` that `accept` named. The fix is
  reviewed, merged and, in a parent run, judged again by the Done judge; `done` fires
  again, and `accept` runs again.
- *Meets every criterion but is not what was wanted*: a request change. The owner's words
  are recorded on the card and folded through `add-to-card` in settled mode; the spec is
  re-derived for the conditions those criteria feed and re-stamped; the work continues to a
  second acceptance. The gap entry notes that Ready was earned on a spec that did not ground
  the outcome.
- *Wants something the request never asked for*: a new card by default, with the current
  one accepted as specified. Amended into this card only when the addition is inseparable
  from the outcome under review.

Acceptance is asked against the evidence plan: every criterion is shown with its artifact
and promise, caveats flagged, the line "no review passed this revision" with its findings
when the build's report carries it, and one question accepts them all or names the refused
ones by ID, so a refusal arrives already classified.

## 7. The decision line and the standing answers

**The decision line** (principle 5) is stated once in `references/decision-line.md` and
applied by the readiness checker, the build session and the coordinator, and by every
skill before it asks the requester anything, after the standing answers. The requester
decides: what an observer of the system sees or can do; what persisted data ends up as;
scope. The developer decides: internal structure; anything a recorded decision, the
profile, a design system or an existing pattern in the code already answers; anything the
spec delegates. When several sub-issues share a gap, the checker asks for the rule, not the
case.

**The standing answers** are profile entries: the requester-side questions a project has
answered once that would otherwise be asked every run, such as whether a data change is
rehearsed and how, or what a push carries. Each entry is the question, its answer, and one
short citation of the card numbers it came from; quotes, versions, commits and dates stay
in the gap ledger and git. The plugin ships no answers; it ships the rule that a question
answered the same way on two separate occasions (separate runs or separate questions,
several entries about one event counting once) becomes a profile entry, and the `curate`
skill proposes them from the gap records for the owner to accept.

**The profile does not build up.** Only the readiness checker and the skills' "Before
anything is asked" test read Standing answers; the change reviewer reads the test gate and
the environments, and the Done judge the test gate. `curate` loads the profile as it stands
on the integration branch (`devfactory profile --rev <integration branch>`), under its own
marker, and reads the gap ledger, every live `gaps.md` and the review ledger. It counts an
event once, entries with the same question on the same date being one event; groups the
misses by the condition that let them through and lists the request changes apart, never
counting one against a condition; and groups the review findings by Done condition and by
text that repeats across cards. It classifies every finding before it proposes anything,
by the test `references/decision-line.md` states under "Classifying a proposal", which
`release` points to as well: plugin-general, reported as a plugin defect and recorded as
"sent to the plugin"; the developer's side of the decision line, reported and not written;
a project fact the template has a section for, proposed for it; a matter the project's own
documents govern, proposed there and never edited by `curate`; and only then a standing
answer. It drops
what the plugin, the recorded decisions, the project instructions, the project's skills
or the profile already hold, and recommends writing only profile facts and standing
answers. Each pass first tests every standing answer and curated line for retirement:
once the plugin or the project's own records hold it, a code identifier or figure it names
has changed, or the condition it answers can no longer arise, it is proposed for
deletion in the same question, and deleted outright with its new home named in the commit
message.

## 8. Plugin layout

```
DevFactory/
  .claude-plugin/marketplace.json
  README.md                 what DevFactory is and how a project uses it
  BUILD-BRIEF.md            voice, form and terms for authors of the plugin's files
  CLAUDE-FIRST.md           the interfaces the plugin's files share
  DESIGN.md
  devfactory/
    .claude-plugin/plugin.json
    skills/
      configure-project/    the profile: board, specs, test gate, environments, data access,
                            concerns, wireframe fidelity, branches, hooks, permissions
      create-card/          a card to the card standard, with stable criterion IDs and the
                            two core sections; a parent issue's title, purpose, work order
                            and model and effort, its sub-issues linked as the binding says
      add-to-card/          fold an addition, interactive or settled; re-derive the spec
                            unless the caller passes no-rederive and re-derives itself
      re-evaluate-card/     audit a card against the standard, or restructure a parent that
                            carries a part beyond its four; re-derive the spec
      grill/                draft the spec from the card, code, decisions and data; run the
                            checker; ask; stamp; commit; write the spec line; for a parent,
                            grill its set and run the set check
      check-ready/          the readiness check alone, for a card or a parent's set, at
                            creation from grill or at development start from coordinate;
                            reports, asks, folds
      start/                start work on a card: read it once and hand a parent issue to
                            coordinate and a standalone card to build
      coordinate/           a parent issue on the Claude desktop app: agents read the run,
                            one question starts every session, settle, relay, merge, judge,
                            accept
      build/                one card in one session: check the stamp, make the delegated
                            calls, build, review, record the review, report
      accept/               show the owner every criterion's evidence, accept in one answer;
                            classify a refusal; hand to release
      release/              rebase and gate; ledger the gaps and reviews and delete specs
                            and records folders; merge and ship by the profile's procedure;
                            close cards; capture post-release evidence; curate; archive
                            sessions, remove worktrees, branches and review checkouts;
                            list each step's outcome
      curate/               read the gap and review records; count each event once; classify
                            each finding, report plugin defects and decision-line misses,
                            propose profile entries and retirements
    agents/
      card-reviewer.md      measures a card against the card standard
      readiness-checker.md  applies the Definition of Ready
      change-reviewer.md    applies Done conditions 1 to 5 to one card's change
      done-judge.md         applies the Definition of Done to a parent branch
    references/
      card-standard.md, card-template.md, card-process.md, working-a-card.md, modules/
      definition-of-request.md, definition-of-ready.md, definition-of-done.md,
      decision-line.md
      spec-template.md, profile-template.md
      events.md             the events, when each fires and by whom, and how a project
                            hooks them
      test-gate.md          when the test gate runs, who runs it, what a recorded pass is
                            worth
      spec-procedure.md     the passages grill and check-ready share: dispatching the
                            checker, asking, folding, a card-changing answer, the ready
                            receipt, landing a commit
      reporting-to-the-coordinator.md   how a session in a parent run reports, asks, stops
                            and waits
      bindings/github-projects.md, bindings/azure-devops.md
      agents.md             each agent, the skill that starts it and the references it
                            reads
      examples/work-type-module.md   a team module example, a Work Type field
    scripts/
      devfactory.py         the machine checks and helpers: stamp, stamp-check, spec-lint,
                            criteria-ids, gaps add, gaps check, gaps ledger,
                            evidence-check, spec-only, reviews add, reviews show,
                            reviews ledger, receipt write, receipt check, begin, end,
                            markers, profile, event
      README.md             the commands, their flags and exit codes
      tests/                the script's tests
    hooks/
      hooks.json            the four hooks, each switched by its line in the profile
      guard_tracker.py      PreToolUse (Bash, PowerShell): refuses any tracker command that
                            is not a known read while no skill that writes cards runs
      guard_git.py          PreToolUse (Bash, PowerShell): refuses a push while a card skill
                            other than release or coordinate runs, and a change to a
                            protected branch, except as the running skill's marker allows
      stamp_notice.py       UserPromptSubmit: says whether a named card's spec is current
      session_context.py    SessionStart: the profile, the event hooks, every skill by its
                            full name, the decision line and the markers
      hooks_lib.py          shared by the hooks: input, repository root, command tokens,
                            profile and markers through the script
      tests/                the hooks' tests
```

**Scripts.** `scripts/devfactory.py` decides every `[machine]` condition that has a command
(`stamp`, `stamp-check`, `spec-lint`, `criteria-ids`, `gaps`, `evidence-check`), confirms a
change is spec-only past the review limit (`spec-only`), records, shows and ledgers the reviews
(`reviews`), writes and compares the receipts (`receipt`), holds the markers (`begin`,
`end`, `markers`), is the one profile reader (`profile`), and fires the events (`event`).
Every command declares its flags, an unknown flag is a usage error, and `--help` prints the
commands and their flags; `scripts/README.md` is the statement of each command's flags,
output and exit codes. Every script and hook is Python 3, standard library only, run with
`python`, and tested with `unittest`; the plugin has no Node dependency. In the owner's
words (the owner, 2026-11-07): "I'm much more comfortable using Python scripts than Node for
anything." The script and the hooks find the profile, the markers and the ledgers under
`.devfactory/` at the repository (or worktree) root, wherever the shell's working directory
is.

**Markers.** A skill marks itself running with `begin <skill>` and `end <skill>`, which
write and remove `.devfactory/.active/<skill>`. `begin` prints `began <skill> <plugin
version>` and stores the version in the marker; when it refreshes a marker written under
another version it also prints `plugin-changed <old> <new>`, and the skill loads itself
again before it continues. A marker expires after the profile's Marker lifetime, a line of
its Hooks section, 12 hours by default, and an expired marker counts as no skill running.
`begin` refreshes a marker, and every skill that holds one across a wait runs `begin` again
on resume. A `devfactory begin <skill>` earlier in the same command counts, for both guards,
as that skill's fresh marker for the rest of that command. `markers` lists the markers and,
with `--clear-stale`, removes the expired ones.

**Hooks.** Four ship in `hooks/hooks.json`, each switched on or off by its line in the
profile's Hooks section, all on by default. Each allows silently on a missing profile, when
its line says off, and on any error of its own. Both guards judge every command a session
gives its Bash or PowerShell tool, in each part of the command line and inside `bash -c`,
`sh -c` and `powershell -Command`.

- The **tracker guard** refuses every `gh issue`, `gh project`, `gh label` and `az boards
  work-item` subcommand that is not a known read, every `gh api` call that is not a GET,
  and every `az rest` call that is not a GET against a work-item API, unless a skill that
  writes cards is running: `create-card`, `add-to-card`, `re-evaluate-card`, `grill`,
  `check-ready`, `build`, `coordinate`, `accept`, `release` or `configure-project`. A
  `start` or `curate` marker does not unlock it.
- The **git guard** protects the integration branch and every parent branch, and judges a
  command by its effect on one. It refuses a push while any skill other than `release` or
  `coordinate` holds a fresh marker, and allows one when no skill is running, so work that
  belongs to no card is pushed without one. It refuses any change to a protected branch: a
  merge, pull, rebase, cherry-pick, hard reset, a reset to a revision in any mode, an amend,
  a forced branch move, a rename or delete of it (`branch -m|-M|-d|-D`), an `update-ref` of
  `refs/heads/<branch>`, or a `checkout -B` or `switch -C` of it, while HEAD is on it, the
  same through `cd`, `git -C`, `--git-dir` or `--work-tree` into its worktree, or a command
  that names it. A `checkout` or `switch <branch>` earlier in the same command sets the
  branch later parts are judged against. Every path is resolved to one canonical form before
  matching, so a Windows path with either slash, an MSYS `/c/…` path and a Cygwin
  `/cygdrive/c/…` path name one place; a target it cannot resolve to a repository, and a
  `git -c alias.<x>=…` invocation, are refused while the session is guarded. Merging,
  pulling or rebasing a protected branch into an unprotected one is never refused, nor is a
  plain commit. A `release` or `coordinate` marker allows everything, except that a session
  whose own root holds a fresh `build` marker gains nothing from a `release` or `coordinate`
  marker in another root. A `build` marker allows the fast-forward into a parent branch,
  which a build session makes with `git -C <parent worktree> merge --ff-only <branch>` from
  its own worktree. A `grill` marker allows its spec commit and fast-forward onto the
  integration branch, so `grill` holds its marker through the spec commit and the spec
  line. A `create-card`, `re-evaluate-card`, `check-ready` or `curate` marker allows the
  same fast-forward, which lands a receipt, a re-stamped spec or a profile change.
- The **stamp notice** gives a prompt that names a card with a spec the result of
  `stamp-check`. It never blocks.
- The **session context** gives a session in a project with a profile the profile's
  location, the project's event hooks, every skill by its full name (`devfactory:start` and
  the rest), the decision line and the active and stale markers.

**Agents** carry their character, inputs, rules, report format and checklist, with `name`,
`description`, `tools` and `model` in their frontmatter, and read the references their
definitions name, so a definition works only with those references beside it
(`references/agents.md`). The four run
read-only on the most capable model, and skills start them by name with the Agent tool,
after reading the definition's Inputs section rather than the whole definition, passing
every input it lists and no model. They decide each `[machine]` condition by running the
command the definition names and quoting its output. Build sessions run on the card's
suggested model and effort, or the profile's default.

**Skills** declare their pre-approved commands in `allowed-tools`, and paths in a skill are
relative to its folder. Each skill's "Read these first, in full" opens by saying a file
already read in full in the session, under the plugin version `begin` printed, need not be
read again. No skill tells a session to read another skill's `SKILL.md`: a passage two
skills need lives in a reference.

**The coordinator** names the Claude desktop app's session tools directly and needs the
desktop app; the card and spec skills run in any Claude Code client.
