---
name: configure-project
description: Create or edit the project profile that configures DevFactory for one project — the board (where it lives and how to reach it, which field each part of a card is written to, any additional fields with the team module that works each one), where specs and recorded decisions live, the test gate, the environments checkpoints can be captured in, how each population of existing data is read without writing, concern extensions, owner-step types, wireframe fidelity and the design-review procedure, branches and merging with the sub-issue branch pattern and the release procedure, the default model and effort, which of the plugin's hooks are on, the read commands pre-approved in the project's Claude Code settings, and the standing answers. Use when the user wants to set up, configure or change DevFactory for a project, add or change a team field and its module, change which hooks run or which reads are pre-approved, migrate an old card-standard board profile, or when another DevFactory skill finds no profile.
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
(worktree) root, wherever the shell's working directory is.

Read these first, in full:

- `../../references/profile-template.md` — what you are writing, section by
  section.
- `../../references/card-standard.md` — the parts of a card and the defaults
  for where each is written.
- The binding for the board's tracker: `../../references/bindings/azure-devops.md`
  for Azure DevOps, `../../references/bindings/github-projects.md` for GitHub
  Projects. Ask which tracker the board is in if the project does not say.
- `../../references/definition-of-ready.md`, condition 4.1 — the core list of
  fixed concerns the project may extend.
- `../../references/spec-template.md` — what a spec folder holds, so the paths
  and entries you propose fit it.

This skill reads the tracker and the repository. It writes only the profile and
its team modules, under `.devfactory/` at the project's root, the allow entries
in the project's `.claude/settings.json`, and one line of `.gitignore`. It never
writes to the tracker. Ask the owner one question at a time with the
AskUserQuestion tool, and wherever the board or the repository suggests an
answer, propose it as the first option rather than asking from blank.

1. **Begin.** Run `devfactory begin configure-project`. When whoever started you handed
   over answers the owner has already given (a brief that names the board, the test gate,
   the environments and so on), take each as that step's answer, show it in the summary at
   step 19, and ask only the questions no answer covers.
2. **Start from what exists.** If the project already has `.devfactory/profile.md`,
   read it and its team modules; change only what the owner asks for, and go
   straight to the steps that cover it. Where it lacks a section the template
   has, offer to fill that section through its step; a profile with no Hooks
   section runs every hook, as the template's default says. A Folding or Stages
   section the template no longer has is read by nothing: offer to remove it,
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
   and how the team marks an epic. Ask how the board marks a parent issue and
   its sub-issues when the binding leaves a choice.
4. **Place the parts.** Start from the defaults: the title in the title field,
   every other part in the description. For each field on the work item type
   that could hold a part, such as an acceptance criteria field or a custom
   rich-text field, ask whether the team wants that part moved there. On
   GitHub Projects no field can hold a part, so keep the defaults. Read a few
   of the board's recent cards and tell the owner where they keep each part
   today: a card whose parts sit elsewhere is still read, and its parts move to
   the profile's fields the next time the card is rewritten.
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
   writing it in step 19. Say that the Permissions entry for the plugin's script
   also lets `devfactory event` run these hooks without a prompt, so each hook
   writes to the tracker unattended.
7. **Place specs and recorded decisions.** Propose `specs/` as the specs path,
   or another path outside any documentation system the project runs where
   `specs/` would sit inside one, and ask. Look for where the project already
   keeps its decisions, such as a decisions or architecture-decision folder,
   propose that path, and ask; if it keeps none, ask where they are.
