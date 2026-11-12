# Events

The plugin moves no card between board columns. Instead, at each point where the work changes
hands, the skill that reached it fires an event, and a project that wants something to happen
then, such as moving the card to its own column, gives that event a hook. A project defines no
events and needs no hook at all: an event with no hook does nothing.

## Firing an event

A skill fires an event for each card it applies to with

    devfactory event <name> --card <id>

once the point is reached and written, never before. The command runs the project's hook if
it has one and prints what the hook printed. A hook that fails (`hook-failed`) never undoes or
holds back the work: the skill reports the failure to the user, with its output, and carries
on.

## The events

| Event | Fired when | Fired by |
|---|---|---|
| `request-met` | The card has been measured and found to meet the Definition of Request, and it has no spec line. Whether the skill that ran the measure changed the card does not matter. | The skill that ran the measure: `create-card`, `re-evaluate-card`, or `grill` at its request gate |
| `ready` | A spec is stamped Ready, committed, and its spec line written. For a parent issue, which has no spec: when every sub-issue is Ready and the set check at creation reports nothing open. | `grill` |
| `approved` | The requester has approved the Ready spec and the status change is committed; for the parent and each sub-issue the one approval covers. | `grill` |
| `work-started` | Any work on the card begins, before any readiness or stamp check: at the start of a standalone card's build session, and when a coordinator starts a parent issue run, for the parent and every sub-issue, before it settles readiness. | `build`, `coordinate` |
| `development-started` | A build session starts work on the card, or resumes it after a `readiness-lost`; for a parent issue, when its first sub-issue's session begins work. | `build`, `coordinate` for a parent |
| `readiness-lost` | A card whose spec was Ready or approved is left not Ready and the work on it has stopped, in one of three cases: a re-derive stops to wait for the requester, or ends with the status below what it was (`grill`); the build's status and stamp check fails and the session stops and waits (`build`); the readiness check reports the card not Ready and stops for the requester (`check-ready`). | `grill`, `build`, `check-ready` |
| `done` | The card's change meets the Definition of Done: the change reviewer's PASS for a standalone card; for a sub-issue, its PASS once the coordinator has checked the report and merged it; the Done judge's DONE for a parent issue, and for each nested parent in it. Past the review or judgment limit, a card whose last findings were all on the developer's side and fixed by spec-only amendments, which `devfactory spec-only` confirms, counts as Done (`decision-line.md`, "Findings after the review limit"). Fired again when a fix for a refused acceptance has been reviewed, merged and, in a parent issue run, judged again. | `build` for a standalone card, `coordinate` otherwise |
| `refused` | The requester refuses the card at acceptance, as a defect sent back to the build or as a request change. A refusal that becomes a new card is not one: this card is accepted as specified. | `accept` |
| `accepted` | The requester has accepted the card, and the acceptance is recorded. | `accept` |
| `released` | The card's change is released by the project's release procedure. | `release` |

`readiness-lost` fires on the outcome, never on the change that led to it. A card change
that is re-derived straight back to the status it had fires nothing, and the card skills
(`create-card`, `re-evaluate-card`, `add-to-card`) never fire it. It fires at most once per
stop. After a `readiness-lost`, the skill that brings the card back fires the event for
where the card now stands: `ready` when its status is Ready before development, `approved`
when its status is approved before development, or `development-started` when the build
resumes.

For a parent issue and its sub-issues, each event fires once per card, for each card it
applies to: `ready` for the parent once its whole set is Ready; `approved` for the parent
and every sub-issue the one approval covers; `work-started` for the parent and every
sub-issue the run covers, as the run starts; `readiness-lost` for each sub-issue left not
Ready; `refused` for the card that owns the refused criterion or outcome, and in a parent
run for the parent as well; `accepted` and `released` for each card accepted or released.

## Writing a hook

A hook is one file in `.devfactory/hooks/` at the repository root, named for its event, with
an extension that says how to run it: `ready.py`, `ready.ps1`, `ready.cmd` or `ready.bat`,
`ready.sh`, or `ready` with no extension for bash. The name is matched without regard to
case. A file of any other type is reported as a failed hook. It runs from the repository root, with the card ID as its
one argument and in the variables `DEVFACTORY_CARD` and `DEVFACTORY_EVENT`, for at most 300
seconds. Exit 0 means it worked.

A hook that moves a card writes to the tracker itself, with the tracker's own CLI and the
project's own column names; the plugin's tracker guard reads only the commands a session
gives its Bash and PowerShell tools, so a hook's writes, run by `devfactory event`, pass it. Example, for a GitHub project whose Ready specs wait in a column
named Queue:

    # .devfactory/hooks/ready.ps1
    param($card)
    gh project item-edit --project-id <project> --id (<item id for $card>) --field-id <Status> --single-select-option-id <Queue>
