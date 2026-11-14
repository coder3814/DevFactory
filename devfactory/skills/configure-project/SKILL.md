---
name: configure-project
description: Create or edit the project profile that configures DevFactory for one project — the board (where it lives and how to reach it, which field each part of a card is written to, any additional fields with the team module that works each one), where specs and recorded decisions live, the test gate, the environments checkpoints can be captured in, how each population of existing data is read without writing, concern extensions, owner-step types, wireframe fidelity and the design-review procedure, branches and merging with the sub-issue and card branch patterns and the release procedure, the default model and effort, which of the plugin's hooks are off, the read commands pre-approved in the project's Claude Code settings, and the standing answers, recording only departures from the defaults and pointing to what the project already records. Use when the user wants to set up, configure or change DevFactory for a project, add or change a team field and its module, change which hooks run or which reads are pre-approved, migrate an old card-standard board profile, or when another DevFactory skill finds no profile.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(python *devfactory.py*)
  - Bash(gh issue view *)
  - Bash(gh project list *)
  - Bash(gh project field-list *)
  - Bash(gh project item-list *)
  - Bash(gh api -X GET *)
  - Bash(az boards work-item show *)
  - Bash(git log *)
---

# Configure a project

Paths below are relative to this skill's directory. `devfactory` below means running the
plugin's script with `python`: the script is `${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`;
if that variable is empty in your shell, it is `../../scripts/devfactory.py` relative to
this skill's folder.

**Markers.** Run `devfactory begin configure-project` as your first action and
`devfactory end configure-project` as your last. Whenever you end your turn to wait for
the owner's answer or acceptance, or stop for any reason, run
`devfactory end configure-project` first, and `devfactory begin configure-project` again
when you resume. A marker expires after the profile's Marker lifetime (12 hours by
default), and `begin` refreshes it. Markers and the profile are found at the repository
(worktree) root, wherever the shell's working directory is. When `begin` prints
`plugin-changed`, load this skill again before you continue.

**Read these first, in full.** A file you have already read in full in this session, under
the plugin version `begin` printed, need not be read again.

- `../../references/profile-template.md` — what you are writing, section by
  section.
- `../../references/test-gate.md` — when the test gate runs and what a Recorded
  gate must guarantee, so the Test gate entries you propose fit it.
- `../../references/card-standard.md` — the parts of a card and the defaults
  for where each is written.
- The binding for the board's tracker: `../../references/bindings/azure-devops.md`
  for Azure DevOps, `../../references/bindings/github-projects.md` for GitHub
  Projects. Ask which tracker the board is in if the project does not say.
- `../../references/spec-template.md` — what a spec folder holds, so the paths
  and entries you propose fit it.

From `../../references/definition-of-ready.md` read only the section "4. The fixed
concerns are disposed": the core list of fixed concerns the project may extend.

This skill reads the tracker and the repository. It writes only the profile and
its team modules, under `.devfactory/` at the project's root, the allow entries
in the project's `.claude/settings.json`, and one line of `.gitignore`. It never
writes to the tracker. Ask the owner one question at a time with the
AskUserQuestion tool, and wherever the board or the repository suggests an
answer, propose it as the first option rather than asking from blank.

The profile records only departures from the defaults, as the template says:
an answer that is the default writes no line, and a section left at its
default is left out. Where the project already records an answer, in its
instructions (`CLAUDE.md`), its recorded decisions or its skills, write a
pointer to it, such as "as CLAUDE.md's push sections say", never a copy,
except in a field the plugin's script or hooks read as a value (the
integration branch, the parent-branch pattern, the specs path and Not code
paths, the Hooks lines, the Marker lifetime), which holds the value itself.

1. **Begin.** Run `devfactory begin configure-project`. When whoever started you handed
   over answers the owner has already given (a brief that names the board, the test gate,
   the environments and so on), take each as that step's answer, show it in the summary at
   step 19, and ask only the questions no answer covers.
