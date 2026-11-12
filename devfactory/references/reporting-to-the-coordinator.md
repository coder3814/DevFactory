# Reporting to the coordinator

How a session in a parent issue run reports, asks and stops, and what the coordinator makes
of what reaches it. A session in the run is one the coordinator started, briefed to build a
sub-issue and kept until `release` reaps it. The coordinator is the session that started
it: its brief gives the coordinator's `local_…` id, and the session's own prompt names it as
the session that started it.

## By message

Every report, question and stop the session makes goes to the coordinator as a message it
sends with `SendMessage` to the coordinator's `local_…` id, never its display name. Load the
tool with `ToolSearch` first when it is deferred. Nothing else is a report: the final message
of a turn is not one, and neither is anything the desktop app relays when the turn ends.

Every question for the requester raised in the session goes to the coordinator this way,
whichever skill raises it: a question the build stops on, and a question a `grill`
Re-derive or Amend run in the session asks, its approval question included. The session
never asks the requester directly.

## What each report carries

**The first report** names the branch the session works on when it is not the branch the
brief names, as when the app started the session on another branch.

**A question** the session must stop on carries this shape, and the session then waits:

```text
Question: <what must be decided, and why the work needs it now>
Options: <each realistic option, and what it leads to>
Recommendation: <one option, and why>
Ready condition failed: <the condition that should have caught it, such as Ready 3.2>
```

**A stop** says why the work stopped and quotes what stopped it: the spec status and the
stamp check's output (`changed <old> <new>`, `not-ancestor`); a re-derive that stopped to
wait for the requester or left the spec below `approved`, with the status it left; the
findings past the review limit that change what an observer sees or can do, what persisted
data ends up as, or scope, each as the review gave it; or a fast-forward that refused, with
its output.

**The build report**, once the card is built and reviewed, carries:

- what was built, by criterion ID;
- the last review's verdict and how many rounds it took, with the reviewer's own run of the
  test gate and each test it named unstable;
- when the review limit was passed, each developer-side finding fixed without asking and
  whether a further review ran; when none ran, the words "no review passed this revision",
  the last review's findings and the amendment that answers each, and never that the card
  passed;
- the delegated calls made, from the spec's log;
- the gaps raised, with their amendments, and whether an amendment changes what another
  card depends on;
- the branch and the revision;
- anything left unverified.

**The merge report** carries the revision rebased onto, the gate's result after the rebase
(a printed record or a fresh run), and the parent branch's head after the fast-forward.

## Ending a turn

The session ends a turn only to wait for the coordinator, and only once the message is sent.
The turn's closing message is one line saying the report was sent; it repeats nothing of the
report.

## Waiting inside the turn

While the session waits on its own work, a reviewer it started or a command it runs in the
background, it keeps the turn open: a blocking foreground wait in slices under the shell's
limit, repeated until the result arrives. It never ends the turn to wait for a notification
of its own work.

## A turn-end note

The desktop app may relay a session's finished turn to the coordinator as a note. The
coordinator makes nothing of it: reports, questions and stops come by message only, and a
note is not acted on.
