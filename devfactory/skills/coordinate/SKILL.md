---
name: coordinate
description: Coordinate a parent issue run — settle readiness before anything starts, start one session per sub-issue briefed to wait, set each going as its waits clear, relay its questions, merge results into the parent branch one at a time, have the Done judge check the combined result, then hand it to acceptance, which hands it to release. Use when the requester says to start work on a card that is a parent issue; needs the Claude desktop app.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(node *devfactory.js*)
---

# Coordinate a parent issue

Coordinating needs the Claude desktop app: its session tools are what start, message, stop
and archive the sessions a run is made of.

"Start work on" a parent issue makes the session that receives it the coordinator. It is a
fresh session, never the one that specified the parent or its sub-issues. It decides what
runs when, relays between the sessions and the requester, and is answerable for every
card's column in the run. It builds nothing and reviews nothing, and it runs nothing
itself, no git or tracker command included: every read, command, board move and change is
done by a session or a subagent it starts. The marker calls below are the one exception.
Subagents suit reads, board moves and worktree clean-up; sessions suit the work the
requester may want to open, steer or stop. Every session it starts runs on the model and
effort the Suggested model and effort of the card it works on names (the parent's, for work
across the run), or the profile's default under Sessions when that card names none. Named
agents (`readiness-checker`, `change-reviewer`, `done-judge`, `card-reviewer`) are started
by name with the Agent tool and carry their own model; any other subagent is started with
the Agent tool too.

`devfactory` below means running the plugin's script with `node`: the script is
`${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.js`; if that variable is empty in your shell, it
is `../../scripts/devfactory.js` relative to this skill's folder.

**Markers.** Run `devfactory begin coordinate` as your first action and keep the marker
for the whole run, through every turn and wait: the git guard allows a push, or a merge
into the integration or the parent branch, only under it or under `release`. Run
`devfactory end coordinate` as your last action, at step 11, or when you stop and report
the run abandoned. A marker expires after the profile's Marker lifetime (12 hours by
default), and `begin` refreshes it, so run `devfactory begin coordinate` again whenever
you resume after a wait. Markers and the profile are found at the repository (worktree)
root, wherever the shell's working directory is.

## Sessions

| Action | Tool |
|---|---|
| Start a session for a card, briefed to wait | `start_session` with `initiation: "user_asked"`, `context: "fresh"`, its own worktree (`use_worktree: true`) cut from the parent branch (`source_branch`), the `model` and `effort` the card's Suggested model and effort names, the brief below as `prompt`, and the run's goal and constraints as `background`. Record the session id and name the result returns. |
| Tell a waiting session to begin, send it an answer, or give it its turn to merge | `SendMessage` to the session's `local_…` id, never its display name. |
| Read a session's report | Its final message arrives as a `<side-sessions-event>` note quoting the report's first 400 characters; read the rest from the card and the spec it updated, or ask the session to restate a part. |
| Stop a session | `stop_session`, then `archive_session` once its worktree and branch are gone. |

The desktop app shapes the run:

- **Sessions start only on a turn the requester's own message began.** On a turn a
  notification began, a start is offered as a card that waits for a click, so a run left
  unattended stalls. Start every sub-issue's session up front, in the requester's turn.
- **Messaging works from any turn**, so set each session going when its waits are met, and
  relay answers, from a notification turn.
- **A session cannot remove the worktree it works in.** Have a separate subagent remove it.
- **A report is a claim, not proof.** Check the branch, the spec and the card before acting
  on it or telling the requester it is done.
- **Link every session you name** as `[title](#local_<id>)` so the requester can open it.
- Run commands likely to exceed about two minutes in the background. When the requester's
  message arrives mid-run about something else, answer it; the run continues on its own
  notifications.

## The build session's brief

The brief names the card, the parent, the spec path, the parent branch and the sub-issue's
own branch, named by the profile's Sub-issue branch entry, and says, in this order:

1. Reply "waiting" and end your turn. When messaged to begin, load the `build` skill for this
   card and follow it from its first step, which marks the session as building before
   anything else; its second step is the rebase onto the parent branch named here.
2. Move the card to the development column as work starts; leave every other column move
   to the coordinator.
