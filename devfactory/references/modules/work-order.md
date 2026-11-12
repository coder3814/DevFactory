# Work order

A core module of the [card standard](../card-standard.md).

## Holds

On a parent issue only: its sub-issues in the order to work them, each saying
what it waits on and which others may run alongside it. It comes after the
purpose and before the suggested model and effort.

## Rules

Every sub-issue of the parent appears exactly once, in the order to work them,
named by its number only, never by its title or scope. The work order on the
card is the order: the tracker's own order of sub-issues is not kept in step
with it, and nothing judges it.

Sub-issues run in parallel by default, as many at once as the waits allow. One
waits on another only for one of three reasons, and each wait names the other
sub-issue and which reason it is:

- it needs the other's result;
- the two change the same files;
- both need something only one session can hold at a time.

No other reason is a wait. Each entry names the sub-issues that may run
alongside it, or says that none may.

A parent issue waits on another parent issue only for that parent's work: code
it builds on, or data its release must find already in place. The wait names
the other parent and is stated against the sub-issues it holds back. A
criterion it cites is cited by its ID. The wait is met once the code it waits
on is on the integration branch and the waiting parent's branch is rebased
onto it, found by the code's content, since a rebase changes commit ids;
nothing else about the other parent, such as where its card sits or whether it
is closed, holds the work back.

The work order reflects the sub-issues as they stand. Whenever sub-issues are
added, removed or reordered, it is revised.

## Examples

A work order that meets the standard:

1. #101 — waits on nothing. May run alongside #102, #103 and #105.
2. #102 — waits on nothing. May run alongside every other sub-issue.
3. #103 — waits on nothing. May run alongside #101, #102 and #104.
4. #104 — waits on #101: needs its result, the stored export format. May run
   alongside #102, #103 and #105.
5. #105 — waits on #103: the two change the same files. May run alongside
   #101, #102 and #104.

| An entry that misses | Under the standard |
|---|---|
| #104 waits on #101, which is riskier. | #104 waits on #101: needs its result, the stored export format. |
| #102 waits on #101, to keep things simple. | #102 waits on nothing. May run alongside #101. |
| #105 waits on #103. | #105 waits on #103: the two change the same files. |
| #102 Export settings page — waits on nothing. | #102 — waits on nothing. May run alongside every other sub-issue. |
