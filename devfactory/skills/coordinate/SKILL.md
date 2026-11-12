---
name: coordinate
description: Coordinate a parent issue run — in the requester's opening turn start one session per sub-issue and one for parent fixes, each briefed to wait, settle readiness, set each session going as its waits clear, relay its questions, merge results into the parent branch one at a time, have the Done judge check the combined result, then go straight to acceptance, which hands it to release. Use when the requester says to start work on a card that is a parent issue; needs the Claude desktop app.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(python *devfactory.py*)
---

# Coordinate a parent issue

Coordinating needs the Claude desktop app: its session tools are what start, message, stop
and archive the sessions a run is made of.

"Start work on" a parent issue makes the session that receives it the coordinator. It is a
fresh session, never the one that specified the parent or its sub-issues. It decides what
runs when, relays between the sessions and the requester, and is answerable for every
event the run fires. It builds nothing and reviews nothing, and it runs nothing
itself, no git or tracker command included: every read, command, event and change is
done by a session or a subagent it starts. The marker calls below are the one exception.
Subagents suit reads, events and worktree clean-up; sessions suit the work the
requester may want to open, steer or stop. Every session it starts runs on the model and
effort the Suggested model and effort of the card it works on names (the parent's, for work
across the run), or the profile's default under Sessions when that card names none. Named
agents (`readiness-checker`, `change-reviewer`, `done-judge`, `card-reviewer`) are started
by name with the Agent tool and carry their own model; any other subagent is started with
the Agent tool too.

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
root, wherever the shell's working directory is.

## Sessions

| Action | Tool |
|---|---|
| Start a session, briefed to wait | `start_session` with `initiation: "user_asked"`, `context: "fresh"`, its own worktree (`use_worktree: true`) cut from the parent branch (`source_branch`), the `model` and `effort` the card's Suggested model and effort names, the brief below as `prompt`, and the run's goal and constraints as `background`. Record the session id and name the result returns. |
| Tell a waiting session to begin, send it an answer or a finding, or give it its turn to merge | `SendMessage` to the session's `local_…` id, never its display name. |
| Read a session's report | The session sends every report, question and stop as a message (the brief says so), which wakes this session on any turn. A `<side-sessions-event>` note quoting a session's final message is not the channel: the app holds those notes back after many in a row with no message from the requester. On a note that carries nothing the session has not already sent by message, such as a session ending a turn to wait, do nothing and end the turn. When a session's note or final message shows a report it did not send, message it to send its report. Read what a report leaves out from the card and the spec it updated, or ask the session to restate a part. |
| Stop a session | `stop_session`. |
| Finish a session | `mark_completed`, then `archive_session`, which stops it and lets the app remove its worktree. Only `release` step 8 does this for the run's sessions, under the release authorisation; its worktrees and branches are removed after the sessions are archived. |

The desktop app shapes the run:

- **Sessions start only on a turn the requester's own message began.** On a turn a
  notification or an agent's report began, a start is offered as a card that waits for a
  click, so a run left unattended stalls. So every session the run will need is started in
  the turn of the requester's "start work" message, before anything that ends that turn:
  one per sub-issue, and one for parent fixes. Read the parent with agents that report
  within the turn (in the foreground), and send nothing to a background agent before the
  sessions are started. The one start that can still wait for a click is a session for a
  sub-issue added to the parent mid-run; say so when it happens, with the reason.
- **Messaging works from any turn**, so set each session going when its waits are met, and
  relay answers and findings, from a notification turn.
- **A session holds the worktree it works in, even idle.** Archive the session first, then
  have a separate subagent remove whatever is left of the worktree.
- **A report is a claim, not proof.** Check the branch, the spec and the card before acting
  on it or telling the requester it is done.
- **Link every session you name** as `[title](#local_<id>)` so the requester can open it.
- Run commands likely to exceed about two minutes in the background. When the requester's
  message arrives mid-run about something else, answer it; the run continues on its own
  notifications.

## The build session's brief

The brief names the card, the parent, the spec path, the parent branch and the sub-issue's
own branch, named by the profile's Sub-issue branch entry. It opens with this rule:
every report, question and stop you make, the merge report included, goes to the
coordinator as a message you send with `SendMessage` to the coordinator's `local_…` id
(the session that started you, which your session prompt names) before you end the turn,
as `build` says under "Reporting to the coordinator"; a final message alone does not reach
the coordinator reliably; keep your turn open while your own commands run, and end it only
to wait for the coordinator. Then it says, in this order:

