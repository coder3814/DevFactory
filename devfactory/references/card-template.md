# Card template

The skeleton of a card, for an agent to fill in or a person to copy, laid out as
the defaults place it: the title, then one description holding every other part.
Where the profile's board section moves a part into another field, leave it out
of the description and write it there: under its heading if the field holds
other parts, without it if the part is alone in the field. Each prompt in italics
says what the section holds; replace it, and delete any section marked *(when
there is any)* that has nothing to say. Where such a section stays, drop the
marker from its heading. Treat the parts marked *(on a sub-issue only)* and
*(on a parent issue only)* the same way: delete each on any other card, and drop
the marker where it stays. The rules for each part are in its module, listed in
[`card-standard.md`](card-standard.md).

---

## Title

*A small, pithy, direct phrase naming the change, in words this card's
stakeholder would recognise. Not a sentence. No problem, no method.*

## Description

*(On a sub-issue only)* *One line naming the parent issue.*

### Summary

*Two short sentences: what the system should do once the change is in and what
that produces, naming the requester where known and clear; then how things stand
today. No detail, no status.*

### The issue or request

*Today, … — a few plain sentences on what prompts the change: the cause
(confirmed or suspected), or the current state and why it falls short; for a
request, the need and why it matters. Point to evidence in attachments, and in
comments once the card exists, by name; do not reproduce it.*

### What needs to be achieved *(when there is any)*

*Only context or a worked example the criteria need to be clear. What, never
how. Does not restate the criteria.*

### Scope *(when there is any)*

*Only what a reader would otherwise get wrong: what they would assume is
included but is not, or the reverse, and where it is tracked if known.*

### Supporting information *(when there is any)*

- *A rule, constraint, decision already taken, or definition the work would
  otherwise miss — each stating what is true or must hold.*

### Open questions *(when there are any)*

- **The question, in full.** *What it affects. Options, where
  known.*

### Acceptance criteria

- **C1.** *The outcome, one checkable declarative sentence each of something
  true once the change is in: the result and the values and conditions that
  decide it, not every label, the steps of a test, values that only illustrate
  it, or a sub-list. Where another card or document defines the values, name it.
  Cover what the card asks for, not edge cases. If one depends on an open
  question, mark it provisional and name the question.*
- **C2.** *Each criterion keeps its ID for the life of the card. A removed ID is
  never reused; a new criterion takes the next number above the highest the
  card has ever carried. Never renumber.*

*On a parent issue, only what the combined result shows beyond its sub-issues'
criteria; never that every sub-issue is done, merged, reviewed or passing the
tests together. With nothing beyond them, one line saying so.*

### Work order *(on a parent issue only)*

1. *Sub-issue — waits on nothing, or on which sub-issue and why: needs its
   result, changes the same files, or both need something only one session can
   hold at a time. May run alongside which sub-issues.*

### Suggested model and effort

*The model, then the effort level (Low, Medium or High), in one line; then a
short reason drawn from the work.*

## Additional fields *(when the profile names any)*

- *Field — the value its team module recommends, and the one-line reason.*
