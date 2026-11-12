---
name: coordinate
description: Coordinate a parent issue run, entered from `start` — have agents read the run and create the parent branch, ask the requester once to start every session and start them all on the reply, each briefed to wait, settle readiness, set each session going as its waits clear, relay its questions, merge results into the parent branch one at a time, have the Done judge check the combined result, then go straight to acceptance, which hands it to release. Use when `start` hands over a card that is a parent issue; needs the Claude desktop app.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(python *devfactory.py*)
---

# Coordinate a parent issue

Coordinating needs the Claude desktop app: its session tools are what start, message, stop
and archive the sessions a run is made of.

`start` hands a parent issue here, in the session the requester's "start work" message
reached, and that session becomes the coordinator. It is a fresh session, never the one that
specified the parent or its sub-issues. It decides what runs when, relays between the
sessions and the requester, and is answerable for every event the run fires. It builds
nothing and reviews nothing, and it runs nothing itself, no git or tracker command included:
every read, command, event and change is done by an agent or a session it starts. The marker
calls below are the one exception. Agents suit reads, events and worktree clean-up; sessions
suit the work the requester may want to open, steer or stop. Every session it starts runs on
the model and effort the Suggested model and effort of the card it works on names, or the
profile's default under Sessions when that card names none. Named agents
(`readiness-checker`, `change-reviewer`, `done-judge`, `card-reviewer`) are started by name
with the Agent tool and carry their own model; any other agent is started with the Agent
tool too.

`devfactory` below means running the plugin's script with `python`: the script is
`${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`; if that variable is empty in your shell, it
is `../../scripts/devfactory.py` relative to this skill's folder.

**Markers.** Run `devfactory begin coordinate` as your first action and keep the marker
for the whole run, through every turn and wait: the git guard allows a push, or a merge
into the integration or the parent branch, only under it or under `release`. Run
`devfactory end coordinate` as your last action, at step 11, or when you stop and report
the run abandoned. A marker expires after the profile's Marker lifetime (12 hours by
default), and `begin` refreshes it, so run `devfactory begin coordinate` again whenever
you resume after a wait. Markers and the profile are found at the repository (worktree)
root, wherever the shell's working directory is. When `begin` prints `plugin-changed`,
load this skill again before you continue.

## Sessions

| Action | Tool |
|---|---|
| Start a session, briefed to wait | `start_session` with `initiation: "user_asked"`, `context: "fresh"`, its own worktree (`use_worktree: true`) cut from the parent branch (`source_branch`), `branch_name` set to the sub-issue's branch as the profile's Sub-issue branch entry names it, the `model` and `effort` the card's Suggested model and effort names, the brief below as `prompt`, and the run's goal and constraints as `background`. Record the session id and name the result returns. |
| Tell a waiting session to begin, send it an answer or a finding, or give it its turn to merge | `SendMessage` to the session's `local_…` id, never its display name. |
| Read a session's report | Every report, question and stop arrives as a message the session sends, which wakes this session on any turn. A `<side-sessions-event>` note that a session ended a turn carries nothing and is not acted on: end the turn. Read what a report leaves out from the card and the spec it updated, or ask the session to restate a part. |
| Stop a session | `stop_session`. |
| Finish a session | `mark_completed`, then `archive_session`, which stops it and lets the app remove its worktree. Only `release`'s reap does this for the run's sessions, under the release authorisation; its worktrees and branches are removed after the sessions are archived. |

The desktop app shapes the run:

- **Sessions start only on a turn the requester's own message began.** A start attempted
  on a turn that an agent's report or a session's message began is refused. So the turn
  that reaches this skill starts agents and ends; once they have reported, the run ends a
  turn with one question that names every session to start, and the requester's reply
  begins a turn of their own, in which every session is started with `initiation:
  "user_asked"`, each with its branch name. A session started so keeps the branch name
  given to it. Never propose a session as a card. A sub-issue added mid-run gets its
  session through the same single question.
- **Every agent runs in the background** and reports in a later turn. Start the agents a
  step needs together, end the turn, and carry on when they report.