1. Reply "waiting" and end your turn. You wait for the run's readiness check to settle as
   well as for what the work order makes you wait on; the coordinator messages you when
   both are done. When messaged to begin, load the `build` skill for this card and follow
   it from its first step, which marks the session as building and then rebases onto the
   parent branch named here, which brings in anything the readiness check amended.
2. The `build` skill fires `development-started` as work starts; leave every other event
   to the coordinator.
3. A question the spec, the profile's Standing answers and the decision line do not
   answer: stop, message it to the coordinator in the shape the `build` skill gives, and
   wait. So too for findings past the review limit that `build` says to stop on.
4. Do not merge until the coordinator says it is this card's turn; never merge into the
   integration branch; never push.
5. When told it is your turn: rebase onto the parent branch, run the test gate as `build`
   says under "The test gate", fast-forward
   the parent branch with `git -C <parent worktree> merge --ff-only <branch>` run from this
   session's own worktree, never by changing into the parent worktree, message your report,
   and end your turn. Stay available: you, your worktree and your branch are kept until the run is
   accepted and released, and the coordinator may message you with a Done-judge finding or
   an acceptance refusal, which you fix as `build` says under "Fixing a finding or a
   refusal".

**The parent-fixes session's brief** is the same, with these differences: its card is the
parent issue, and its spec is the parent's; its branch is named by the profile's Sub-issue
branch entry with the parent's id as the card's; it fires no event, `development-started`
included, since the coordinator fires the parent's; and it is not set going when readiness
settles. It waits until the coordinator messages it to capture the parent's own evidence
rows once every sub-issue is merged (step 9), or a Done-judge finding or an acceptance
refusal that no single sub-issue owns, then follows `build` under "Fixing a finding or a
refusal" for the parent, and after its merge waits again, kept like the others, for the
next one.

There is one coordinator per run. It never starts a session that acts as a coordinator; a
parent issue outside this run, such as one created along the way, is a new run the
requester starts.

**Asking the requester.** Every question first passes "Before anything is asked" in
[`../../references/decision-line.md`](../../references/decision-line.md): the profile's
Standing answers, then the decision line. Only what survives both reaches the requester,
one question at a time, the recommended option first with a one-line reason. Nothing in
this run asks for a go-ahead to take the next step it prescribes.

## Read these first, in full

- The project profile and the binding it names, as
  [`../../references/working-a-card.md`](../../references/working-a-card.md) says.
- [`../../references/modules/work-order.md`](../../references/modules/work-order.md): the
  waits and what may run alongside what.
- [`../../references/decision-line.md`](../../references/decision-line.md): the test every
  question passes first, and the findings that carry on past the review limit.
- [`../../references/definition-of-ready.md`](../../references/definition-of-ready.md) and
  [`../../references/definition-of-done.md`](../../references/definition-of-done.md).
- [`../../references/spec-template.md`](../../references/spec-template.md).
- [`../build/SKILL.md`](../build/SKILL.md): what each session does.

## Steps

Steps 1 to 3 run in the turn of the requester's "start work" message, and that turn does
not end before step 3 has started every session.

1. **Read the parent.** Have an agent, in the foreground, read the parent issue, its work
   order, and every sub-issue in full with its comments, and report each one's spec line,
   spec status and what it waits on. A sub-issue that is itself a parent issue is
   coordinated in place: its sub-issues join this run in its own work order. A sub-issue
   whose spec status is not `approved` is not built in this run, wherever it sits on the
   board: tell the requester which ones wait and why. The parent stays open until they are
   done. Note whether the requester's starting instruction authorises the release ahead of
   time, such as "drive all the way to the end": step 10 acts on it.

2. **Create the parent branch.** Have an agent, in the foreground, fire `work-started` for
   the parent and for each sub-issue this run covers, then create the parent branch and its
   worktree as the profile's Branches and merging says, cut from the integration branch,
   which carries the specs. No one works in the parent worktree. Sub-issues merge into the
   parent branch, never into the integration branch.

