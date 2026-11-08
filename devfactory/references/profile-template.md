# Project profile

How a project configures DevFactory: its board, where its specs live, how its work is proven,
where it can be shown, and the answers it has already settled. The `configure-project` skill
writes the profile by reading the board and the repository and asking the project's owner;
every other skill reads it first, before touching a card, a spec or a branch. The plugin
holds the process; everything that varies by project is here and nowhere else.

## Where it lives

One folder per project, `.devfactory/` at the repository root:

- `profile.md`: the profile, laid out below.
- `modules/`: the team modules the profile names.
- `gaps.md`: the gap ledger, the gap records of released cards, which `release` appends to.
- `.active/`: the marker folder. A card or spec skill writes a marker here when it begins
  and removes it when it ends, and the hooks read it to tell whether one is running.
  `configure-project` adds `.devfactory/.active/` to `.gitignore`, so markers are never
  committed.

Recorded decisions are not here. They stay where the project keeps them, and the profile says
where, so the readiness checker can read them.

## What it holds

```markdown
# Project profile: <project name>

## Tracker
- Binding: <binding name, for example azure-devops>
- <the entries the binding names, one per line>

## Where each part is written
| Part | Field |
|---|---|
| Title | <title field> |
| Summary | <description field> |
| The issue or request | <description field> |
| What needs to be achieved | <description field> |
| Scope | <description field> |
| Supporting information | <description field> |
| Open questions | <description field> |
| Acceptance criteria | <description field> |
| Work order | <description field> |
| Suggested model and effort | <description field> |

## Additional fields
| Field or fields | Team module |
|---|---|
| <field>, … | `modules/<module>.md` |
| none | `modules/<rules module>.md` |


## Specs
- Path: <specs/, or another path>

## Recorded decisions
- Path: <where the project keeps its decisions>

## Test gate
- Command: <the command that proves existing behaviour, or the procedure or script that
  selects and runs it, in the project's words>

## Environments
### <name>
- Can show: <what a checkpoint here can demonstrate>
- Cannot show: <what it cannot>
- Reached by: <how a checkpoint here is reached, in the project's words>

## Data access
- <population>: <how it is read, read-only, in the project's words; who may read it>

## Concern extensions
- <concern>: <what a disposition of it must answer>

## Owner-step types
- <type>: <what the step is and who takes it>

## Wireframe fidelity
- <wireframe; or finished mock-up; or design card: a card of its own whose approved mock-up this
  card's spec references>
- Design review: <how a wireframe is shown to the requester and approved>

## Branches and merging
- Integration branch: <branch>
- Worktree layout: <where a session's worktree goes and how it is named>
- Parent branch: <how a parent issue's branch is named>
- Sub-issue branch: <how a sub-issue's branch is named>
- Merging: <who merges what into which branch, and when>
- Release: <the project's release steps, or the skill that holds them>

## Sessions
- Default model and effort: <used when a card suggests none>

## Hooks
- Tracker guard: <on / off>
- Git guard: <on / off>
- Stamp notice: <on / off>
- Session context: <on / off>
- Marker lifetime: <hours>h

## Permissions
- <an allowlist entry, for example `Bash(gh issue view *)`>

## Standing answers
- **<the question, as it was asked>** <the answer, and where it came from>
```

### The board

- **Tracker** names the binding, a file in [`bindings/`](bindings/) that says how the card
  standard maps onto that tracker, and the entries that binding asks for. The bindings are
  [`azure-devops.md`](bindings/azure-devops.md) and
  [`github-projects.md`](bindings/github-projects.md).
- **Where each part is written** lists every core module. The defaults, and the rules for
  moving a part into another field, are in [`card-standard.md`](card-standard.md).
- **Additional fields** is optional: none, or as many entries as the team wants. Each names
  the field or fields and the team module that works them. One module may cover several
  fields. A module whose field is `none` holds rules the team adds for the card as a whole,
  such as what a kind of card may and may not cover; the card reviewer applies it to the
  card's parts the way it applies a core module, and it recommends no field value.
- **No board columns.** The profile names no column, and no skill reads one or moves a
  card between them: every skill works a card wherever it sits. A project that wants cards
  moved gives the events in [`events.md`](events.md) hooks in `.devfactory/hooks/`, beside
  the profile.

### The work

- **Specs** is where each card's spec folder goes, as `<path><card>/`; the default is
  `specs/`. The folder's layout is in [`spec-template.md`](spec-template.md).
- **Recorded decisions** is where the readiness checker reads the decisions that already
  answer a question.