- **Messaging works from any turn**, so set each session going when its waits are met, and
  relay answers and findings, from whatever turn a report began.
- **A note is not a message.** When a session ends a turn the app sends this session a
  note. It carries nothing: reports, questions and stops come by message only, and a note
  is not acted on.
- **A session holds the worktree it works in, even idle.** Archive the session first, then
  have a separate agent remove whatever is left of the worktree.
- **A report is a claim, not proof.** Check the branch, the spec and the card before acting
  on it or telling the requester it is done.
- **Link every session you name** as `[title](#local_<id>)` so the requester can open it.
- When the requester's message arrives mid-run about something else, answer it; the run
  continues on its own reports.

## The build session's brief

The brief names the card, the parent, the spec path, the parent branch and the sub-issue's
own branch, named by the profile's Sub-issue branch entry. It opens with this rule: report
to the coordinator as the plugin's `references/reporting-to-the-coordinator.md` says, by
message to the coordinator's `local_…` id (the session that started you, which your session
prompt names). Then it says, in this order:

1. Reply "waiting" and end your turn. You wait for the run's readiness check to settle as
   well as for what the work order makes you wait on; the coordinator messages you when
   both are done. When messaged to begin, load the `build` skill for this card and follow
   it from its first step, which marks the session as building and then rebases onto the
   parent branch named here, which brings in anything the readiness check amended.
2. The `build` skill fires `development-started` and `readiness-lost` for this card, and
   `grill` fires what its outcome calls for; leave every other event to the coordinator.
3. A question the spec, the profile's Standing answers and the decision line do not
   answer: stop, message it to the coordinator in the shape
   `references/reporting-to-the-coordinator.md` gives under "What each report carries", and
   wait. So too for findings past the review limit that `build` says to stop on.
4. Do not merge until the coordinator says it is this card's turn; never merge into the
   integration branch; never push.
5. When told it is your turn: rebase onto the parent branch, run the test gate as the
   plugin's `references/test-gate.md` says under "When the gate runs", fast-forward the
   parent branch with `git -C <parent worktree> merge --ff-only <branch>` run from this
   session's own worktree, never by changing into the parent worktree, message your
   report, and end your turn. Stay available: you, your worktree and your branch are kept
   until the run is accepted and released, and the coordinator may message you with a
   Done-judge finding or an acceptance refusal, your own card's or one no single sub-issue
   owns, which you fix against the card and spec the message names, as `build` says under
   "Fixing a finding or a refusal".

There is one coordinator per run. It never starts a session that acts as a coordinator; a
parent issue outside this run, such as one created along the way, is a new run the
requester starts.

**Asking the requester.** Every question first passes "Before anything is asked" in
[`../../references/decision-line.md`](../../references/decision-line.md): the profile's
Standing answers, then the decision line. Only what survives both reaches the requester,
one question at a time, the recommended option first with a one-line reason. Nothing in
this run asks for a go-ahead to take the next step it prescribes, except the one question
that starts the sessions, which the app's rule on starting sessions requires.

## Read these first, in full

A file you have already read in full in this session, under the plugin version `begin`
printed, need not be read again.

- The project profile and the binding it names, as
  [`../../references/working-a-card.md`](../../references/working-a-card.md) says.
- [`../../references/modules/work-order.md`](../../references/modules/work-order.md): the
  waits and what may run alongside what.
- [`../../references/decision-line.md`](../../references/decision-line.md): the test every
  question passes first, and the findings that carry on past the review limit.
- [`../../references/definition-of-ready.md`](../../references/definition-of-ready.md) and
  [`../../references/definition-of-done.md`](../../references/definition-of-done.md).
- [`../../references/spec-template.md`](../../references/spec-template.md).
- [`../../references/reporting-to-the-coordinator.md`](../../references/reporting-to-the-coordinator.md):
  how each session reports.
- The Inputs section of [`../../agents/done-judge.md`](../../agents/done-judge.md).

## Steps

