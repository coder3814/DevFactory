# DevFactory design

> Status: **draft for the owner's acceptance**. Nothing below is built. Once accepted, this
> document is the brief the plugin is built from, and it stays the design of record: when the
> built plugin and this document disagree, one of them is wrong and the disagreement is a
> finding.

DevFactory is one plugin that carries a change from a request to an accepted result with an
agent doing the work unattended. It owns the request (a card on a board), grills the request
into a specification that a fresh agent can build from without asking anything, runs the
build (a parent issue as one session per sub-issue), handles the two things that interrupt an
unattended build (a question the spec did not answer, and an acceptance not given), judges
the result Done against the spec, and records every miss so the grilling improves.

It is project-agnostic. Everything about one project lives in that project's **profile**,
which the plugin reads and never embeds.

## 1. Where the design comes from

Three sources, and what each contributes.

- **The card standard** (the `card-standard` plugin): what a good request looks like, how it
  is written and changed on a tracker, how a board is configured. Kept as the request layer,
  nearly whole.
- **Grillwork** (its Definition of Ready and Definition of Done): the claim that a spec
  exists to carry development to Done without a single additional question, enumerated
  conditions with a mode each, dispositions where silence is not valid, boundaries with
  reasons, the interface surface grounded before Ready, stable criterion IDs, the gap record,
  and the learning loop. Kept as the spec and judgement layer, trimmed.
- **The BottleNote run** (its `board-conventions`, `check-parent-issue-readiness` and
  `coordinate-parent-issue` skills, and the 240 owner questions those runs produced): the
  parent-issue coordination, the work order, the model-and-effort suggestion, and the
  evidence of which questions get asked and why. The analysis of those questions is the
  reason for every rule in sections 5 to 8.

## 2. Principles

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
9. **One runtime seam.** Only the coordinator touches session mechanics, in one section,
   so another runtime is that section rewritten.

## 3. The objects

### 3.1 The card

A work item on the project's tracker, written to the card standard: title, summary, the
issue or request, what needs to be achieved, scope, supporting information, open questions,
acceptance criteria. Two sections the BottleNote conventions added become core, because any
adopter that runs sessions needs them:

- **Suggested model and effort**, after the acceptance criteria.
- **Work order**, on a parent issue only: its sub-issues in the order to work them, each
  saying what it waits on (one of: needs the other's result; changes the same files; both
  need something only one session can hold) and which may run alongside it. Sub-issues run
  in parallel by default.

Criteria carry **stable IDs** (`C1`, `C2`, …) that survive amendment: a removed criterion's
ID is never reused, and a new one takes the next number. Work orders, comments, gap records
and evidence cite the ID, never the position.

### 3.2 The spec

One folder per card in the project repository, at the path the profile names (default
`specs/<card>/`), versioned with the code and outside any documentation system the project
runs. It holds:

- `spec.md`: the specification (section 3.3).
- `wireframe.*`: present when the interface determination is non-trivial.
- `gaps.md`: the gap record (section 7).
- `evidence/`: what the Done judge consumes, added during development.

The card carries one line pointing at the spec: its path and the commit at which it earned
Ready. The spec is written while the card is in a pre-development column and lands on the
integration branch through a commit of its own. During development it is amended on the
sub-issue's branch and merges with the work. At release the folder is deleted; history keeps
it, and the durable facts have already gone wherever the project keeps decisions.

### 3.3 What the spec holds

In this order, general to specific:

1. **Header**: card, version, Ready stamp (card revision hash, repo commit, date), request
   type(s).
2. **Decisions delegated to the developer**: the calls the grilling identified as the
   developer's under principle 5, listed so the builder knows they are its to make, and the
   log of the calls it made.
3. **Boundaries**: exclusions with reasons; deferrals with reasons; for each requirement, its
   edge behaviour either specified or named as excluded or delegated.
4. **Dispositions**: one line per fixed concern (section 5, condition 4).
5. **Interface surface**: the determination (non-trivial / trivial, because / not
   applicable, because) and, when non-trivial, the approved wireframe's path and the pages
   or screens it covers.
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

### 3.4 The project profile

One folder per project, `.devfactory/`, replacing `.card-standard/`:

- `profile.md`: the board (tracker binding and its entries, column field, columns, fold
  columns, the column each lifecycle stage maps to), where specs live, the test gate (the
  command that proves existing behaviour), the environments available for checkpoints and
  what each can and cannot show, how each population of existing data is read without
  writing, the fixed-concern list extensions, the owner-step types the
  project has, the branch and merge conventions (integration branch, worktree layout, how a
  parent branch is named), and the standing answers (section 8).
