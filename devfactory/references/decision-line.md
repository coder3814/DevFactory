# The decision line

Who decides what, stated once. The readiness checker uses it to tell a question grilling
must ask from one it may delegate; the build session uses it to decide instead of asking;
the coordinator uses it to send back a question the session could have answered; and every
skill that asks the requester anything applies it first, as "Before anything is asked"
says.

**The requester decides** what an observer of the system sees or can do; what persisted data
ends up as; and scope.

**The developer decides** internal structure; anything a recorded decision, the profile, a
design system or an existing pattern in the code already answers; and anything the spec
delegates.

**When several cards or sub-issues share a gap, ask for the rule, not the case.** One answer
that settles every instance is asked once; the same question asked per card is a checker
miss.

## Examples

| The requester's | The developer's |
|---|---|
| Where a form lands after save. | Whether a lookup is a constant or a table. |
| The wording of a message a user sees when an action fails. | The names of internal types, functions and files. |
| Whether existing records are converted to the new shape, left as they are, or removed. | How the conversion is batched and in what order it runs. |
| Whether an export is part of this card or a later one. | Following the list-paging pattern the code already uses elsewhere. |
| What happens when a user submits the same action twice. | A choice a recorded decision already makes, which is followed, not asked. |
| A limit a user can reach, such as the most items a list shows. | A limit no observer can reach or notice, such as an internal buffer size. |

A question on the requester's side that a recorded decision, the profile or the spec already
answers is not asked either: the answer is followed and cited.

## Before anything is asked

Every question any skill would put to the requester, a go-ahead included, first goes
through two tests, in this order. This holds for request grilling
([`working-a-card.md`](working-a-card.md), "Request grilling") as much as for every other
question:

1. **The profile's Standing answers.** When an entry answers it, act on that answer and
   cite the entry; nothing is asked.
2. **This line.** When the question is on the developer's side, decide it, log it as below,
   and carry on; nothing is asked.

Only a question on the requester's side that neither settles reaches the requester. A
skill also asks nothing it does not need an answer to: a go-ahead for the next step the
skill already prescribes, such as starting acceptance once the Done judge says DONE, is
not asked. The stops that remain are these:

- a question about what an observer of the system sees or can do, what persisted data ends
  up as, or scope;
- an owner step whose moment has arrived, such as a production write, which only the
  requester takes;
- the acceptance itself;
- the release, unless the requester has already authorised it, as `accept` and `release`
  say;
- a change review or Done judgment that still fails after the one extra round that
  "Findings after the review limit" allows;
- the profile writes `curate` proposes, asked once per curation.

## Findings after the review limit

A change review or a Done judgment that still fails after its two further rounds is not
by itself a reason to ask. A finding is on the developer's side when fixing it changes
nothing an observer sees or can do, nothing persisted data ends up as, and not the scope:
a missing or weak test, an incomplete evidence record or sidecar, a gap entry not
written, or a spec that no longer matches the built code while the behaviour it describes
is unchanged. When every finding is on the developer's side, it is fixed and the work
carries on. A code fix gets one more review. Carrying on without a further review is
allowed only when each fix is a spec amendment made through `grill` and
`devfactory spec-only <spec dir> --base <the failed revision>` prints `spec-only`. The
report then says, in these words, "no review passed this revision", lists the last
review's findings and their amendments, and never says the card passed. Each fix records
its gap entry as usual. A finding that changes what an observer sees or can do, what
persisted data ends up as, or scope goes to the requester, with the rest of that round's
findings.

## Recording a delegated call

A developer who makes a call on its side of the line records it in the spec's
delegated-decisions log (laid out in [`spec-template.md`](spec-template.md)), one line each:
the call, the choice, the reason. The Done judge reads the log to ground every decision in
the work ([`definition-of-done.md`](definition-of-done.md), condition 4.1).

A question that survives the line and the spec's delegations is a readiness miss. It goes to
the coordinator as the question, the options, a recommendation and the Ready condition that
failed, and its answer becomes a spec amendment and a gap entry.
