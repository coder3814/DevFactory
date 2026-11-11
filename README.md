# DevFactory

**A Claude Code plugin that takes a request from a card on your board to an accepted,
unattended build, and stops asking you questions along the way.**

You write the request, and DevFactory grills you until it meets a Definition of Request, with
every answer in it. It then grills the request into a specification complete enough that an
agent can build from it without a single further question, proves that claim with a numbered
Definition of Ready, runs the build as one Claude session per piece of work, judges the
result against a Definition of Done, and records every miss so the next grilling asks it up
front. You are asked twice: once to approve the spec, once to accept the result.

## The problem it solves

Giving an agent a card and saying "build this" produces one of two outcomes. Either the agent
guesses at everything the card left open and you find out at the end, or it stops to ask you
every few minutes and the run is unattended in name only. A card written to a good standard
is deliberately short: it states the outcome and leaves the method to the developer. That is
right for a card and wrong for an unattended build, which needs every edge, every
disposition and every owner step settled before it starts.

In one project that moved to unattended parent-issue runs, the owner answered about 240
questions across 24 runs in eight days. A third were behaviour the card had left open. A
sixth were process questions that had been answered before and never written down. A tenth
were rules meeting real data for the first time. Almost none needed to be asked during the
run.

## What DevFactory does about it

**Keeps the card as the request.** Cards are written and maintained to a card standard:
title, summary, the issue, scope, supporting information, open questions, acceptance criteria
with stable IDs, a suggested model and effort, and for a parent issue a work order that says
which sub-issues run in parallel and which wait on what. Skills create cards, add to them and
re-evaluate them, always recording what changed and folding it into the card. Every card is
worked wherever it sits on your board; the plugin moves no card, but fires an event at each
hand-off, and when work starts, when a spec loses Ready because its card changed, and when
you refuse a result, which your own `.devfactory/hooks/` scripts can use to move it.

**Grills the card into a spec.** A spec folder sits beside your code, one per card. It holds
what the card does not: which decisions are delegated to the developer and which are the
requester's, boundaries with reasons, a disposition for every fixed concern (existing data,
security, performance, release sequencing, owner steps), the interface determination and its
approved design, the result of running the card's rules against the real data population,
an evidence plan with a checkpoint per criterion, and every owner step with its moment in the
run. A readiness checker measures the spec against nine numbered conditions. You answer each
open question once. The spec is stamped with a hash of the card, so a later change to the
card is detected mechanically, not remembered.

**Judges each thing once.** A check runs in the stage that produces what it judges: the card
reviewer when the card is written, the readiness checker when the spec is. A passing check
leaves a receipt in the card's spec folder, committed with the code, recording a fingerprint
of everything it read: the card's text, comments, fields and sub-issue order, the spec
files, the gap records, the profile, the plugin's standard and the code commit. The next
stage compares fingerprints instead of judging again, so moving from card to spec to
development re-runs a check only when something it reads has changed, and then only that
check.

**Runs the build unattended.** For a parent issue, a coordinator starts one Claude desktop
session per sub-issue, all in your opening turn, sets each going as its waits clear, relays the rare question that
survives the spec and the decision line, merges results into the parent branch one at a
time, and has a separate judge apply the Definition of Done to the combined result. For a
single card, one session builds it and a separate reviewer passes it. No agent accepts its
own work.

**Treats every question as a defect in the spec.** A question asked after Ready is a gap:
recorded with the condition that let it through, answered as a spec amendment, and kept in a
project ledger after release. The checker reads the ledger before every grilling, and a
curate skill proposes which questions should become standing answers in your project's
profile.

**Enforces its own rules.** Four hooks ship with the plugin, each switchable per project. A
tracker guard refuses a raw write to your board unless a card skill is running. A git guard
refuses a push, or a change to the integration or a parent branch, unless the skill that owns
that step is running. A stamp notice tells a session whether the card it was asked about has
changed since its spec earned Ready. A session-context hook puts the project's lifecycle, the
skills to use and the decision line in front of every new session. Machine checks are Python
scripts, so two checkers agree by construction.

## Why you would want it

- **Fewer interruptions.** Readiness is checked before anything starts, with the same
  numbered list every time, so the start-of-run check usually finds nothing.
- **No repeated checking.** Work that hasn't changed since it passed is not judged again at
  the next stage, which saves the time of the check and the new questions a fresh reviewer
  would raise about the same content.
- **One approval, one acceptance.** The rewritten wording of a card is not re-approved on
  every edit; your answer is the acceptance, and you judge intent once at the end against the
  evidence plan, every criterion shown with its evidence and accepted in one answer.
- **Rules that hold under load.** The guards block what prose rules only discourage.
- **A process that learns.** Every miss is recorded against the condition that let it through,
  and the gaps become the next grilling's checklist.
- **Project-agnostic.** Everything about your project lives in one profile: the board, where
  specs go, the test gate, the environments, how data is read without writing, branch and
  release conventions, standing answers. The plugin holds the process and nothing else.

## What it needs

- Claude Code, with the Claude desktop app for coordinating parent issues (sub-issue sessions
  are desktop sessions). Card and spec skills work in any Claude Code client.
- Python 3 on the machine, standard library only.
- A board in GitHub Projects or Azure DevOps, reached through its CLI.
- A git repository.

## Getting started

1. Add the marketplace and install the plugin:

   ```bash
   claude plugin marketplace add coder3814/DevFactory
   ```

   ```bash
   claude plugin install devfactory@devfactory
   ```

2. In your project, run `/devfactory:configure-project`. It reads your board and repository,
   asks you one question at a time, and writes `.devfactory/profile.md` plus the read-only
   permissions the skills need. Start a new session afterwards so the hooks load.
3. Write a card with `/devfactory:create-card`, then `/devfactory:grill` it. When the spec is
   Ready, approve it.
4. For a parent issue, `/devfactory:coordinate`. For one card, `/devfactory:build`. Then
   `/devfactory:accept` and `/devfactory:release`.

## Reading further

- [DESIGN.md](DESIGN.md): what the plugin is and how each part works, the design of record.
- `devfactory/references/definition-of-request.md`, `definition-of-ready.md` and
  `definition-of-done.md`: the three definitions, condition by condition.
- `devfactory/references/events.md`: the events and how a project hooks them.
- `devfactory/references/decision-line.md`: what the requester decides and what the developer
  decides.
- `devfactory/references/profile-template.md`: everything a project configures.
- `devfactory/scripts/README.md`: the script commands and how to run the tests.
