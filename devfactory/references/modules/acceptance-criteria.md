# Acceptance criteria

A core module of the [card standard](../card-standard.md).

## Holds

What is true once the change is in: the card's own definition of done, distinct
from the plugin's Definition of Done, which judges a delivered result against it.

## Rules

The criteria are the outcome: each is one declarative sentence stating one thing
that is true once the change is in, specific enough to build to and to check —
named results and the real values they depend on, never "works correctly". The
real values are those that decide the result, not every label or literal the
change touches; where another card or document already defines them, the
criterion names it rather than repeating them. A criterion carries the
conditions its result depends on, but not the steps of a test that would show
it, values that only illustrate it, or a sub-list. One that needs more than
a sentence is two criteria, or is carrying detail that belongs to the tests.

The criteria cover the outcome the card asks for, not every situation it could
meet. Edge cases belong to the tests that land with the change.

Criteria describe what can be observed, not how it was built, unless the change
itself concerns specific code. A criterion that depends on an open question is
marked provisional, naming the question and nothing more, and stays so until it
is answered. Where a reader might expect an out-of-scope behaviour to change, a
criterion may state that it stays as it is. A criterion only a person can check
is fine, provided it says exactly what they should see.

A parent issue carries no criteria. A requirement only the combined result of
several sub-issues can show, such as a flow that crosses them, is a criterion on
the sub-issue that completes it, as "Parent issues" in the card standard says.

Each criterion opens with its stable ID: `C1`, `C2`, and so on. An ID stays with
its criterion for the life of the card, through every amendment: a criterion
restated, generalised or narrowed keeps its ID; a criterion split keeps its ID
on the part that carries its original outcome, and each new part takes a new
one; criteria merged into one keep one of their IDs and retire the rest. A
removed criterion's ID is never reused, and a new criterion takes the next
number, one above the highest the card has ever carried, so gaps in the
numbering are expected. Criteria are never renumbered. Anything that cites a
criterion — the work order, a comment, the spec, a gap or evidence — cites its
ID, never its position.

## Examples

| A criterion that misses | Under the standard |
|---|---|
| On the attached census, typing "Default jobs" into Occupation's Override and re-analyzing leaves Occupation with the mapping it had before, and that row says the census has no column headed "Default jobs". The row is not badged Corrected, and the Mapping Log does not record it as Corrected. | An Override that names no column in the census leaves the mapping unchanged and says so on its row, with no Corrected badge or Mapping Log entry. |
| On a row also marked Confirmed or Update, a pick from "this column belongs to a different field on this line" is either applied on re-analysis or that row says the pick was not applied and that its Confirmed or Update mark is why. | A different-field pick on a row also marked Confirmed or Update is either applied on re-analysis, or the row says its Confirmed or Update mark blocked it. |
| On that merged census, the mapping review shows the client's own headings in Matched to and offers them in Override, and Default Jobs (HR) can be assigned to Occupation. | The mapping review of a merged census shows and offers every client column under its own heading. |