3. A question the spec and the decision line do not answer: stop and report it to the
   coordinator in the shape the `build` skill gives, and wait.
4. Do not merge until the coordinator says it is this card's turn; never merge into the
   integration branch; never push.
5. When told it is your turn: rebase onto the parent branch, rerun the tests, fast-forward
   the parent branch with `git -C <parent worktree> merge --ff-only <branch>` run from this
   session's own worktree, never by changing into the parent worktree, report, and end your
   turn. Stay available: you, your worktree and your branch are kept until the run is
   accepted and released, and the coordinator may message you with a Done-judge finding or
   an acceptance refusal.

There is one coordinator per run. It never starts a session that acts as a coordinator; a
parent issue outside this run, such as one created along the way, is a new run the
requester starts.

The requester is asked one question at a time, the recommended option first with a
one-line reason.

## Read these first, in full

- The project profile and the binding it names, as
  [`../../references/working-a-card.md`](../../references/working-a-card.md) says.
- [`../../references/modules/work-order.md`](../../references/modules/work-order.md): the
  waits and what may run alongside what.
- [`../../references/decision-line.md`](../../references/decision-line.md): the test every
  relayed question passes first.
- [`../../references/definition-of-ready.md`](../../references/definition-of-ready.md) and
  [`../../references/definition-of-done.md`](../../references/definition-of-done.md).
- [`../../references/spec-template.md`](../../references/spec-template.md).
- [`../build/SKILL.md`](../build/SKILL.md): what each session does.

## Steps

1. **Read the parent.** Have an agent read the parent issue, its work order, and every
   sub-issue in full with its comments, and report each one's column, spec line, spec
   status and what it waits on. A sub-issue that is itself a parent issue is coordinated in
   place: its sub-issues join this run in its own work order. A sub-issue whose spec status
   is not `approved` is not built in this run, whatever its column: tell the requester which
   ones wait and why. The parent stays open until they are done.

2. **Settle readiness.** Follow `check-ready` over the parent, at development start. It ran
   when the parent was created and each time a card was added, so it should find nothing;
   anything it finds is settled with the requester and folded now. Every read and write it
   calls for is delegated to an agent. No session starts until it reports nothing open.

3. **Create the parent branch.** Have an agent create the parent branch and its worktree as
   the profile's Branches and merging says, cut from the integration branch, which carries
   the specs. No one works in the parent worktree. Sub-issues merge into the parent branch,
   never into the integration branch.

4. **Start every session up front.** Start one session for each sub-issue this run builds,
   all of them in the requester's turn and before the first begins, each with
   `start_session` as "Sessions" says and briefed to wait with the brief above. Each runs on
   the model and effort its card's Suggested model and effort names, or the profile's
   default. Link each one for the requester.

5. **Set each going.** Message a session to begin when both hold:
   - every wait the work order gives it is met: a sub-issue that waits on another begins
     only once that one is merged into the parent branch, and one that waits on another
     parent's release begins only once that release is live and the parent branch is
     rebased onto the integration branch;
   - every owner step its spec schedules before that point is done. When an owner step's
     moment arrives, ask the requester to take it, and set the session going once they say
     it is done.

   Run as many at once as the waits allow. If the machine cannot sustain that many at
   once, hold the extra ones back and tell the requester which and why. When the first
   sub-issue begins, have the parent, and any nested parent whose sub-issue it is, moved to
   Development.

6. **Relay questions.** A question pauses only the sub-issue that raised it. Read it in the
   shape `build` gives it.
   - Test it against the decision line and the spec first. A question the developer's side
     or the spec already answers goes back to the session with what answers it, and nothing
     is asked.
   - Otherwise put it to the requester as the session gave it: the question, the options
     with the recommendation first, and the Ready condition that failed. When several
     sessions raise the same gap, ask for the rule once.
   - Send the answer to the session word for word, telling it to apply it through `grill`
     in amend mode and continue. The amendment writes the spec change and the gap entry on
     the session's branch, and, when the answer changes observable behaviour or scope, the
     card through `add-to-card` in settled mode, the answer being the acceptance.
   - When the session reports that the answer changes what another sub-issue waits on, have
     the work order revised on the parent through `add-to-card` in settled mode, citing the
     answer that drove it, and re-check what may run.

