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
| `request-met` | The skill has created or changed the card, it now meets the Definition of Request, and it has no spec line yet. A card with a spec has passed this hand-off already. | `create-card`, `re-evaluate-card` |
| `ready` | The spec is stamped Ready, committed, and the card's spec line written, by a new spec or a re-derivation before development. | `grill` |
| `approved` | The requester has approved the Ready spec and the status change is committed. | `grill` |
| `work-started` | Any work on the card begins, before any readiness or stamp check: at the start of a build session, and when a coordinator starts a parent issue run, before it settles readiness. | `build`, `coordinate` |
| `development-started` | A build session starts work on the card; for a parent issue, when its first sub-issue's session starts. | `build`, `coordinate` for a parent |
| `readiness-lost` | A card whose spec was Ready or approved is found not to be Ready: the build's status and stamp check fails; the readiness check at development start finds the card not Ready; or the card is changed, by any card skill, so that its spec no longer matches. | `build`, `check-ready`, `create-card`, `re-evaluate-card`, `add-to-card` |
| `done` | The card's change meets the Definition of Done: the change reviewer's PASS for a standalone card; for a sub-issue, its PASS once the coordinator has checked the report and merged it; the Done judge's DONE for a parent issue, and for each nested parent in it. | `build` for a standalone card, `coordinate` otherwise |
| `refused` | The requester refuses the card at acceptance, as a defect sent back to the build or as a request change. A refusal that becomes a new card is not one: this card is accepted as specified. | `accept` |
| `accepted` | The requester has accepted the card, and the acceptance is recorded. | `accept` |
| `released` | The card's change is released by the project's release procedure. | `release` |

For a parent issue and its sub-issues, each event fires once per card, for each card it
applies to: `approved` for the parent and every sub-issue the one approval covers;
`work-started` for the parent and every sub-issue the run covers, as the run starts;
`readiness-lost` for each card found not Ready, the parent included; `refused` for the card
that owns the refused criterion or outcome, and in a parent run for the parent as well;
`accepted` and `released` for each card accepted or released.

## Writing a hook

A hook is one file in `.devfactory/hooks/` at the repository root, named for its event, with
an extension that says how to run it: `ready.py`, `ready.ps1`, `ready.cmd` or `ready.bat`,
`ready.sh`, or `ready` with no extension for bash. The name is matched without regard to
case. A file of any other type is reported as a failed hook. It runs from the repository root, with the card ID as its
one argument and in the variables `DEVFACTORY_CARD` and `DEVFACTORY_EVENT`, for at most 300
seconds. Exit 0 means it worked.

A hook that moves a card writes to the tracker itself, with the tracker's own CLI and the
project's own column names; the plugin's tracker guard reads only the commands an agent runs,
so a hook's writes pass it. Example, for a GitHub project whose Ready specs wait in a column
named Queue:

    # .devfactory/hooks/ready.ps1
    param($card)
    gh project item-edit --project-id <project> --id (<item id for $card>) --field-id <Status> --single-select-option-id <Queue>
