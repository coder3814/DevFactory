---
name: configure-project
description: Create or edit the project profile that configures DevFactory for one project — the board (where it lives and how to reach it, which field each part of a card is written to, any additional fields with the team module that works each one, the columns in which additions are folded, and the column each lifecycle stage maps to), where specs and recorded decisions live, the test gate, the environments checkpoints can be captured in, how each population of existing data is read without writing, concern extensions, owner-step types, wireframe fidelity and the design-review procedure, branches and merging with the sub-issue branch pattern and the release procedure, the sessions runtime and default model and effort, and the standing answers. Use when the user wants to set up, configure or change DevFactory for a project, add or change a team field and its module, migrate an old card-standard board profile, or when another DevFactory skill finds no profile.
---

# Configure a project

Paths below are relative to this skill's directory.

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

This skill reads the tracker and the repository, and writes only the profile and
its team modules, under `.devfactory/` at the project's root. It never writes to
the tracker. Ask the owner one question at a time, and wherever the board or the
repository suggests an answer, propose it rather than asking from blank.

1. **Start from what exists.** If the project already has `.devfactory/profile.md`,
   read it and its team modules; change only what the owner asks for, and go
   straight to the steps that cover it. Where it lacks a section the template
   has, offer to fill that section through its step. If the project has instead
   an old `.card-standard/<board>.md`, read it and its `.card-standard/modules/`
   as the starting point for the board part (tracker, where each part is
   written, additional fields, folding), and offer to migrate it: its entries
   and modules carried into `.devfactory/`, and `.card-standard/` removed once
   the new profile is written, if the owner agrees. Otherwise, take any of the
   binding's tracker entries, such as organization, project, area path or
   repository, and the access method that the project's contributor or agent
   instructions state, and ask for whatever is missing.
2. **Read the board.** List the project's teams and ask which team the profile
   is for, then that team's boards and which one. Read the board's columns and
   its column field, and the fields of the work item type its cards are created
   as. Ask which work item type that is when the board shows more than one.
   On GitHub Projects, list the owner's projects and ask which one, then its
   board views and which one; read the view's column field and options and the
   project's fields, and ask which repository and issue type new cards go to
   and how the team marks an epic. Ask how the board marks a parent issue and
   its sub-issues when the binding leaves a choice.
3. **Place the parts.** Start from the defaults: the title in the title field,
   every other part in the description. For each field on the work item type
   that could hold a part, such as an acceptance criteria field or a custom
   rich-text field, ask whether the team wants that part moved there. On
   GitHub Projects no field can hold a part, so keep the defaults. Read a few
   of the board's recent cards and tell the owner where they keep each part
   today: a card whose parts sit elsewhere is still read, and its parts move to
   the profile's fields the next time the card is rewritten.
4. **Add fields.** List the work item type's fields, the required fields with
   no default first, and ask which ones the team wants its cards to carry. On
   GitHub Projects, list the fields the binding says a card can carry. For
   each one the team wants, interview them on what it holds and, for a field
   with set values, how they choose between the values. Draft its team module
   from their answers, in their words. A team may want none. Where a field the
   team wants matches the example module, a work type field and
   `../../references/examples/work-type-module.md`, offer it as the draft
   instead, without its opening note. Check its values against the field's
   allowed values, and change it as the team asks.
5. **Choose the fold columns.** Show the board's columns and ask in which ones
   additions should be folded into the card, letting the owner choose any
   number of them, all or none. If the project will develop cards through
   `coordinate` and `build`, point out what the template's Folding entry says
   about its Development column.
6. **Map the stages.** Show the seven lifecycle stages beside the board's
   columns, propose the column each stage maps to, and ask the owner to confirm
   or change the mapping. Every stage gets a column; several may share one
   where the board has fewer columns.
7. **Place specs and recorded decisions.** Propose `specs/` as the specs path,
   or another path outside any documentation system the project runs where
   `specs/` would sit inside one, and ask. Look for where the project already
   keeps its decisions, such as a decisions or architecture-decision folder,
   propose that path, and ask; if it keeps none, ask where they are.
8. **Find the test gate.** Read the project's build files, such as a package
   manifest's test script, a make target, a solution or project file, or the
   test step of a continuous-integration workflow, and propose the command that
   runs the whole existing test suite. Ask the owner to confirm or correct it.
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
    fidelity. Then ask how a wireframe is shown to the requester and approved,
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
15. **Choose the sessions runtime.** List the files in `../../references/runtime/`
    and offer them as the runtime the coordinator follows. Then ask for the
    default model and effort level (Low, Medium or High) used when a card
    suggests none.
16. **Record standing answers.** Explain what a standing answer is and the rule
    that a question answered twice in gap records becomes one, as the template
    says. Start the section empty unless the owner has answers to record now;
    record each as the question, its answer and where the answer came from.
17. **Accept and write.** Show the profile and every team module in full and get
    the owner's acceptance or changes. Once accepted, write them to
    `.devfactory/profile.md` and `.devfactory/modules/`, carry out any migration
    the owner agreed to in step 1, and tell the owner to commit them so the
    whole team shares one profile.