- **Test gate** is the command, or the named procedure or script, that proves existing
  behaviour; a gate with a precondition, such as a container runtime, names it here. Done condition 1.1 runs it at
  the revision under evaluation.
- **Environments** lists every place a checkpoint can be captured. A spec's evidence row
  names one by its heading, and Ready condition 7.3 checks that its "can show" covers what
  the row promises. "Reached by" is in the project's words: a command, a deploy, a sign-in.
- **Data access** names each population of existing data a card's rules might act on and
  how it is read without writing, so the readiness checker can run the rules against it
  (Ready condition 5). A population with no entry makes condition 5 unchecked, never passed.
- **Concern extensions** adds to the core list of fixed concerns in
  [`definition-of-ready.md`](definition-of-ready.md), condition 4.1. Every spec in the
  project then disposes of each one. Optional.
- **Owner-step types** names the kinds of step only the requester can take in this project,
  so a spec can schedule one by its type.
- **Wireframe fidelity** is what the approved design artifact fixes. The default is a wireframe:
  structure, fields, states and interaction, not aesthetics. A project may instead require a
  finished mock-up, or a **design card**: the design is a card of its own, grilled and accepted
  first, and the development card's spec names that card's approved mock-up as its interface
  artifact, so Ready condition 6.2 is met by the reference rather than by a file in the spec
  folder. Its **Design review** line is
  how a wireframe is shown to the requester and approved, in the project's steps or the
  skill that holds them; `grill` follows it when the interface determination is
  non-trivial.
- **Branches and merging** is how work moves into the integration branch and out to
  release: where worktrees go, how a parent branch and a sub-issue branch are named, who
  merges and when, and the release procedure, in the project's steps or the skill that
  holds them. `coordinate`, `build` and `release` follow it. The change reviewer's base
  revision is the merge-base of the card's branch with the parent branch, or with the
  integration branch for a standalone card, at the time of the review.
- **Sessions** is the model and effort used when a card suggests none. The coordinator
  runs a parent issue as one session per sub-issue through the Claude desktop app's session
  tools, so a project that runs parent issues needs the Claude desktop app, and
  `coordinate` says so.

### Hooks and permissions

- **Hooks** switches each of the plugin's four hooks on or off for this project; all four
  are on by default, and a hook whose line says off does nothing. The **tracker guard**
  refuses a write to the tracker while no card skill is running, so every card change goes
  through the card skills. The **git guard** refuses a push, or a merge or rebase into the
  integration branch or a parent branch, while neither `release` nor `coordinate` is
  running. The **stamp notice** says, when a prompt names a card that has a spec, whether
  the spec is still current or the card has changed since it earned Ready; it never blocks.
  The **session context** prints, when a session starts, where the profile is, the event
  hooks the project has, which skill does what, and whether a card skill is running. The guards
  read the markers in `.devfactory/.active/`.
- **Permissions** lists the allowlist entries `configure-project` writes to the project's
  `.claude/settings.json`, so the skills' reads run without a prompt each time, such as
  reading a card, listing the board, reading the git log and running the plugin's script.
  Only read commands belong here; a write to the tracker or to a branch is never
  pre-approved.

### Standing answers

A standing answer is a question the project has settled once that would otherwise be asked
every run, such as where post-release checks run or what a push carries. Each entry is the
question as it was asked and its answer, with where the answer came from (a gap entry, a
decision, the owner).

The plugin ships no answers; it ships the rule: **a question answered twice in gap records
becomes an entry.** `curate` proposes entries from the gap records, and the owner accepts
them. A spec that relies on an entry names it under Project bindings used.

## Team modules

A team module is a Markdown file the team owns and may tune at will. It has the same sections
as a core module:

- **Holds:** what the field carries; for a module covering several fields, what each one
  carries.
- **Rules:** what it must and must not be.
- **Examples:** where they help.
- **Related data:** optional — anything outside the card the module decides from, such as
  the card's epic and that epic's fields.
- **Choosing a value:** for a field with set values only — the allowed values and how to
  choose between them, in the team's words.

The agent working a card applies a team module to the card as a whole, with the related data
the module names, and recommends a value, with a one-line reason, for the user to accept. A
team module never writes to the tracker itself.

The plugin ships one example module, [`work-type-module.md`](examples/work-type-module.md), a
Work Type field. `configure-project` offers it as the draft when a team wants a matching
field, and copies it into the project's `.devfactory/modules/`, where it becomes the team's
to change. Only the team's copy is ever applied.
