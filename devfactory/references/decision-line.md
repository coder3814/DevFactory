# The decision line

Who decides what, stated once. The readiness checker uses it to tell a question grilling
must ask from one it may delegate; the build session uses it to decide instead of asking;
the coordinator uses it to send back a question the session could have answered.

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

## Recording a delegated call

A developer who makes a call on its side of the line records it in the spec's
delegated-decisions log (laid out in [`spec-template.md`](spec-template.md)), one line each:
the call, the choice, the reason. The Done judge reads the log to ground every decision in
the work ([`definition-of-done.md`](definition-of-done.md), condition 4.1).

A question that survives the line and the spec's delegations is a readiness miss. It goes to
the coordinator as the question, the options, a recommendation and the Ready condition that
failed, and its answer becomes a spec amendment and a gap entry.
