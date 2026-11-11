---
name: curate
description: Read the project's gap records, the ledger of released specs' gaps and every live spec's record, group the misses by the Ready or Done condition that let them through, drop what the profile already holds or has declined, and propose checker emphasis, standing answers, missing profile entries and decision-line misses in one numbered question, writing to the profile only what the requester accepts and recording what they skip. Use after a release, or when the requester asks what the gap records show.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(python *devfactory.py*)
  - Bash(git log *)
  - Bash(git show *)
  - Bash(git ls-tree *)
---

# Curate the gap records

Every question asked after Ready, every refused acceptance and every Done-check miss is a
gap entry naming the condition that let it through. Curating turns those entries into
proposals, so the next grilling asks up front what this run had to ask mid-build. It writes
nothing the requester has not accepted.

`devfactory` below means running the plugin's script with `python`: the script is
`${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`; if that variable is empty in your shell, it
is `../../scripts/devfactory.py` relative to this skill's folder.

**Markers.** Run `devfactory begin curate` as your first action and
`devfactory end curate` as your last, including when you stop to ask the requester or to
report, and `devfactory begin curate` again when you resume. A marker expires after the
profile's Marker lifetime (12 hours by default), and `begin` refreshes it. Markers and the
profile are found at the repository (worktree) root, wherever the shell's working
directory is.

The requester is asked one question per curation pass, as step 6 says, and nothing else;
before it, every proposal passes "Before anything is asked" in
[`../../references/decision-line.md`](../../references/decision-line.md) and step 4's
filter, so a proposal the profile already settles never reaches them.

## Read these first, in full

- [`../../references/spec-template.md`](../../references/spec-template.md): the gap entry's
  form.
- [`../../references/definition-of-ready.md`](../../references/definition-of-ready.md) and
  [`../../references/definition-of-done.md`](../../references/definition-of-done.md): the
  conditions entries name.
- [`../../references/decision-line.md`](../../references/decision-line.md).
- [`../../references/profile-template.md`](../../references/profile-template.md): the gap
  ledger, Standing answers and the rule that a question answered twice becomes one, and
  Declined proposals.

## Steps

1. **Load the profile** with `devfactory profile`, read from the integration branch's head
   so that another run's committed curation counts, with the project's Standing answers
   and Declined proposals. When `devfactory begin curate` lists another live `curate`
   marker, another run is curating now: wait until that marker is gone, then load the
   profile again, so the two passes never ask the same proposal.

2. **Collect every gap entry** by reading the files themselves: the project ledger
   `.devfactory/gaps.md`, which holds every released spec's entries prefixed with its card's
   id, and each live `gaps.md` under the profile's specs path on the integration branch. Keep each entry's card, its stage and
   its date, and its request types: from the ledger heading for a released entry, from
   the spec header for a live one.

3. **Group them** by the condition named in "Let through by", and within each condition by
   stage, and by request type. Note any entry still open.

4. **Draw the proposals**, each resting on the entries that support it:
   - **Checker emphasis**: a condition that let through more than one entry, and the request
     types it let them through for, so the readiness checker applies it harder there.
   - **Standing answers**: a question answered twice, in substance, across entries or runs,
     with the answer as given and the entries it came from.
   - **Profile entries missing**: a question whose answer is a project fact the profile has
     a section for (an environment, the test gate, an owner-step type, a convention) and
     does not hold.
   - **Decision-line misses**: a question that was really the developer's call, with the
     side of the line and what already answered it (a recorded decision, the profile, a
     pattern in the code, a delegation).

   Then drop every proposal already settled: one whose substance the profile already holds
   (a standing answer, a profile entry, or a rule in the section it would go to), and one
   the requester has declined, which Declined proposals records. A proposal is settled in
   substance, not by its wording: "write a page-cost test for each page" and "every page
   gets a cost test" are one proposal. A declined proposal comes back only when entries
   dated after its decline support it, and then says so.

5. **Report the proposal**: the count per condition, then each remaining proposal with its
   entries, numbered, the writable ones (standing answers and missing profile entries)
   first. Checker emphasis and decision-line misses are reported, not written: the
   readiness checker reads the ledger and every live gap record itself.

6. **Ask once.** When any writable proposal remains, ask one question covering them all:
   which numbers to write and which to skip, with your recommendation for each and a
   one-line reason, and an option to write every one you recommend. Ask nothing when none
   remains. On the answer, write each accepted standing answer to the profile's Standing
   answers with where it came from, and each accepted profile entry to the section it
   belongs in; record each skipped one under Declined proposals with the date, the run or
   card it was proposed after, and the requester's words. Commit the profile change on its
   own on the integration branch, so the next curation reads it.