2. **Start from what exists.** If the project already has `.devfactory/profile.md`,
   read it and its team modules; change only what the owner asks for, and go
   straight to the steps that cover it. A section it lacks whose absence means
   the default (where each part is written, the specs path, the hooks, the
   Marker lifetime) is not offered: its absence is the answer. Offer to fill
   only a section that has no default, such as the test gate or the
   environments, through its step. Offer to remove a line that only restates a
   default, a Permissions section, which `.claude/settings.json` records,
   and an entry that copies what the project's instructions, decisions or
   skills already say, which becomes a pointer. A Folding or Stages
   section, which the template does not have, is read by nothing: offer to remove it,
   and, where the owner wants their old stage moves kept, to write them as event
   hooks in step 6. If the project has
   instead an old `.card-standard/<board>.md`, read it and its
   `.card-standard/modules/` as the starting point for the board part (tracker,
   where each part is written, additional fields), and offer to
   migrate it: its entries and modules carried into `.devfactory/`, and
   `.card-standard/` removed once the new profile is written, if the owner
   agrees. Otherwise, take any of the binding's tracker entries, such as
   organization, project, area path or repository, and the access method that
   the project's contributor or agent instructions state, and ask for whatever
   is missing.
3. **Read the board.** List the project's teams and ask which team the profile
   is for, then that team's boards and which one. Read the board's columns and
   its column field, and the fields of the work item type its cards are created
   as. Ask which work item type that is when the board shows more than one.
   On GitHub Projects, list the owner's projects and ask which one, then its
   board views and which one; read the view's column field and options and the
   project's fields, and ask which repository and issue type new cards go to
   and how the team marks an epic. Record nothing about how a parent issue and
   its sub-issues are linked: that is the binding's, in its Sub-issues section.
4. **Place the parts.** Start from the defaults: the title in the title field,
   every other part in the description. For each field on the work item type
   that could hold a part, such as an acceptance criteria field or a custom
   rich-text field, ask whether the team wants that part moved there. On
   GitHub Projects no field can hold a part, so keep the defaults. Read a few
   of the board's recent cards and tell the owner where they keep each part
   today: a card whose parts sit elsewhere is still read, and its parts move to
   the profile's fields the next time the card is rewritten. Record only the
   parts moved off the default; with none moved, leave the section out.
5. **Add fields.** List the work item type's fields, the required fields with
   no default first, and ask which ones the team wants its cards to carry. On
   GitHub Projects, list the fields the binding says a card can carry. For
   each one the team wants, interview them on what it holds and, for a field
   with set values, how they choose between the values. Draft its team module
   from their answers, in their words. A team may want none. Where a field the
   team wants matches the example module, a work type field and
   `../../references/examples/work-type-module.md`, offer it as the draft
   instead, without its opening note. Check its values against the field's
   allowed values, and change it as the team asks.
6. **Explain the events.** Say that the plugin moves no card on the board: it
   fires the events in `../../references/events.md` at each point where the work
   changes hands, and a project that wants cards moved, or anything else done,
   adds a hook for that event in `.devfactory/hooks/`. Ask whether the owner
   wants any hook now; write each one they ask for, as `events.md` says, with
   the tracker's own CLI and the column names they give, and show it before
   writing it in step 19. Say that the allowlist entry for the plugin's script
   also lets `devfactory event` run these hooks without a prompt, so each hook
   writes to the tracker unattended.
7. **Place specs and recorded decisions.** Propose `specs/` as the specs path,
   or another path outside any documentation system the project runs where
   `specs/` would sit inside one, and ask. Write a Path line only for a path
   other than `specs/`. Look for where the project already
   keeps its decisions, such as a decisions or architecture-decision folder,
   propose that path, and ask; if it keeps none, ask where they are. When the
   project's own rules have work commit notes beside the code that are not code,
   such as change notes for a documentation system, propose their folder as the
   Specs entry's Not code paths, so a note written after evidence was captured
   does not make that evidence stale, and ask.
