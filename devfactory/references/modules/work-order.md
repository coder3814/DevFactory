# Work order

A core module of the [card standard](../card-standard.md).

## Holds

On a parent issue only: its sub-issues in the order to work them, each saying
what it waits on and which others may run alongside it. It comes after the
acceptance criteria and before the suggested model and effort.

## Rules

Every sub-issue of the parent appears once, in the order to work them, and the
tracker's sub-issue order matches it.

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
added, removed or reordered, it is revised, and the tracker's sub-issue order is
set to match.

## Examples

A work order that meets the standard:

1. #101 Export format — waits on nothing. May run alongside #102, #103 and
   #105.
2. #102 Export settings page — waits on nothing. May run alongside every other
   sub-issue.
3. #103 Scheduled export — waits on nothing. May run alongside #101, #102 and
   #104.
4. #104 Export history — waits on #101: needs its result, the stored export
   format. May run alongside #102, #103 and #105.
5. #105 Export audit — waits on #103: the two change the same files. May run
   alongside #101, #102 and #104.

| A wait that misses | Under the standard |
|---|---|
| #104 waits on #101, which is riskier. | #104 waits on #101: needs its result, the stored export format. |
| #102 waits on #101, to keep things simple. | #102 waits on nothing. May run alongside #101. |
| #105 waits on #103. | #105 waits on #103: the two change the same files. |
