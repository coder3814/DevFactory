# Definition of Request

**The purpose of a request is to state the whole outcome the change must achieve, with every
answer already in it, so that a spec can be written from it without changing it.** The card
is the request. It is the only statement of scope: the spec may ask for nothing beyond it
(Definition of Ready condition 3.4), and specification grilling never changes it, so a gap in
the request is a gap the change will carry.

A card meets the **Definition of Request** when both hold:

1. **It meets the card standard**, [`card-standard.md`](card-standard.md) with every module
   it lists: the `card-reviewer` agent finds no breach and no question for the user.
2. **It has no open question.** Every answer the request needs is in it.

The three definitions follow the work in order: the Definition of Request for the card, the
Definition of Ready ([`definition-of-ready.md`](definition-of-ready.md)) for its spec, and the
Definition of Done ([`definition-of-done.md`](definition-of-done.md)) for the built change.

## Where it is worked and where it is checked

**Request grilling** brings a card to this definition. It is the questioning in
`create-card` and `re-evaluate-card`: it asks the user every question the card reviewer
raises and every open question on the card, one at a time, until none is left, as "Request
grilling" in [`working-a-card.md`](working-a-card.md) says. A question the user cannot answer
yet stays on the card as an open question, and the card does not meet the definition until it
is answered.

**Specification grilling**, the `grill` skill, checks it first, every time it starts work on a
card, new or re-derived: when the card's request receipt matches, the card is unchanged since
a reviewer found it meets the definition and the check is already made; otherwise it starts
the `card-reviewer` on the card as it stands. It goes on only when the card meets the
definition. The check is the gate, not where the card sits on the
board.

Specification grilling never changes the card. When drafting the spec turns up a question
whose answer would change the card — its outcome, a criterion, its scope or its work order —
the request was not complete: the requester's answer is folded into the card through
`add-to-card`, as "Settled mode" in that skill says, and specification grilling carries on
from the changed card. A question whose
answer only settles how the request is delivered, such as edge behaviour, an owner step's
moment or a delegated call, is answered into the spec alone.

## Where the card sits

This definition never reads the board. A card is worked and checked wherever it sits, and the
plugin moves no card between columns. When a skill has measured a card that has no spec line
and found that it meets the definition, that skill fires the `request-met` event
([`events.md`](events.md)), whether or not it changed the card; a project can use the event
to move the card to whatever column it keeps for complete requests.