- `modules/`: team modules for additional fields, as today.
- `decisions/` is **not** here. Recorded decisions stay where the project keeps them; the
  profile names where that is so the checker can read them.

### 3.5 The definitions

`references/definition-of-ready.md` and `references/definition-of-done.md`: numbered
conditions, each tagged `[machine]`, `[rubric]` or `[judgment]`. Sections 5 and 6 are their
content.

### 3.6 The gap record

`gaps.md` beside the spec: one entry per question asked after Ready, per refused acceptance,
and per Done-check miss, each naming the Ready or Done condition that let it through. The
readiness checker reads the project's gap records before grilling, so a recurring class is
asked up front next time.

## 4. The lifecycle

| Stage | What happens | Who acts | Exit |
|---|---|---|---|
| Request | The card is created or restructured under the card standard. | `create-card`, the owner | Card accepted |
| Grilling | The spec is drafted from the card, the code, the recorded decisions and the data population; the readiness checker measures it; the owner answers each question once. | `grill`, the readiness checker agent, the owner | Ready earned and stamped |
| Approval | The owner approves the Ready spec. For a parent issue, every sub-issue is Ready first. | the owner | Spec status `approved`; the card waits in the Approval column until work starts |
| Development | One session per sub-issue builds from the spec in its own worktree; questions go through the coordinator as gaps; each session's work is reviewed by a separate agent against the spec; results merge into the parent branch in the work order. | `coordinate`, `build`, the change reviewer agent | Every sub-issue merged |
| Done | Merged work sits in the Done column. The Done judge measures the parent branch against the parent spec and the Definition of Done; a standalone card's passing change review is its Done verdict. Findings are fixed as sub-issue work. | the Done judge agent | Done verdict |
| Acceptance | The owner judges the result against the evidence, criterion by criterion. A refusal is classified (section 7.2). | the owner | Accepted |
| Release | Merge, push, release and close as the profile's conventions say; specs deleted; gap record curated. | `release` | Cards closed |

The profile maps each stage to a board column. A project whose board has fewer columns maps
several stages to one.

## 5. Definition of Ready

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

**4. The fixed concerns are disposed**
4.1 Every concern on the list has a disposition; "not applicable, because X" is one.
    `[machine: presence]` The core list: existing data changed; security; performance;
    release sequencing (does the change need anything before or after the deploy); owner
    steps. The profile may extend it.
4.2 Each disposition is true of the request as specified. `[judgment]`
4.3 A non-trivial disposition's demands appear as criteria or evidence rows. `[machine]`

**5. The data population is checked** (when the request's rules act on existing data)
5.1 The rules were run read-only against the population the spec names, with counts per
    rule. `[machine: presence]`
5.2 Every row no rule covers is resolved by a rule, an exclusion or a delegation. `[judgment]`

**6. The interface surface is grounded**
6.1 The determination is stated: non-trivial, trivial because, or not applicable because.
    `[machine]`
6.2 When non-trivial, the wireframe is present and approved, and grounds structure, fields,
    states and interaction. `[machine: presence; judgment: grounding]`

**7. The evidence plan is complete**
7.1 Every criterion has an evidence row naming artifact, what it shows, condition, how it is
    generated and the checkpoint. `[machine]`
7.2 Every row could be failed by a delivered artifact. `[judgment]`
7.3 Every checkpoint named is one the profile's environments can provide. `[machine]`

**8. The owner's part is scheduled**
8.1 Every owner step has a moment in the run. `[machine: presence]`
8.2 For a parent issue, the work order's waits each cite an allowed reason, no pair marked
    parallel would collide, and no wait holds back work that could run. `[judgment]`

**9. The spec grounds the work**
9.1 Every project binding the spec relies on exists in the profile. `[machine]`
9.2 The spec is stamped with the card revision and repo commit it was checked against, and
    the card matches the stamp. `[machine]`
9.3 A fresh agent could decompose and build the work from the card, the spec, the profile
    and the repository without a single new question, every decision either grounded in them
    or delegated under principle 5. `[judgment]` This is the purpose of the definition tested
    directly; conditions 1 to 8 catch its common failures cheaply.

Dropped from Grillwork and why: per-criterion tag traceability from commits (needs tooling
and a commit discipline the plugin cannot enforce), video evidence (capture capability is
the project's), the per-spec rubric set and instantiation (the profile binds the few terms
that vary), and the existing-behaviour gate as a spec entry (it is a profile entry).

## 6. Definition of Done

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

## 7. Change handling

### 7.1 Before development

A card change goes only through the plugin's card skills (the board conventions already
require this). Each skill, after writing the card, re-derives the spec for the conditions
the changed part feeds, re-stamps, and reports what changed. A change to the interface
determination or to a scope boundary re-grounds the whole spec. A comment that changes no
part of the card changes nothing. A direct edit on the tracker is caught by the stamp at the
next check and handled the same way.