1. **Read the run and create the parent branch.** In the turn that reached this skill,
   start two agents together, then say in one line what was started and end the turn.
   - One reads the parent issue and every sub-issue its work order names, in full with
     its comments, and reports for each sub-issue its number, its Suggested model and
     effort, its spec line and spec status, and what it waits on. A sub-issue that is
     itself a parent issue is coordinated in place: its sub-issues join this run in its own
     work order, and the agent reads and reports them the same way.
   - The other fires `work-started` for the parent and for each sub-issue the parent's work
     order names, as `start` read it, then creates the parent branch and its worktree as
     the profile's Branches and merging says, cut from the integration branch, which
     carries the specs. Once the first agent reports the sub-issues of a nested parent,
     have an agent fire `work-started` for each of them too.

   No session works in the parent worktree; only the run's records folder is committed
   there, by an agent, when a step below writes to it. Sub-issues merge into the parent branch, never into
   the integration branch. Note whether the requester's starting instruction
   authorises the release ahead of time, such as "drive all the way to the end": step 10
   acts on it.

2. **Ask once to start the sessions.** When both agents have reported, check the reports
   against each other. A sub-issue whose spec status is not `approved` is not built in this
   run, wherever it sits on the board; the parent stays open until it is done. End the turn
   with one question that names every session to start, one per sub-issue this run builds,
   and in the same message say which sub-issues wait and why, and which sub-issue waits on
   which other parent issue.

3. **Start every session.** The requester's reply begins a turn of their own. In it, start
   every session the question named, each with `start_session` as "Sessions" says and
   briefed to wait with the brief above. Link each one for the requester, and say in one
   line that the sessions are started.

4. **Settle readiness.** Follow `check-ready` over the parent, at development start. It ran
   when the parent was created and each time a card was added, so it should find nothing;
   anything it finds is settled with the requester and folded now. Every read and write it
   calls for is delegated to an agent. No session is set going until it reports nothing
   open. When its folds committed anything to the integration branch, have an agent rebase
   the parent branch onto it before any session begins. A sub-issue the check finds no
   longer Ready keeps its session waiting until its spec is approved again; one that leaves
   the run has its session stopped and archived, then its worktree and branch removed by an
   agent.

5. **Set each going.** Message a sub-issue's session to begin when all of these hold, and
   say in one line which session was set going:
   - the readiness check of step 4 reported nothing open;
   - every wait the work order gives it is met. A sub-issue that waits on another begins
     only once that one is merged into the parent branch. One that waits on another parent
     issue begins once the code it waits on is on the integration branch and this parent
     branch is rebased onto it. While such a wait is unmet, have an agent check it again at
     every wake, by content, since a rebase changes commit ids: `git cherry <integration
     branch> <other parent's branch>` lists no commit marked `+`, so each commit of the
     other parent has one carrying the same change on the integration branch. When the
     other parent's branch no longer exists, the agent finds its sub-issues' changes on the
     integration branch by reading its log and the files they change. When the wait is
     met, have an agent rebase this parent branch onto the integration branch while no
     session is merging, and confirm the integration branch is an ancestor of it (`git
     merge-base --is-ancestor`). Nothing else, such as a board column, a closed card or a
     deploy, is waited for;
   - every owner step its spec schedules before that point is done. When an owner step's
     moment arrives, ask the requester to take it, and set the session going once they say
     it is done.

   Run as many at once as the waits allow. If the machine cannot sustain that many at
   once, hold the extra ones back and tell the requester which and why. When the first
   sub-issue begins, have an agent fire `development-started` for the parent, and for any
   nested parent whose sub-issue it is.

   A sub-issue added to the parent during the run is checked by `grill`'s parent path, as
   any card added to a parent issue is, which follows `check-ready` at creation over the
   set. It needs a session of its own: when it is approved, end a turn with the one
   question that names its session, as "Sessions" says, and start it, briefed to wait, in
   the turn the requester's reply begins.

