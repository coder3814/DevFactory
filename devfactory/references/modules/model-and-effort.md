# Suggested model and effort

A core module of the [card standard](../card-standard.md).

## Holds

On every card: the model and the effort level suggested for developing the
card, and why; on a parent issue, for the session that coordinates its run. It
is the card's last part: after the acceptance criteria, and on a parent issue
after the work order.

## Rules

One line names the model and the effort level, which is Low, Medium or High.
A short reason follows, drawn from the work: what about the change calls for
that model and that effort, such as the judgement it needs, how much of the
system it touches, or that it is mechanical. A reason that names only a size or
a label, rather than the work, misses. On a parent issue the work is
coordinating the run, such as how many sub-issues run at once and how their
waits interlock.

It reflects the card as it stands. Whenever the card changes, the suggestion is
checked against the card as it now is and revised if it no longer fits.

The card reviewer judges it by this module and by "Throughout the card" only.
Being required on every card, it is never text a reader does not need.

## Examples

| A suggestion that misses | Under the standard |
|---|---|
| High effort. | `<model>`, High effort. A correction to every stored record, needing judgement about which records each rule covers. |
| `<model>`, Medium. A medium-sized card. | `<model>`, Low effort. One wording change on one page, checked by eye. |
| `<model>`, High effort, because it is important. | `<model>`, Medium effort. A new report built from data the system already holds, with no new storage. |