8. **Find the test gate.** Read the project's build files, such as a package
   manifest's test script, a make target, a solution or project file, or the
   test step of a continuous-integration workflow, and propose the command that
   runs the whole existing test suite. Ask the owner to confirm or correct it.
   Then ask whether the project has a command that runs only the tests a change
   touches, which a build runs while building, and record it as Affected tests;
   none is a valid answer. Then ask whether the project has, or wants, a recorded
   gate: a command of its own that records each pass against the git tree it ran on
   and prints that record instead of rerunning when the same tree is tested again,
   so the gate after a rebase is not rerun on code the review's run already passed.
   Explain the contract
   `../../references/test-gate.md` gives under "Recorded gates" (written only by the
   command after its own pass, never for a dirty tree, keyed to `HEAD^{tree}` and the
   tests passed, stored where every worktree and a reviewer's checkout read it, with a
   forced rerun, which is the reviewer's fresh run), and that the project writes and owns
   the command; the plugin ships none. When the owner names one, record it with its
   Forced rerun and how it takes a selection of tests. None is a valid answer: every
   point that runs the gate then runs the Command.
9. **List the environments.** Propose environments from what the repository
    reveals, such as a local run configuration, a container compose file or a
    deploy workflow and the targets it deploys to. Ask which environments exist,
    and for each, what a checkpoint there can show, what it cannot, and how it
    is reached, in the project's words, one environment at a time. Say that the
    Repository checkpoint is built in, for command output from a clean checkout, git
    history and the card's comments, so no environment's "can show" lists those and none
    is named Repository.
10. **Name the data access.** Propose the populations of existing data a card's
    rules might act on from what the repository reveals, such as a database
    schema, migrations, data files or seed data, and ask which exist. For each,
    one population at a time, ask how it is read without writing and who may
    read it, in the project's words. Say that a population with no entry leaves
    Ready condition 5 unchecked for any card whose rules act on it. None is a
    valid answer for a project whose cards never act on existing data.
11. **Extend the concerns.** Show the core fixed concerns and ask whether the
    project adds any, proposing any that its recorded decisions or contributor
    rules make recurring. For each, record what its disposition must answer.
    None is a valid answer.
12. **Name the owner-step types.** Ask what kinds of step only the requester
    can take in this project, proposing any the contributor rules or recorded
    decisions name, such as approving a mock-up or running something in a
    protected environment. For each, record what it is and who takes it.
13. **Set the wireframe fidelity and design review.** Say that the default is a
    wireframe, which fixes structure, fields, states and interaction but not
    aesthetics, and ask whether the project's design review works at another
    fidelity: a finished mock-up, or a design card of its own whose approved
    mock-up a development card's spec references. Record only what the artifact
    fixes, never when one is required, which Ready conditions 6.1 and 6.2 decide.
    With a design card, ask where approved design artifacts are kept, outside
    the specs path, and record it as the Design artifacts line. Then ask how a
    wireframe is shown to the requester and approved, proposing any procedure or
    skill the contributor rules name, and record it as the Design review line.
14. **Set branches and merging.** Read the project's contributor rules, if any,
    such as a contributing guide or agent instructions, and propose the
    integration branch, the worktree layout, how a parent issue's branch is
    named, how a sub-issue's branch is named, how a standalone card's branch and
    worktree are named (the Card branch entry), who merges what into which branch
    and when, and the release procedure: the project's own steps, or the skill
    or document it names, for pushing, releasing and closing finished work.
    Where the rules are silent, read the repository's branches and its deploy
    workflows and ask. Say that the coordinator briefs each sub-issue's session
    with the branch the Sub-issue branch pattern names, and that a session the
    app started on another branch keeps that branch and reports its name, and
    that a standalone card is built on the branch and worktree the Card branch
    entry names, which `release` later merges.
15. **Set the sessions default.** Ask for the default model and effort level
    (Low, Medium or High) a build session uses when a card suggests none. Say
    that `coordinate` runs a parent issue as one session per sub-issue through
    the Claude desktop app's session tools, so a project that runs parent
    issues needs the Claude desktop app; a standalone card, which `start` hands
    to `build`, does not.
16. **Choose the hooks.** Show the three hooks as the template's "Hooks and
    permissions" describes them — the tracker guard, the stamp
    notice and the session context — say that all three are on by default, and
    ask whether the owner wants any off. Say that the tracker guard judges every
    command a session gives its Bash or PowerShell tool, and that it
    refuses every `gh issue`, `gh project`, `gh label` and
    `az boards work-item` subcommand that is not a known read, every `gh api`
    call that is not a GET, and every `az rest` call that is not a GET against a
    work-item API, unless a skill that writes the tracker is running. Say that
    the session context lists every skill by its full name, such as
    `devfactory:start`. Record an `off` line only for each hook the owner turns off, and
    nothing for one left on. Then ask for the `Marker lifetime`, proposing the
    default of 12 hours: a marker older than that no longer counts as a running
    skill, and `begin` refreshes it. Record a `Marker lifetime` line only when
    the owner chooses another value. With every hook on and the default
    lifetime, leave the Hooks section out. For troubleshooting, tell the owner: a guard that lets a write
    through while no skill is running points to a marker an interrupted skill
    left behind, which `devfactory markers` lists with its age and
    `devfactory markers --clear-stale` removes once past its lifetime; a guard
    that refuses a running skill's write points to an expired marker, which
    that skill's `begin` refreshes.
17. **Choose the permissions.** Propose the allowlist entries for the
    project's `.claude/settings.json`, which is their only record (the profile
    keeps no copy), read commands only, in the `Bash(<command> *)` spelling, as
    one list that covers every read command the skills name, with the tracker
    reads of the project's tracker only:
    - `Bash(python *devfactory.py*)`, the plugin's script;
    - for GitHub Projects, `Bash(gh issue view *)`, `Bash(gh project list *)`,
      `Bash(gh project field-list *)`, `Bash(gh project item-list *)` and
      `Bash(gh api -X GET *)`;
    - for Azure DevOps, `Bash(az boards work-item show *)`;
    - `Bash(git log *)`, `Bash(git show *)`, `Bash(git diff *)`,
      `Bash(git status *)`, `Bash(git rev-parse *)`, `Bash(git merge-base *)`,
      `Bash(git cherry *)`, `Bash(git worktree list *)`,
      `Bash(git branch --list *)`, `Bash(git ls-tree *)` and
      `Bash(git hash-object *)`.

    Read the project's `.claude/settings.json`, if
    there is one, and say which entries it already allows. Ask the owner to
    accept, drop or add entries. Refuse any entry that writes, such as a
    tracker edit, a push or a merge: writes are never pre-approved.