### 7.2 During development

Only two things change a spec in development.

**A question the spec did not answer.** The session first applies principle 5 and the spec's
delegations; a question they answer is decided and logged, not asked. A surviving question
goes to the coordinator in a fixed shape: the question, the options, a recommendation, and
the Ready condition that failed. The owner's answer becomes a spec amendment on the
sub-issue's branch and a gap entry. The card changes only when the answer alters observable
behaviour or scope, through `add-to-card`, with the answer as the acceptance and no second
round on wording. A changed dependency re-checks the work order. The session rebases on the
amended spec and continues.

**An acceptance not given.** The refusal names the criterion the result fails or states the
outcome that is missing, and that sorts it:

- *Fails a stated criterion*: a defect, not a change. The session fixes it; the Done judge's
  miss is a gap entry against the Done condition.
- *Meets every criterion but is not what was wanted*: a request change. The owner's words
  are recorded on the card and folded through `add-to-card`; the spec is re-derived for the
  conditions those criteria feed and re-stamped; the session continues to a second
  acceptance. The gap entry notes that Ready was earned on a spec that did not ground the
  outcome.
- *Wants something the request never asked for*: a new card by default, with the current
  one accepted as specified. Amended into this card only when the addition is inseparable
  from the outcome under review.

Acceptance is asked against the evidence plan, criterion by criterion, so a refusal arrives
already classified.

## 8. The decision line and the standing answers

**The decision line** (principle 5) is stated once in `references/decision-line.md` and
quoted in the readiness checker, the build brief and the coordinator. The requester decides:
what an observer of the system sees or can do; what persisted data ends up as; scope. The
developer decides: internal structure; anything a recorded decision, the profile, a design
system or an existing pattern in the code already answers; anything the spec delegates. When
several sub-issues share a gap, the checker asks for the rule, not the case.

**The standing answers** are profile entries: the questions a project has answered once that
would otherwise be asked every run. Examples from the first adopter: where post-release checks
run; whether a data change is rehearsed and how; what a push carries; how finished branches
are removed; which models run the project's own pipeline agents. The plugin ships no answers;
it ships the rule that a question answered twice becomes a profile entry, and the `curate`
skill proposes them from the gap records.

## 9. Plugin layout

```
DevFactory/
  .claude-plugin/marketplace.json
  devfactory/
    plugin.json
    skills/
      configure-project/      the profile: board, specs path, test gate, environments, concerns, conventions
      create-card/            from card-standard, plus stable criterion IDs and the two core sections
      add-to-card/            from card-standard, plus the spec re-derivation trigger
      re-evaluate-card/       from card-standard, plus the trigger
      grill/                  draft the spec from the card, code, decisions and data; run the checker; ask; stamp
      check-ready/            the readiness check alone, for a card or every sub-issue of a parent; reports, asks, folds
      coordinate/             a parent issue: settle, start one session per sub-issue, relay, merge, judge, release
      build/                  one card in one session: read spec, decide delegated calls, build, review, report
      accept/                 walk the owner through acceptance against the evidence plan; classify a refusal
      release/                merge, push, release and close as the profile says; delete specs; curate gaps
      curate/                 read gap records across specs; propose checker tuning and profile entries
    agents/
      README.md               why the card reviewer stays a reference, and that no agent names a model
      readiness-checker.md    applies the Definition of Ready, fixed inputs, fixed report
      change-reviewer.md      a sub-issue's result against its spec, given what not how
      done-judge.md           applies the Definition of Done to a parent branch
    references/
      card-standard.md, card-template.md, card-process.md, working-a-card.md, card-reviewer.md, modules/
      definition-of-ready.md, definition-of-done.md, decision-line.md
      spec-template.md, profile-template.md
      bindings/github-projects.md, bindings/azure-devops.md
      runtime/claude-desktop.md     the session mechanics the coordinator uses; the only runtime-bound file
    hooks/
      (optional) a PreToolUse hook that refuses raw tracker writes outside the card skills
  README.md
  DESIGN.md
```

**Hooks.** Agent hooks cannot judge readiness. Two are worth having, both optional and
profile-enabled: one that refuses a raw tracker write (`gh issue edit`, `gh issue comment`,
their Azure DevOps equivalents) from a session not running a card skill, enforcing principle
"every change goes through the skills"; and one that, at session start in a project with a
profile, checks the stamp of any spec the prompt names and says if it is stale. Everything
else is a skill step.

