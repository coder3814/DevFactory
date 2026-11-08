# Title

A core module of the [card standard](../card-standard.md).

## Holds

The title is a small, pithy, direct phrase naming the change, in words that
card's stakeholder would recognise.

## Rules

It is not a full sentence. "The stakeholder" means that card's stakeholder — for
a design-system or development card that may be the developers, not the
business.

It does not need to distinguish the card from any other card's title.

It carries neither the problem nor the method. It reflects the card as it stands
and never decides the card's size or whether it is split.

A card whose outcome is a decision names the question while undecided and the
decision once decided.

## Examples

| A title that misses | Under the standard |
|---|---|
| Age is elapsed days over 365.25, so an employee is not 65 on their 65th birthday | Age on the birthday itself |
| An employee should turn 65 on their 65th birthday | Age on the birthday itself |
| Production retains no application logs, so no past error can be investigated | Retained production logs |
| The browser tests should run in a pipeline lane | Browser tests in the pipeline |
| Excluded Records drops every coverage column, and a name collision in its rename crashes the build | Coverage columns on Excluded Records |
| Whether sign-in should use tenant-wide admin consent | Tenant-wide admin consent? |