8. **Find the test gate.** Read the project's build files, such as a package
   manifest's test script, a make target, a solution or project file, or the
   test step of a continuous-integration workflow, and propose the command that
   runs the whole existing test suite. Ask the owner to confirm or correct it.
   Then ask whether the project has, or wants, a recorded gate: a command of its own
   that records each pass against the git tree it ran on and prints that record instead
   of rerunning when the same tree is tested again, so the gate is not rerun on code a
   recorded run already passed. Explain the contract the "Recorded gate" entry in
   `../../references/profile-template.md` gives (written only by the command after its
   own pass, never for a dirty tree, keyed to `HEAD^{tree}` and the tests passed, stored
   where every worktree and a reviewer's checkout read it, with a forced rerun), and that
   the project writes and owns the command; the plugin ships none. When the owner names
   one, record it with its Forced rerun and how it takes a selection of tests. None is a
   valid answer: the gate points then run the Command, as before.
9. **List the environments.** Propose environments from what the repository
    reveals, such as a local run configuration, a container compose file or a
    deploy workflow and the targets it deploys to. Ask which environments exist,
    and for each, what a checkpoint there can show, what it cannot, and how it
    is reached, in the project's words, one environment at a time.
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
    mock-up a development card's spec references. Then ask how a wireframe is shown to the requester and approved,
    proposing any procedure or skill the contributor rules name, and record it
    as the Design review line.
14. **Set branches and merging.** Read the project's contributor rules, if any,
    such as a contributing guide or agent instructions, and propose the
    integration branch, the worktree layout, how a parent issue's branch is
    named, how a sub-issue's branch is named, who merges what into which branch
    and when, and the release procedure: the project's own steps, or the skill
    or document it names, for pushing, releasing and closing finished work.
    Where the rules are silent, read the repository's branches and its deploy
    workflows and ask.
15. **Set the sessions default.** Ask for the default model and effort level
    (Low, Medium or High) a build session uses when a card suggests none. Say
    that `coordinate` runs a parent issue as one session per sub-issue through
    the Claude desktop app's session tools, so a project that runs parent
    issues needs the Claude desktop app; a standalone card built with `build`
    does not.
16. **Choose the hooks.** Show the four hooks as the template's "Hooks and
    permissions" describes them — the tracker guard, the git guard, the stamp
    notice and the session context — say that all four are on by default, and
    ask whether the owner wants any off. Say that the tracker guard covers
    `gh api graphql` mutations and `gh api` calls with `-f`, `-F`, `--input`,
    `--method` or a non-GET `-X`, besides the issue, project and board
    commands. Record one `on` or `off` line for each in the Hooks section. Then
    ask for the Hooks section's `Marker lifetime`, proposing the default of 12
    hours: a marker older than that no longer counts as a running skill, and
    `begin` refreshes it. Record it as the `Marker lifetime` line, `12h` by
    default. For troubleshooting, tell the owner: a guard that lets a write
    through while no skill is running points to a marker an interrupted skill
    left behind, which `devfactory markers` lists with its age and
    `devfactory markers --clear-stale` removes once past its lifetime; a guard
    that refuses a running skill's write points to an expired marker, which
    that skill's `begin` refreshes.
17. **Choose the permissions.** Propose the allowlist entries for the
    Permissions section, read commands only, in the `Bash(<command> *)`
    spelling: the plugin's script, `Bash(python *devfactory.py*)`; the binding's
    reads, `Bash(gh issue view *)`, `Bash(gh project item-list *)` and
    `Bash(gh api -X GET *)` for GitHub Projects, or
    `Bash(az boards work-item show *)` for Azure DevOps; and the repository
    reads the skills and agents make, `Bash(git log *)`, `Bash(git show *)`,
    `Bash(git diff *)`, `Bash(git status *)`, `Bash(git rev-parse *)` and
    `Bash(git merge-base *)`. Read the project's `.claude/settings.json`, if
    there is one, and say which entries it already allows. Ask the owner to
    accept, drop or add entries. Refuse any entry that writes, such as a
    tracker edit, a push or a merge: writes are never pre-approved.
18. **Record standing answers.** Explain what a standing answer is and the rule
    that a question answered twice in gap records becomes one, as the template
    says. Start the section empty unless the owner has answers to record now;
    record each as the question, its answer and where the answer came from.
19. **Accept and write.** Show the profile and every team module in full, the
    allow entries to be added to `.claude/settings.json` and the `.gitignore`
    line, and get the owner's acceptance or changes. Once accepted:
    - write the profile and modules to `.devfactory/profile.md` and
      `.devfactory/modules/`, and each event hook the owner asked for to
      `.devfactory/hooks/`, with the Write tool;
    - merge the Permissions entries into the project's `.claude/settings.json`
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
    runs without them: the next session in the project is the first with the guards on.
20. **End.** Run `devfactory end configure-project`.
