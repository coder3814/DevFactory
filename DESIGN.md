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

## 2. The objects

### 2.1 The card

A work item on the project's tracker, written to the card standard: title, summary, the
issue or request, what needs to be achieved, scope, supporting information, open questions,
acceptance criteria. Two further sections are core, because every run of sessions needs
them:

- **Suggested model and effort**, after the acceptance criteria. A build session runs on
  it, or on the profile's default when the card suggests none.
- **Work order**, on a parent issue only: its sub-issues in the order to work them, each
  saying what it waits on (one of: needs the other's result; changes the same files; both
  need something only one session can hold) and which may run alongside it. Sub-issues run
  in parallel by default.

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
  what produced it.

The card points at its spec with exactly one line, `Spec: <path> @ <commit>`, the last line
of the description body, where the commit is the spec folder's own commit. `grill` rewrites
that line after every commit of the spec folder, and the card revision the stamp hashes
excludes any line of that form, so writing it never makes the spec stale.

The spec is written before development starts, wherever the card sits on the board, and lands on the
integration branch through a commit of its own. During development it is amended on the
sub-issue's branch and merges with the work. At release its gap entries are appended to the
project's gap ledger and the folder is deleted, not archived; history keeps it, and the
durable facts have already gone wherever the project keeps decisions.

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
   environment (checkpoint) it is captured in.
8. **Owner steps**: each step only the requester can take (approve a mock-up, sign in
   somewhere, run something in production) with the moment in the run it happens.
9. **Project bindings used**: the profile entries this spec relies on, by name.
10. **Amendments**: version, date, what changed, and the gap or rejection that drove it.

### 2.4 The project profile

One folder per project, `.devfactory/` at the repository root:

- `profile.md`: the profile.
- `modules/`: the team modules the profile names.
- `gaps.md`: the gap ledger, the gap records of released cards (section 2.7).
- `.active/`: the marker folder the hooks read (section 8), ignored by git.
- `hooks/`: the project's event hooks, one script per event it wants acted on (section 3).

`profile.md` holds, each as its own section:

- **The board**: the tracker binding and the entries it asks for; the field each part of a
  card is written to; any additional fields with the team module that works each one (a
  module may have no field and hold rules for the card as a whole). It names no board
  column: no skill reads a card's column or moves a card.
- **The work**: where specs live; where recorded decisions live, so the checker can read
  them (they are never kept in the profile); the test gate, the command or procedure that
  proves existing behaviour; the environments available for checkpoints and what each can
  and cannot show; **Data access**, each population of existing data a card's rules might
  act on and how it is read without writing, which `grill` and the readiness checker run
  data rules through; the fixed-concern list extensions; the owner-step types the project
  has.
- **Wireframe fidelity**: what the approved design artifact fixes (section 2.5), with a
  **Design review** line saying how a wireframe is shown to the requester and approved.
