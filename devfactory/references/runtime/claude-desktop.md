# Runtime: Claude desktop sessions

The one runtime-bound file in the plugin. The `coordinate` skill says *what* it does with
sessions in neutral words; this file says *how* on the Claude desktop app, where a session
can start other sessions, message them, read their reports and stop them. A project chooses
this runtime in its profile. Another runtime is another file in this folder, written to the
same four actions, and nothing outside this folder changes.

## The four actions

| The skill says | On Claude desktop |
|---|---|
| Start a session for a card, briefed to wait | `start_session` with `initiation: "user_asked"`, a fresh context, its own worktree (`use_worktree: true`), the model and effort the card's **Suggested model and effort** names, and the brief below. Record the session's id and name the result returns. |
| Tell a waiting session to begin, or send it an answer | `SendMessage` to the session's `local_…` id, never its display name. |
| Read a session's report | Its final message arrives as a `<side-sessions-event>` note quoting the report's first 400 characters; read the rest from the card and the spec it updated, or ask the session to restate a part. Treat a report as a claim: check the branch, the spec and the card before acting on it. |
| Stop a session | `stop_session`, then `archive_session` once its worktree and branch are gone. |

## Constraints that shape the coordinator

- **Sessions start only on a turn the owner's own message began.** On a turn a
  notification began, a start is offered as a card that waits for a click, so a run left
  unattended stalls. The coordinator therefore starts every sub-issue's session up front,
  in the owner's turn, each briefed to reply "waiting" and end its turn until messaged to
  begin, and to rebase onto the current parent branch before starting.
- **Messaging works from any turn**, so the coordinator sets each session going when its
  waits are met, and relays answers, from a notification turn.
- **A session cannot remove the worktree it is working in.** The coordinator has a
  separate subagent remove it after the merge.
- **The coordinator runs nothing itself**, not even a `git` or `gh` command: every read,
  board move and change is a session's or a subagent's. Subagents suit reads, board moves
  and worktree clean-up; sessions suit the work the owner may want to open, steer or stop.
- **One coordinator per run.** The coordinator never starts a session that acts as a
  coordinator; a parent issue created along the way is a new run the owner starts.
- **Link every session you name** as `[title](#local_<id>)` so the owner can open it.
- **Stop and reap** every session and subagent you started before you finish.

## The build session's brief

The brief names the card, the parent, the spec path and the parent branch, and says, in
this order:

1. Reply "waiting" and end your turn. When messaged to begin, rebase onto the parent branch
   named here, then follow the `build` skill for this card.
2. Move the card to the development column as work starts; leave every other column move
   to the coordinator.
3. A question the spec and the decision line do not answer: stop and report it to the
   coordinator in the shape the `build` skill gives, and wait.
4. Do not merge until the coordinator says it is this card's turn; never merge into the
   integration branch; never push.
5. When told it is your turn: rebase onto the parent branch, rerun the tests, fast-forward
   the parent branch from the parent worktree, report, and end your turn. Stay available:
   you, your worktree and your branch are kept until the run is accepted and released, and
   the coordinator may message you with a Done-judge finding or an acceptance refusal.

## Notes a coordinator should know

- A session's note is its report, not proof: verify the diff or the spec before telling
  the owner it is done.
- Run commands likely to exceed about two minutes in the background.
- When the owner's message arrives mid-run about something else, answer it; the run
  continues on its own notifications.