6. **Relay questions.** A question pauses only the sub-issue that raised it. Read it in the
   shape `reporting-to-the-coordinator.md` gives under "What each report carries". A
   question a `grill` Re-derive raises in the session, the request to approve a spec whose
   status returned to `Ready` included, is relayed the same way as any other.
   - Test it as "Asking the requester" says, against the spec as well. A question a
     standing answer, the developer's side or the spec already answers goes back to the
     session with what answers it, and nothing is asked.
   - Otherwise put it to the requester as the session gave it: the question, the options
     with the recommendation first, and the Ready condition that failed. When several
     sessions raise the same gap, ask for the rule once.
   - Send the answer to the session word for word, with the Ready condition that failed,
     telling it to apply the answer on its own branch and continue: when the answer changes
     the card, as [`spec-procedure.md`](../../references/spec-procedure.md) says under "A
     card-changing answer", through `add-to-card` in settled mode passing `no-rederive`
     and then `grill` Re-derive, with the stage, Development, and `--kind request-change`
     when the requester changed their mind rather than answered a miss; when it leaves the
     card as it is, through `grill` Amend. An approval answer goes back the same way, for
     `grill` to set `approved`.
   - When the session reports that the answer changes what another sub-issue waits on, have
     an agent revise the work order on the parent as "A card-changing answer" says, citing
     the answer that drove it, and re-check what may run.