- **Branches and merging**: the integration branch, the worktree layout, how a parent branch
  and a sub-issue branch are named, who merges what and when, and the release procedure
  (the project's steps or the skill it names).
- **Sessions**: the default model and effort.
- **Hooks**: one on or off line per hook, all on by default, and the Marker lifetime.
- **Permissions**: the read-only allowlist entries `configure-project` writes to the
  project's `.claude/settings.json`, so the skills' reads run without a prompt. A write to
  the tracker or to a branch is never pre-approved.
- **Standing answers** (section 7).

`configure-project` writes the profile from the board, the repository and the owner's
answers. It takes the answers its caller already holds and asks only the rest, commits the
profile or tells the owner to, and says that hook changes take effect in the next session.

### 2.5 Wireframe fidelity

The approved design artifact grounds Ready condition 6.2. The profile chooses what it fixes:

- **Wireframe**, the default: structure, fields, states and interaction, not aesthetics.
- **Finished mock-up**: the artifact is a complete design.
- **Design card**: the design is a card of its own, grilled and accepted first, and the
  development card's spec references that card's approved mock-up, which meets condition
  6.2 without a file in the spec folder. As the owner put it (the owner, 2026-11-07): "When
  coming up with a design, that should be a card of its own. It can move from a wireframe
  but should have a full, fleshed-out, approved mockup in the equivalent of completed HTML
  for any interface change. That completed HTML would then be used in the implementation of
  a development card."

### 2.6 The definitions

`references/definition-of-ready.md` and `references/definition-of-done.md`: numbered
conditions, each tagged `[machine]`, `[rubric]` or `[judgment]`. Sections 4 and 5 are their
content. Every `[machine]` condition is decided by a command of the plugin's script,
`scripts/devfactory.py`, which the condition names, never by an agent reading. A machine
condition no command covers yet says so in its tag, and the definition lists it under
"Machine conditions without a script yet".

### 2.7 The gap record

`gaps.md` beside the spec: one entry per question asked from Ready onward, per refused
acceptance, and per Done-check miss, each naming the Ready or Done condition that let it
through. A question answered before the spec first earns Ready is folded into the spec, not
recorded as a gap.

Gap records survive release: before a spec folder is deleted, its entries are appended to
the project ledger `.devfactory/gaps.md`, each under the card ID and the spec's request
types. The readiness checker reads the ledger and every live `gaps.md` before grilling, so a
recurring class is asked up front next time, and `curate` reads the same records.

### 2.8 The receipts

Without receipts every hand-off re-judged what the stage before it had just judged: `grill`
started a fresh card reviewer on a card `create-card` had just passed, and the start of a
parent issue run started a fresh readiness checker on specs `grill` had just stamped. That
cost the time of the check, and because a fresh reviewer finds something different every
time, it raised new questions about content that had not changed.

A receipt records, field by field, the fingerprint of everything a passing check read, in
`receipts.md` in the card's spec folder, committed with the code. `devfactory receipt write`
writes it and `devfactory receipt check` compares it; nothing else reads or writes the file.

- **Request**, written when the card reviewer finds the card meets the Definition of Request
  and the card as written is exactly what it measured: the card revision, a hash of the card
  facts (each team field, each comment with its text, each attachment, the parent and the
  sub-issues in the tracker's order, and the related data a team module names), the
  plugin's version with a hash of its references and agents, and a hash of the profile and
  its team modules. `create-card` and `re-evaluate-card` write it; `grill`'s request gate
  compares it and starts a reviewer only when it differs, writing a new one on a pass.
- **Ready**, written when `grill` stamps a spec Ready and when `check-ready` finds nothing
  open: the spec folders measured together, a hash of their files with the Status value left
  out so approval keeps it matching, a hash of the gap ledger and every live gap record, the
  standard, the profile, and the head commit the check read. The commit matches while it is
  an ancestor of the head and nothing outside the specs path and `.devfactory/` has changed
  since, because everything under those is fingerprinted on its own. `check-ready` compares
  it at development start, after the stamps, and starts no checker when it matches.

A receipt never replaces the stamp. The stamp says the spec still answers the card; the
receipt says a check need not run again.

## 3. The lifecycle

| Stage | What happens | Who acts | Exit |
|---|---|---|---|
| Request | The card is created or restructured under the card standard, and request grilling asks the owner every question the card reviewer raises and every open question, until none is left. | `create-card`, `re-evaluate-card`, the card reviewer agent, the owner | The card meets the Definition of Request |
| Grilling | Specification grilling first checks the card against the Definition of Request, which a matching request receipt has already done, then drafts the spec from the card, the code, the recorded decisions and the data population; the readiness checker measures it; the owner answers each question only the spec settles. It never changes the card: a question whose answer would is handed back to request grilling. | `grill`, the card reviewer and readiness checker agents, the owner | Ready earned and stamped |
| Approval | The owner approves the Ready spec. For a parent issue, every sub-issue is Ready first. | the owner | Spec status `approved` |
| Development | A build starts only on an approved spec. One session per sub-issue builds from the spec in its own worktree; questions go through the coordinator as gaps; each session's work is reviewed by a separate agent against the spec; results merge into the parent branch. | `coordinate`, `build`, the change reviewer agent | Every sub-issue merged |
| Done | The Done judge measures the parent branch against the parent spec and the Definition of Done; a standalone card's passing change review is its Done verdict. Past the review or judgment limit, a round whose findings were all fixed by spec-only amendments goes on to acceptance as Done. | the Done judge agent | Done verdict, or a spec-only round past the limit |
| Acceptance | The owner judges the result against the evidence: every criterion is shown with its artifact, and one question accepts them all or names the refused ones. A refusal is classified (section 6.2). | `accept`, the owner | Accepted |
| Release | Merge, push, release and close by the profile's release procedure; gap entries appended to the ledger; specs deleted; sessions, worktrees and branches removed; gap records curated. | `release` | Cards closed |

Three definitions gate the work, one per hand-off: the Definition of Request
(`references/definition-of-request.md`) before a spec is written, the Definition of Ready
before a build, the Definition of Done before acceptance. Each is checked by an agent where
the work changes hands, never by where the card sits.

**The board is the project's.** Every skill works a card wherever it sits, and no skill
moves one. At each hand-off the skill fires an event — `request-met`, `ready`, `approved`,
`work-started`, `development-started`, `readiness-lost`, `done`, `refused`, `accepted`,
`released` — with `devfactory event`, which runs
the project's hook for it in `.devfactory/hooks/` if there is one and does nothing
otherwise (`references/events.md`). A project that wants its cards moved, to whatever
columns its board has, writes those hooks; a failed hook is reported and never holds back
the work.

`build` and `coordinate` check the spec's status before any work
starts. Results merge into the parent branch in the order they finish, except that a card
that waits on another merges after the card it waits on. A standalone card is not merged
when its review passes; `release` merges it once, after acceptance.

**Loops are bounded.** After a change review or the Done judge fails, the work gets at most
two further rounds. A third failure asks nothing when every finding is on the developer's
side (a missing test, an incomplete evidence record, a spec that no longer matches the
built code with no change to what an observer sees): the findings are fixed, a code fix
gets one more review or judgment, and a spec-only amendment goes straight on to
acceptance. Only findings that change what an observer sees or can do, what persisted data
ends up as, or scope stop the work and go to the requester, through the coordinator in a
parent issue run.

**Sessions are kept.** In a parent issue run, each sub-issue's session, worktree and branch
are kept until the run is accepted and released. A Done-judge finding or a refusal that
belongs to one sub-issue is fixed by that sub-issue's kept session, on its branch rebased
onto the parent branch; one no sub-issue owns is fixed by the run's parent-fixes session,
started with the others and waiting for such findings. Either is reviewed and merged as any
sub-issue's work is.

**Every session starts in the requester's turn.** The Claude desktop app starts a session
only on a turn the requester's own message began; on a notification turn a start waits for
a click. So the coordinator starts every sub-issue's session and the parent-fixes session
in the turn of the "start work" message, each briefed to wait for the readiness check and
for its work-order waits, and then sets each going by message, which works from any turn.
A sub-issue added mid-run is the one start that can wait for a click.

**Stops are few.** Before any question reaches the requester it is tested against the
profile's Standing answers and the decision line (section 7). A step the process already
prescribes, such as going into acceptance after the Done judge's DONE, is not asked for.
The release is asked once, or not at all when the requester authorised it ahead of time,
in their starting instruction or their acceptance answer. `curate` asks once per pass,
with every proposal numbered, and drops what the profile already holds or has declined.

## 4. Definition of Ready

A spec is Ready when every condition holds, evaluated over the card, the spec, the profile
and the repository. Cheap presence checks come first; the end-to-end test is last.

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
4.2 Each disposition is true of the request as specified. `[judgment]`
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
    parallel would collide, and no wait holds back work that could run. `[judgment]`

**9. The spec grounds the work**
9.1 Every project binding the spec relies on exists in the profile. `[machine]`
9.2 The spec is stamped with the card revision and the repo commit it was checked against,
    the commit being the branch head the checker read. The condition holds when the card's
    revision equals the stamp's and the stamped commit is an ancestor of the current head.
    It is not applicable at creation, before the stamp exists, or in a re-derive check.
    `[machine]`
9.3 A fresh agent could decompose and build the work from the card, the spec, the profile
    and the repository without a single new question, every decision either grounded in them
    or delegated under principle 5. `[judgment]` This is the purpose of the definition tested
    directly; conditions 1 to 8 catch its common failures cheaply.

The definition does not trace criteria through tags in commits, which needs a commit
discipline the plugin cannot enforce; does not require video evidence, since capture
capability is the project's; has no per-spec rubric set, since the profile binds the few
terms that vary; and keeps the existing-behaviour gate in the profile rather than in each
spec.

## 5. Definition of Done

A change is Done when every condition holds, evaluated over the spec, the base revision and
the revision under evaluation.

**1. The tests exist and pass**
1.1 The profile's test gate passes at the revision under evaluation. `[machine]`
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
    produced it. `[machine]`

**4. The work is grounded**
4.1 Every decision embodied in the work is grounded in the spec or recorded as a delegated
    call in the spec's log. `[judgment]`
4.2 The gap record is closed: every gap has a resolving amendment. `[machine]`
4.3 Every disposition is still true of the delivered result. `[judgment]`

**5. Nothing beyond the request**
5.1 Every change in the change set serves a criterion, a delegated call or the work's own
    scaffolding. `[judgment]`

**6. For a parent issue**
6.1 Every parent criterion is met by the combined result, including what no single sub-issue
    could show. `[judgment]`

Exclusions: intent is not gated; the owner judges it at acceptance. Nothing is checked by
taste; every check carries a mode.

The change reviewer applies conditions 1 to 5 to one card's change; the Done judge applies
the whole definition to a parent branch.

## 6. Change handling

### 6.1 Before development

A card changes only through the plugin's card skills, which the tracker guard enforces
(section 8). Each skill, after writing the card, re-derives the spec for the conditions the
changed part feeds, re-stamps, and reports what changed. A change to the interface
determination or to a scope boundary re-grounds the whole spec. A comment that changes no
part of the card changes nothing. An addition is folded wherever the card sits; a card with
a spec is protected by its stamp, not by a frozen column. A direct edit on the tracker is caught by the stamp at the
next check and handled the same way.

`add-to-card` runs in one of two modes, named by its caller:

- **Interactive**, the default: the addition is recorded and folded, and the requester
  accepts the rewritten wording or asks for changes. This holds for additions made outside
  a run and outside approval.
- **Settled**: the requester has already answered (a request question handed back from
  specification grilling, a change asked for at approval, a relayed question, a refusal). The answer is the acceptance; the fold is written without a further round on
  its wording, and the requester may still object.

### 6.2 During development

A card is not frozen when development starts: a request change is accepted as an amendment.
Only two things change a spec in development.

**A question the spec did not answer.** The session first applies principle 5 and the spec's
delegations; a question they answer is decided and logged, not asked. A surviving question
goes to the coordinator in a fixed shape: the question, the options, a recommendation, and
the Ready condition that failed. The owner's answer becomes a spec amendment on the
sub-issue's branch and a gap entry. When the answer changes the card, it goes onto the card
first, through `add-to-card` in settled mode, and the amendment then checks the changed card
against the Definition of Request; `grill` itself never writes the card. A changed dependency re-checks
the work order. The session rebases on the amended spec and continues.

**An acceptance not given.** The refusal names the criterion the result fails or states the
outcome that is missing, and that sorts it:

- *Fails a stated criterion*: a defect, not a change. It is fixed as section 3 says, by the
  kept session that owns it; the Done judge's miss is a gap entry against the Done
  condition.
- *Meets every criterion but is not what was wanted*: a request change. The owner's words
  are recorded on the card and folded through `add-to-card` in settled mode; the spec is
  re-derived for the conditions those criteria feed and re-stamped; the work continues to a
  second acceptance. The gap entry notes that Ready was earned on a spec that did not ground
  the outcome.
- *Wants something the request never asked for*: a new card by default, with the current
  one accepted as specified. Amended into this card only when the addition is inseparable
  from the outcome under review.

Acceptance is asked against the evidence plan: every criterion is shown with its artifact
and promise, caveats flagged, and one question accepts them all or names the refused ones
by ID, so a refusal arrives already classified.

## 7. The decision line and the standing answers

**The decision line** (principle 5) is stated once in `references/decision-line.md` and
applied by the readiness checker, the build session and the coordinator, and by every
skill before it asks the requester anything, after the standing answers. The requester
decides: what an observer of the system sees or can do; what persisted data ends up as;
scope. The developer decides: internal structure; anything a recorded decision, the
profile, a design system or an existing pattern in the code already answers; anything the
spec delegates. When several sub-issues share a gap, the checker asks for the rule, not the
case.

**The standing answers** are profile entries: the questions a project has answered once that
would otherwise be asked every run, such as where post-release checks run, whether a data
change is rehearsed and how, what a push carries, how finished branches are removed, or
which models run the project's own pipeline agents. Each entry is the question as it was
asked, its answer, and where the answer came from. The plugin ships no answers; it ships the
rule that a question answered twice in gap records becomes a profile entry, and the `curate`
skill proposes them from the gap records for the owner to accept.

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
                            two core sections
      add-to-card/          fold an addition, interactive or settled; re-derive the spec
      re-evaluate-card/     measure a card against the standard; re-derive the spec
      grill/                draft the spec from the card, code, decisions and data; run the
                            checker; ask; stamp; commit; write the spec line
      check-ready/          the readiness check alone, for a card or every sub-issue of a
                            parent; reports, asks, folds
      coordinate/           a parent issue on the Claude desktop app: start every
                            session up front, settle, relay, merge, judge, accept
      build/                one card in one session: check the stamp, make the delegated
                            calls, build, review, report
      accept/               show the owner every criterion's evidence, accept in one answer;
                            classify a refusal
      release/              release by the profile's procedure; ledger the gaps; delete
                            specs; close cards; remove sessions, worktrees and branches
      curate/               read the gap records; propose checker emphasis and profile
                            entries
    agents/
      card-reviewer.md      measures a card against the card standard
      readiness-checker.md  applies the Definition of Ready
      change-reviewer.md    applies Done conditions 1 to 5 to one card's change
      done-judge.md         applies the Definition of Done to a parent branch
    references/
      card-standard.md, card-template.md, card-process.md, working-a-card.md, modules/
      definition-of-ready.md, definition-of-done.md, decision-line.md
      spec-template.md, profile-template.md
      bindings/github-projects.md, bindings/azure-devops.md
      agents.md             each agent and the skill that starts it
      examples/work-type-module.md   a team module example, a Work Type field
    scripts/
      devfactory.py         the machine checks and helpers: stamp, stamp-check, spec-lint,
                            criteria-ids, gaps add, gaps check, gaps ledger,
                            evidence-check, receipt write, receipt check, begin, end,
                            markers, profile, event
      README.md             the commands, their arguments and exit codes
      tests/                the script's tests
    hooks/
      hooks.json            the four hooks, each switched by its line in the profile
      guard_tracker.py      PreToolUse: refuses a tracker write while no card skill runs
      guard_git.py          PreToolUse: refuses a push, or a change to a protected branch,
                            except as the running skill's marker allows
      stamp_notice.py       UserPromptSubmit: says whether a named card's spec is current
      session_context.py    SessionStart: the profile, the event hooks, the skills to use
                            and any active marker
      hooks_lib.py          shared by the hooks: input, repository root, command tokens,
                            profile and markers through the script
      tests/                the hooks' tests
```

**Scripts.** `scripts/devfactory.py` decides every `[machine]` condition that has a command
(`stamp`, `stamp-check`, `spec-lint`, `criteria-ids`, `gaps`, `evidence-check`), writes
and compares the receipts (`receipt`), holds the
markers (`begin`, `end`, `markers`), is the one profile reader (`profile`), and fires the
events (`event`). Every script
and hook is Python 3, standard library only, run with `python`, and tested with `unittest`;
the plugin has no Node dependency. In the owner's words (the owner, 2026-11-07): "I'm much
more comfortable using Python scripts than Node for anything." The script and the hooks find
the profile, the markers and the gap ledger under `.devfactory/` at the repository (or
worktree) root, wherever the shell's working directory is.

**Markers.** A skill marks itself running with `begin <skill>` and `end <skill>`, which
write and remove `.devfactory/.active/<skill>`. A marker expires after the profile's Marker
lifetime, a line of its Hooks section, 12 hours by default, and an expired marker counts as
no skill running. `begin` refreshes a marker, and every skill that holds one across a wait
runs `begin` again on resume. `markers` lists the markers and, with `--clear-stale`,
removes the expired ones.

**Hooks.** Four ship in `hooks/hooks.json`, each switched on or off by its line in the
profile's Hooks section, all on by default. Each allows silently on a missing profile, when
its line says off, and on any error of its own.

- The **tracker guard** refuses a tracker write (an issue edit, comment or create, a project
  item edit or add, the Azure DevOps equivalents, a GraphQL mutation or a query read from a
  file, and any other API call that is not a GET) unless a card-writing skill is running:
  `create-card`, `add-to-card`, `re-evaluate-card`, `grill`, `check-ready`, `build`,
  `coordinate`, `accept` or `release`. A `configure-project` or `curate` marker does not
  unlock it.
- The **git guard** protects the integration branch and every parent branch. It refuses any
  push, and any change to a protected branch: a merge, pull, rebase, cherry-pick, hard
  reset, amend or forced branch move while HEAD is on it, the same through `cd` or `git -C`
  into its worktree, or a rebase that names it. Merging, pulling or rebasing a protected
  branch into an unprotected one is never refused, nor is a plain commit. A `release` or
  `coordinate` marker allows everything. A `build` marker allows the fast-forward into a
  parent branch, which a build session makes with
  `git -C <parent worktree> merge --ff-only <branch>` from its own worktree. A `grill`
  marker allows its spec commit and fast-forward onto the integration branch, so `grill`
  holds its marker through the spec commit and the spec line. A `create-card` or
  `re-evaluate-card` marker allows the same fast-forward, which lands a request receipt.
- The **stamp notice** gives a prompt that names a card with a spec the result of
  `stamp-check`. It never blocks.
- The **session context** gives a session in a project with a profile the profile's
  location, the project's event hooks, the skills, the decision line and any active
  marker.

**Agents** carry their whole definition inline (character, inputs, rules, report format,
checklist), with `name`, `description`, `tools` and `model` in their frontmatter. The four
run read-only on the most capable model, and skills start them by name with the Agent tool,
passing every input the definition lists and no model. They decide each `[machine]`
condition by running the command the definition names and quoting its output. Build
sessions run on the card's suggested model and effort, or the profile's default.

**Skills** declare their pre-approved commands in `allowed-tools`, and paths in a skill are
relative to its folder.

**The coordinator** names the Claude desktop app's session tools directly and needs the
desktop app; the card and spec skills run in any Claude Code client.