18. **Record standing answers.** Explain what a standing answer is and the rule
    that a question answered the same way on two separate occasions becomes
    one, as the template says, and what does not belong there: a rule that
    would hold on any project or that changes how a skill or agent works, which
    belongs in the plugin; a call on the developer's side of the decision line;
    and a procedure the project's own instructions, decisions or skills already
    own, which is pointed to. Start the section empty unless the owner has
    answers to record now; record each as the question, its answer and, when it
    came from cards, one short citation of their numbers.
19. **Accept and write.** Show the profile and every team module in full, the
    allow entries to be added to `.claude/settings.json` and the `.gitignore`
    line, and get the owner's acceptance or changes. Once accepted:
    - write the profile and modules to `.devfactory/profile.md` and
      `.devfactory/modules/`, and each event hook the owner asked for to
      `.devfactory/hooks/`, with the Write tool;
    - merge the accepted allowlist entries into the project's `.claude/settings.json`
      under `permissions.allow`: read the file with the Read tool, add each
      entry it does not already hold with the Edit tool, and keep every other
      key and every existing entry, never removing one; when the file does not
      exist, create it with the Write tool holding only `permissions.allow`;
    - add the line `.devfactory/.active/` to the project's `.gitignore`, creating
      the file if there is none, unless a line already ignores that folder;
    - carry out any migration the owner agreed to in step 2;
    - run `devfactory profile` and confirm it prints the profile you wrote.
    Commit the profile, the modules, any hooks, `.claude/settings.json` and `.gitignore` as the
    project's conventions say, or tell the owner to, so the whole team shares one profile.
    Say that hooks and the session context load when a session starts, so this session
    runs without them: the next session in the project is the first with the hooks on.
20. **End.** Run `devfactory end configure-project`.