7. **Handle a request change.** When the requester changes what a card asks for during the
   run, outside an answer to a question, have the card changed through `add-to-card` in
   settled mode, with the requester's words as the comment, and let its hand-off to `grill`
   re-derive bring the spec along for the conditions the change feeds.
   Once the sub-issue's session has begun, its session does this on its own branch, where
   the spec now lives; before then, an agent does it on the parent branch. Tell every
   session the change affects (its spec changed, or its waits or files did) to rebase onto
   the re-derived spec and continue, and re-check the work order. A change to a sub-issue
   already merged is fixed as step 9's findings are. A refusal at acceptance is `accept`'s
   to classify, not this step's.

8. **Merge one at a time.** Merge results in the order they finish, so parallel sessions
   never merge over each other, and a sub-issue that waits on another merges after the one
   it waits on.
   - When a session reports its review passed, have an agent check the report against the
     branch, the spec's log and gap record, and the review verdict. When a session reports
     that its third review still failed, put the findings to the requester and ask how to
     proceed; the sub-issue does not merge meanwhile.
   - When it is a card's turn, message its session to merge as its brief says: rebase onto
     the parent branch, rerun the tests, and fast-forward the parent branch with
     `git -C <parent worktree> merge --ff-only <branch>` from its own worktree. When the
     fast-forward refuses, the session stops and reports it, and nothing is forced.
   - Keep the session, its worktree and its branch: they stay until `accept` ends in
     acceptance, and `release` reaps them.
   - Then have the sub-issue moved to Done, and a nested parent moved to Done once all its
     sub-issues are there.

9. **Judge the combined result.** When every sub-issue this run builds is merged, start the
   `done-judge` agent by name with the Agent tool; it carries its own definition
   ([`../../agents/done-judge.md`](../../agents/done-judge.md)), tools and model. Give it the
   path to the plugin's
   `references/` folder, the parent card and spec path, each sub-issue's card and spec path,
   the profile path, the base revision (the integration branch commit the parent branch was
   cut from or last rebased onto), the parent branch's head, and a clean checkout at that
   head, never how the work was built. A finding that belongs to one sub-issue goes to
   that sub-issue's kept session, which fixes it on its branch, rebased onto the parent
   branch; a finding no single sub-issue owns is fixed by a new session started and
   briefed as a sub-issue's is, in a worktree cut from the parent branch. A session can
   start only in the requester's turn, so on a notification turn tell the requester the
   start waits for their click, with the reason. Either is
   reviewed by its change reviewer and merged as step 8 says; a finding that
   is a readiness miss gets a gap entry through `grill` in amend mode. Judge again once the
   findings are merged. After a NOT DONE there are at most two further rounds: when the
   third judgment is still NOT DONE, stop and report it to the requester with its findings,
   and wait. On DONE, have the parent moved to Done.

10. **Accept.** Follow `accept` for the parent run. It ends by asking the requester to start
    `release`, which only the requester can start; it runs in this session, under this
    coordinator's marker and its own, and does every command through a session or a
    subagent. A refusal `accept` sorts as a defect or a
    request change is built as step 9's findings are: by the kept session of the sub-issue
    it belongs to, or by a new session cut from the parent branch when no sub-issue owns
    it, reviewed and merged the same way, and then goes back to `accept`.

11. **Stop.** Once `release` has reaped, confirm that every session and agent you started
    has stopped, and that each agent stopped its own. Report anything you cannot confirm has
    stopped. Run `devfactory markers --clear-stale` to remove any marker left behind past
    its lifetime, then run `devfactory end coordinate`.

## Throughout

- **Columns.** A move to a stage is a move to the column the profile's Stages map it to.
  The coordinator is answerable for every card's column in the run, whoever makes the
  move. After each move that should have happened, the session's own move to
  Development included, have an agent check the board and make any move that is missing.
  The parent moves to Release and closes only when every one of its sub-issues is released;
  until then it stays in Development for those still waiting.
- **Progress.** Report to the requester at each phase: what is running, what is done, what
  is waiting and on what.
- **Work no card asks for.** Work found along the way that no card asks for becomes a
  standalone card through `create-card`, never a new sub-issue of this parent.