**Agents** carry their whole definition inline, name no model, and are started by the skills
with the model the card suggests or the profile defaults.

**The runtime seam.** `coordinate` says "start a session for each sub-issue, briefed to wait;
message it to begin; read its report; stop it". `references/runtime/claude-desktop.md` says
how, including the desktop app's constraints (sessions start only on the owner's turn; a
waiting session replies and ends its turn; messaging works from any turn). A Codex adapter is
a second file in that folder and a profile entry choosing it.

## 10. What is carried over, changed and dropped

| From | Piece | Fate |
|---|---|---|
| card-standard | Card standard, modules, template, process, working-a-card, card reviewer | Carried; criteria gain stable IDs; two core sections added |
| card-standard | configure-board | Becomes `configure-project`; profile folder renamed `.devfactory/` |
| card-standard | create-card, add-to-card, re-evaluate-card | Carried; gain the spec trigger; fold acceptance stays for card changes outside a run, dropped inside a run |
| card-standard | suggest-work-type, work-type starter module | Dropped from core; the starter module stays available as a team module example |
| card-standard | Bindings (GitHub Projects, Azure DevOps) | Carried |
| Grillwork | Definition of Ready, Definition of Done | Carried, rewritten as sections 5 and 6 |
| Grillwork | Spec template, gap markers, amendments table, findings and curator | Carried in reduced form: spec template, gaps.md, `curate` |
| Grillwork | Tag traceability, video evidence, rubric instantiation, evidence publisher, Python engine, hook contract | Dropped |
| BottleNote | board-conventions: model and effort, work order, sub-issue markers, parallel-by-default | Carried into the core card sections and `coordinate` |
| BottleNote | board-conventions: content-card scope, image bar, intake criteria, title rule | Stay in BottleNote as team modules or project rules |
| BottleNote | check-parent-issue-readiness | Replaced by `check-ready` and the readiness checker agent |
| BottleNote | coordinate-parent-issue | Replaced by `coordinate`; its desktop mechanics move to the runtime file; its branch and merge conventions move to the profile |
| BottleNote | CLAUDE.md "Card state follows the work" | Becomes the profile's stage-to-column map |
| BottleNote | design-review | Stays in BottleNote; `grill` names it as the project's way of getting a wireframe approved |

## 11. What BottleNote keeps

The profile at `.devfactory/profile.md` (board, specs path, `dotnet test` gate, environments
Demo and production with what each can show, the extra concern "production data migration
readiness", the branch and release conventions from `AGENTS.md`, the standing answers), its
content-card rules as a team module, `design-review`, and every skill about its own
operations. `AGENTS.md` and `CLAUDE.md` lose their card process text and gain one line: cards
and parent issues are worked with the DevFactory plugin and this project's profile.

## 12. Decisions for the owner before building

1. **Fold acceptance outside a run.** Keep the card process's "every update ends with the
   user accepting the rewrite" for changes made while a card is not in development, or drop
   it everywhere. The design keeps it outside runs and drops it inside.
2. **Wireframe fidelity.** Grillwork rejects a mock-up that pins aesthetics. BottleNote's
   design reviews iterate polished mock-ups. The design lets the profile choose; the default
   is the wireframe.
3. **Request changes during development.** The design accepts them as amendments (7.2).
   The alternative is to freeze a card at development start and route every request change
   to a new card.
4. **Spec deletion at release.** The design deletes the spec folder; the alternative is an
   archive path.
5. **Hooks.** Ship the two optional hooks in the first version, or defer them. Deferred: the
   first version ships none, and the hooks folder stays empty until the owner decides.

## 13. Build order

Each step lands as its own commit in this repository and is reviewed against this document.

1. Repository scaffold: marketplace and plugin manifests, README, this design.
2. References: card standard carried over with stable IDs and the two core sections;
   decision line; the two definitions; spec and profile templates; bindings.
3. Agents: card reviewer, readiness checker, change reviewer, Done judge.
4. Card skills: `configure-project`, `create-card`, `add-to-card`, `re-evaluate-card`.
5. Spec skills: `grill`, `check-ready`.
6. Run skills: `build`, `coordinate` with the Claude desktop runtime file, `accept`,
   `release`, `curate`.
7. Hooks, when the owner chooses them (deferred, see 12.5).
8. First adopter: BottleNote's profile, removal of the replaced skills and rules, and one
   parent issue run end to end as the acceptance test of the plugin.