3. **Start every session up front.** Start one session for each sub-issue this run builds,
   and the parent-fixes session, all of them in the requester's turn, each with
   `start_session` as "Sessions" says and briefed to wait with the briefs above. Each runs
   on the model and effort its card's Suggested model and effort names (the parent's for
   the parent-fixes session), or the profile's default. Link each one for the requester.

4. **Settle readiness.** Follow `check-ready` over the parent, at development start. It ran
   when the parent was created and each time a card was added, so it should find nothing;
   anything it finds is settled with the requester and folded now. Every read and write it
   calls for is delegated to an agent, which may run in the background now that every
   session is started. No session is set going until it reports nothing open. When its
   folds committed anything to the integration branch, have an agent rebase the parent
   branch onto it before any session begins. A sub-issue the check finds no longer Ready
   keeps its session waiting until its spec is approved again; one that leaves the run has
   its session stopped and archived, then its worktree and branch removed by a subagent.

5. **Set each going.** Message a sub-issue's session to begin when all of these hold:
   - the readiness check of step 4 reported nothing open;
   - every wait the work order gives it is met: a sub-issue that waits on another begins
     only once that one is merged into the parent branch, and one that waits on another
     parent issue begins once the code it waits on is on the integration branch and this
     parent branch is rebased onto it. Have an agent check it by content, since a rebase
     changes commit ids: `git cherry <integration branch> <other parent's branch>` lists
     no commit marked `+`, so each commit of the other parent has one carrying the same
     change on the integration branch, and the integration branch is an ancestor of this
     parent branch (`git merge-base --is-ancestor`). When the other parent's branch no
     longer exists, the agent finds its sub-issues' changes on the integration branch by
     reading its log and the files they change. Nothing else, such as a board column, a
     closed card or a deploy, is waited for;
   - every owner step its spec schedules before that point is done. When an owner step's
     moment arrives, ask the requester to take it, and set the session going once they say
     it is done.

   Run as many at once as the waits allow. If the machine cannot sustain that many at
   once, hold the extra ones back and tell the requester which and why. When the first
   sub-issue begins, have an agent fire `development-started` for the parent, and for any
   nested parent whose sub-issue it is.

   A sub-issue added to the parent during the run is checked by `check-ready` as a card
   added to a parent issue, and needs a session of its own: start it, briefed to wait,
   when the requester next sends a message, or offer it on a notification turn and tell
   the requester the start waits for their click.

6. **Relay questions.** A question pauses only the sub-issue that raised it. Read it in the
   shape `build` gives it.
   - Test it as "Asking the requester" says, against the spec as well. A question a
     standing answer, the developer's side or the spec already answers goes back to the
     session with what answers it, and nothing is asked.
   - Otherwise put it to the requester as the session gave it: the question, the options
     with the recommendation first, and the Ready condition that failed. When several
     sessions raise the same gap, ask for the rule once.
   - Send the answer to the session word for word, telling it to apply it as step 7.3 of
     `build` says and continue: when the answer changes the card, through `add-to-card` in
     settled mode with no-rederive first, the answer being the acceptance; then, for every
     answer, through `grill` in amend mode, which writes the spec change and the gap entry
     on the session's branch and never changes the card.
   - When the session reports that the answer changes what another sub-issue waits on, have
     the work order revised on the parent through `add-to-card` in settled mode with
     no-rederive, citing the answer that drove it, then the parent's spec amended through
     `grill` in amend mode, and re-check what may run.

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
     branch, the spec's log and gap record, and the review verdict. A session whose review
     limit was reached with every finding on the developer's side has fixed them and
     carried on as `build` step 8 says; its report says so, and it is checked the same way.
   - When a session reports findings past its review limit that change what an observer
     sees or can do, what persisted data ends up as, or scope, put those findings to the
     requester and ask how to proceed; the sub-issue does not merge meanwhile.
   - When it is a card's turn, message its session to merge as its brief says: rebase onto
     the parent branch, run the test gate as `build` says, and fast-forward the parent branch with
     `git -C <parent worktree> merge --ff-only <branch>` from its own worktree. When the
     fast-forward refuses, the session stops and reports it, and nothing is forced.
   - Keep the session, its worktree and its branch: they stay until `accept` ends in
     acceptance, and `release` reaps them.
   - Then have an agent fire `done` for the sub-issue.