7. **Handle a request change.** When the requester changes what a card asks for during the
   run, outside an answer to a question, have the card changed as `spec-procedure.md` says
   under "A card-changing answer": through `add-to-card` in settled mode passing
   `no-rederive`, with the requester's words as the comment, then `grill` Re-derive, given
   the stage the work is at, the condition that let it through, written `Ready <id>`, and
   `--kind request-change`, brings the spec along for the
   conditions the change feeds.
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
     branch, the spec's log and gap record, the session's review record, which `devfactory
     reviews show --card <id>` prints, and the review verdict. A session whose review
     limit was reached with every finding on the developer's side has fixed them and
     carried on, as "Findings after the review limit" in `decision-line.md`
     says; its report says so, with "no review passed this revision" when no review ran
     after the last fix, and it is checked the same way.
   - When a session reports findings past its review limit that change what an observer
     sees or can do, what persisted data ends up as, or scope, put those findings to the
     requester and ask how to proceed; the sub-issue does not merge meanwhile.
   - When it is a card's turn, message its session to merge as its brief says: rebase onto
     the parent branch, run the test gate as `references/test-gate.md` says under "When the
     gate runs", and fast-forward the parent branch with `git -C <parent worktree> merge
     --ff-only <branch>` from its own worktree. When the fast-forward refuses, the session
     stops and reports it, and nothing is forced.
   - Keep the session, its worktree and its branch: they stay until `accept` ends in
     acceptance, and `release` reaps them.
   - Then have an agent fire `done` for the sub-issue, and say in one line that it merged.

9. **Judge the combined result.** The run captures no evidence of its own process: that
   each sub-issue merged and passed its review, and that the gate passes on the parent
   branch, are facts the Done judge establishes itself under Done 6.1, so nothing is
   captured or committed for them before it runs. When every sub-issue this run builds is
   merged, start the `done-judge` agent by name with the Agent tool; it carries its own
   definition, tools and model. Give it every input its Inputs section lists: the path to
   the plugin's `references/` folder, the parent card, each sub-issue's card and spec path,
   the profile path, the base revision (the integration branch commit the parent branch was
   cut from or last rebased onto), the parent branch's head, and a clean checkout at that
   head, made by an agent as a worktree of the repository (`git worktree add --detach`) so
   it reads the same gate records; never how the work was built.
   - After each judgment, have an agent write the findings to a file outside the
     repository, run `devfactory reviews add --card <parent id> --round <n> --verdict
     <DONE|NOT DONE> --findings <that file>`, which records the judgment under the parent's
     id outside the tracked tree, commit nothing for it, and remove the judge's checkout
     (`git worktree remove --force <path>`). Say in one line what the judgment was.
   - A finding that belongs to one sub-issue goes by message to that sub-issue's kept
     session, which fixes it on its branch, rebased onto the parent branch. A finding no
     single sub-issue owns goes by message to the kept session of the sub-issue whose files
     it touches most, naming the card and spec it fixes against. No session is started for
     a finding. Say in one line which finding went where.
   - Each fix is reviewed by its change reviewer and merged as step 8 says; a finding that
     is a readiness miss gets a gap entry through `grill` Amend, its condition written
     `Ready <id>`. Judge again once the findings are merged.
   - After a NOT DONE there are at most two further rounds. When the third judgment is
     still NOT DONE, sort its findings by the decision line's "Findings after the review
     limit". When every finding is on the developer's side, have them fixed as above and
     carry on without asking: after a code fix, review and judge once more; when every fix
     is a spec-only amendment, say so in the message to each session, so it amends the spec
     through `grill` Amend and reports without a review, then merge it as step 8 says. Once
     every amendment is merged, have an agent run `devfactory spec-only <specs path> --base
     <the judged revision>` on the parent branch. Only when it prints `spec-only` does the
     run go straight to step 10, with no further judgment, carrying to `accept` the line "no
     review passed this revision", the last judgment's findings and their amendments; when
     it prints any `outside` path, judge once more. Escalate to the requester, and wait,
     only with findings that change what an observer sees or can do, what persisted data
     ends up as, or scope, or when the extra judgment is still NOT DONE.
   - On DONE, or when a spec-only round past the limit is merged and `spec-only` confirmed
     it, have an agent fire `done` for the parent and for each nested parent in it.

10. **Accept.** Go straight into `accept` for the parent run once the Done judge says DONE,
    or once step 9 sends a spec-only round on, with the line, findings and amendments step
    9 carries; ask nothing first. `accept` runs in this session, under this coordinator's
    marker and its own, and does every command through a session or an agent. It ends in
    the release: what an authorisation to release does is stated once, in `release` under
    "What an authorisation covers". When step 1 noted a release authorised ahead of time,
    or the requester's acceptance authorises it, start `release`; otherwise `accept` asks
    once, and on a yes start `release` yourself, never on your own judgment. A refusal
    `accept` sorts as a defect or a request change is built as step 9's findings are: by
    the kept session of the sub-issue it belongs to, or by the kept session of the
    sub-issue whose files it touches most when no sub-issue owns it. A defect goes to that
    session with the `Done <id>` `accept` named, and the session writes its gap entry once
    the fix is committed, as `build` says under "Fixing a finding or a refusal". Its fix is
    reviewed and merged as step 8 says, which fires `done` for that sub-issue, and judged
    again by the Done judge as step 9 says, which fires `done` for the parent on DONE; then
    `accept` runs again.

11. **Stop.** Once `release` has reaped, confirm from its closing list of steps that
    `curate` ran and that every post-release plan was captured or reported, that every
    session you started is marked completed and archived, and that every agent you started
    has stopped, each having stopped its own. Report anything you cannot confirm: a session
    not archived, a worktree kept, a branch not deleted, a plan neither captured nor
    reported. Run `devfactory markers --clear-stale` to remove any marker left behind past
    its lifetime, then run `devfactory end coordinate`.

## Throughout

- **Events.** The run moves no card on the board; it fires the events in
  [`../../references/events.md`](../../references/events.md), and the project's hooks move
  cards as the project wants. The coordinator fires `work-started` for every card the run
  covers, `development-started` for the parent and each nested parent, and `done` for each
  sub-issue it merges and for the parent and each nested parent on the Done judge's DONE,
  again after a refusal's fix. The coordinator is answerable for every event in the run,
  whoever fires it: a hook failure a session or agent reports is reported to the requester
  with its output, and the work carries on. The parent closes only when every one of its
  sub-issues is released.
- **Progress.** At each milestone (sessions started, a session set going, a merge, a
  finding sent, a judgment) say one line to the requester. A progress line asks nothing.
- **Work no card asks for.** Work found along the way that no card asks for becomes a
  standalone card through `create-card`, never a new sub-issue of this parent.
