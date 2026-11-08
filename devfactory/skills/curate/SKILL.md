---
name: curate
description: Read the project's gap records, the ledger of released specs' gaps and every live spec's record, group the misses by the Ready or Done condition that let them through, and propose checker emphasis, standing answers, missing profile entries and decision-line misses, writing to the profile only what the requester accepts. Use after a release, or when the requester asks what the gap records show.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(node *devfactory.js *)
  - Bash(git log *)
  - Bash(git show *)
  - Bash(git ls-tree *)
---

# Curate the gap records

Every question asked after Ready, every refused acceptance and every Done-check miss is a
gap entry naming the condition that let it through. Curating turns those entries into
proposals, so the next grilling asks up front what this run had to ask mid-build. It writes
nothing the requester has not accepted.

`devfactory` below means `node "${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.js"`, the script
in the plugin's `scripts/` folder.

**Markers.** Run `devfactory begin curate` as your first action and `devfactory end curate`
as your last, including when you stop to ask the requester or to report.

The requester is asked one question at a time, the recommended option first with a
one-line reason.

## Read these first, in full

- [`../../references/spec-template.md`](../../references/spec-template.md): the gap entry's
  form.
- [`../../references/definition-of-ready.md`](../../references/definition-of-ready.md) and
  [`../../references/definition-of-done.md`](../../references/definition-of-done.md): the
  conditions entries name.
- [`../../references/decision-line.md`](../../references/decision-line.md).
- [`../../references/profile-template.md`](../../references/profile-template.md): the gap
  ledger, Standing answers and the rule that a question answered twice becomes one.

## Steps

1. **Load the profile** with `devfactory profile`, and the project's Standing answers.

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

5. **Report the proposal**: the count per condition, then each proposal with its entries.

6. **Ask about each write.** For each proposed standing answer and missing profile entry,
   ask whether to write it. On acceptance, write a standing answer to the profile's
   Standing answers with where it came from, and a profile entry to the section it belongs
   in. Checker emphasis and decision-line misses are reported, not written: the readiness
   checker reads the ledger and every live gap record itself.