9. **Judge the combined result.** The run captures no evidence of its own process: that
   each sub-issue merged and passed its review, and that the gate passes on the parent
   branch, are facts the Done judge establishes itself under Done 6.1, so nothing is
   captured or committed for them before it runs. When the parent's spec has evidence rows
   for parent criteria, among them the finished figure a parent disposition states for a
   figure several sub-issues move (Ready 4.2), message the parent-fixes session, once
   every sub-issue is merged, to capture them on its branch rebased onto the parent branch, check them as `build` step
   8 says, and merge as step 8 says; then judge. When every sub-issue this run builds is merged, start the
   `done-judge` agent by name with the Agent tool; it carries its own definition
   ([`../../agents/done-judge.md`](../../agents/done-judge.md)), tools and model. Give it the
   path to the plugin's
   `references/` folder, the parent card and spec path, each sub-issue's card and spec path,
   the profile path, the base revision (the integration branch commit the parent branch was
   cut from or last rebased onto), the parent branch's head, and a clean checkout at that
   head, made as a worktree of the repository (`git worktree add --detach`) so it reads the
   same gate records, never how the work was built.
   - A finding that belongs to one sub-issue goes by message to that sub-issue's kept
     session, which fixes it on its branch, rebased onto the parent branch. A finding no
     single sub-issue owns goes by message to the parent-fixes session. If that session is
     gone, send it to the kept session of the sub-issue whose files the finding touches
     most, naming the parent's spec as the one it fixes against. No session is started for
     a finding.
   - Each fix is reviewed by its change reviewer and merged as step 8 says; a finding that
     is a readiness miss gets a gap entry through `grill` in amend mode. Judge again once
     the findings are merged.
   - After a NOT DONE there are at most two further rounds. When the third judgment is
     still NOT DONE, sort its findings by the decision line's "Findings after the review
     limit". When every finding is on the developer's side, have them fixed as above and
     carry on without asking: after a code fix, review and judge once more; when every fix
     is a spec-only amendment, say so in the message to each session, so it amends the spec
     and reports without a review, then merge it as step 8 says and go straight to step 10,
     with no further judgment. Escalate to the requester, and wait, only
     with findings that change what an observer sees or can do, what persisted data ends
     up as, or scope, or when the extra judgment is still NOT DONE.
   - On DONE, or when a spec-only round past the limit is merged, have an agent fire
     `done` for the parent and for each nested parent in it.

10. **Accept.** Go straight into `accept` for the parent run once the Done judge says DONE,
    or once step 9 sends a spec-only round on; ask nothing first. `accept` runs in this
    session, under this coordinator's marker and its own, and does every command through
    a session or a subagent. It ends in the release: when step 1 noted a release
    authorised ahead of time, or the requester's acceptance authorises it, start `release`
    without asking again; otherwise `accept` asks once, and on a yes start `release`
    yourself, never on your own judgment. A refusal `accept` sorts as a defect or a request
    change is built as step 9's findings are: by the kept session of the sub-issue it
    belongs to, or by the parent-fixes session when no sub-issue owns it, reviewed and
    merged the same way, and then goes back to `accept`.

11. **Stop.** Once `release` has reaped, confirm that every session you started, the
    parent-fixes session included, is marked completed and archived, and that every agent
    you started has stopped, each having stopped its own. Report anything you cannot
    confirm: a session not archived, a worktree kept, a branch not deleted. Run `devfactory markers --clear-stale`
    to remove any marker left behind past its lifetime, then run `devfactory end
    coordinate`.

## Throughout

- **Events.** The run moves no card on the board; it fires the events in
  [`../../references/events.md`](../../references/events.md), and the project's hooks move
  cards as the project wants. The coordinator is answerable for every event in the run,
  whoever fires it: a hook failure a session or agent reports is reported to the
  requester with its output, and the work carries on. The parent closes only when every
  one of its sub-issues is released.
- **Progress.** Report to the requester at each phase: what is running, what is done, what
  is waiting and on what. A report asks nothing.
- **Work no card asks for.** Work found along the way that no card asks for becomes a
  standalone card through `create-card`, never a new sub-issue of this parent.
