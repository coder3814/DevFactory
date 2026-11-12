---
name: curate
description: Read the project's gap records, the ledger of released specs' gaps and every live spec's record, group the misses by the Ready or Done condition that let them through, test every standing answer and curated profile line for retirement, classify each proposal as plugin-general, the developer's side of the decision line, a profile section, a project document or a standing answer, drop what the plugin, the project's documents or the profile already hold or the requester has declined, and put the writes and retirements in one numbered question, writing to the profile only what the requester accepts, recording what they skip and reporting plugin defects and decision-line misses without writing them. Use after a release, or when the requester asks what the gap records show.
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
proposals, so the next grilling asks up front what this run had to ask mid-build, and it
keeps the profile from building up: most findings belong in the plugin, on the developer's
side of the decision line, or in a document the project already keeps, and only what is
left is written to the profile. It writes no profile entry, and retires none, that the
requester has not accepted.

**Who reads what.** A standing answer works only through a reader that reads it: the
readiness checker reads Standing answers (its step 2), and every skill tests a question
against them before asking it, as "Before anything is asked" in `decision-line.md` says.
The change reviewer reads only the profile's test gate and environments, and the Done judge
only its test gate. A rule meant to change a review, a Done judgment or how any skill or
agent works belongs in the plugin, never in Standing answers.

`devfactory` below means running the plugin's script with `python`: the script is
`${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`; if that variable is empty in your shell, it
is `../../scripts/devfactory.py` relative to this skill's folder.

**Markers.** Run `devfactory begin curate` as your first action and
`devfactory end curate` as your last, including when you stop to ask the requester or to
report, and `devfactory begin curate` again when you resume. A marker expires after the
profile's Marker lifetime (12 hours by default), and `begin` refreshes it. Markers and the
profile are found at the repository (worktree) root, wherever the shell's working
directory is.

The requester is asked one question per curation pass, as step 7 says, and nothing else;
before it, every proposal passes "Before anything is asked" in
[`../../references/decision-line.md`](../../references/decision-line.md) and step 5's
filter, so a proposal the plugin, the project's own records or the profile already settles
never reaches them.

## Read these first, in full

- [`../../references/spec-template.md`](../../references/spec-template.md): the gap entry's
  form.
- [`../../references/definition-of-ready.md`](../../references/definition-of-ready.md) and
  [`../../references/definition-of-done.md`](../../references/definition-of-done.md): the
  conditions entries name.
- [`../../references/decision-line.md`](../../references/decision-line.md).
- [`../../references/profile-template.md`](../../references/profile-template.md): the gap
  ledger, Standing answers and the rule for when a question becomes one, Declined proposals,
  and that the profile records only departures from the defaults and may point to where the
  project already records something.
- The project's own records, for the filter and the retirement test: the recorded decisions
  the profile names, the project instructions (`CLAUDE.md` and any it includes), and the
  project's skills under `.claude/skills/`.

## Steps

1. **Load the profile** with `devfactory profile`, read from the integration branch's head
   so that another run's committed curation counts, with the project's Standing answers,
   Declined proposals and Proposals awaiting an answer. An entry awaiting an answer is
   another run's curation under way, whatever worktree it runs in, unless it is older than
   the profile's Marker lifetime, when that run is taken as abandoned and the entry no
   longer counts.

2. **Collect every gap entry** by reading the files themselves: the project ledger
   `.devfactory/gaps.md`, which holds every released spec's entries prefixed with its card's
   id, and each live `gaps.md` under the profile's specs path on the integration branch. Keep each entry's card, its stage and
   its date, and its request types: from the ledger heading for a released entry, from
   the spec header for a live one.

3. **Group them** by the condition named in "Let through by", and within each condition by
   stage, and by request type. Note any entry still open.

4. **Test for retirement.** Before drawing anything new, test every standing answer, and
   every profile line a curate or release pass wrote (the profile's history says which),
   against four triggers:
   - the installed plugin now states its rule, in a skill, an agent or a reference;
   - a recorded decision, the project instructions or a project skill records it;
   - a code identifier or figure it names has changed, which you confirm in the code;
   - the condition it answers can no longer arise.

   Each entry a trigger meets is a retirement proposal, naming the trigger and where its
   substance now lives, or that it no longer applies.

5. **Draw the proposals**, each resting on the entries that support it: checker emphasis,
   a condition that let through more than one entry, with the request types it let them
   through for; a question asked and answered; a missing project fact; and a question that
   was really the developer's call. Then classify each by the first of these tests that
   holds:
   1. **Plugin-general.** It would hold on a project with a different tracker, no mock-ups
      and no production; or it changes how a plugin skill, agent or condition behaves; or
      the reader it targets does not read Standing answers, as "Who reads what" says.
      Write nothing to the profile. Report it as a plugin defect naming the plugin file and
      section and stating the rule in general terms, with no project case in it.
   2. **The developer's side of the decision line.** Answering it changes nothing an
      observer sees or can do, nothing persisted data ends up as, and not the scope.
      Report it as a decision-line miss, with what already answered it (a recorded
      decision, the profile, a pattern in the code, a delegation), and write nothing.
   3. **A profile section.** It is a project fact the profile template has a section for (an
      environment, the test gate, an owner-step type, data access, a convention), and the
      profile does not hold it. Propose it for that section.
   4. **A project document.** It governs the deployed system or the product, or it is a
      procedure the project's recorded decisions, project instructions or project skills
      already own. Name that document and propose the change there; `curate` does not edit
      it.
   5. **A standing answer.** Only what remains: a question on the requester's side,
      answered the same way on two separate occasions. Separate occasions are separate runs
      or separate questions; several entries recording one event count once. Checker
      emphasis that survives the first test is reported, not written: the readiness checker
      reads the ledger and every live gap record itself.

   Then drop every proposal already settled or under way: one whose substance the plugin,
   the recorded decisions, the project instructions, a project skill or the profile already
   holds; one Declined proposals records, sent to the plugin or declined by the requester;
   and one another run is asking now, which Proposals awaiting an answer records. A proposal
   is matched in substance, not by its wording: "write a page-cost test for each page" and
   "every page gets a cost test" are one proposal.

6. **Report**: the count per condition, then the retirements, then each remaining proposal
   numbered with its class and its entries, the writable ones (classes 3 and 5) first.
   Plugin defects, decision-line misses and checker emphasis are reported and not asked
   about. Record each plugin defect under Declined proposals as "sent to the plugin", with
   the date and the run or card, so it is not proposed again; this is the pass's own
   record, written in step 7's commit, or on its own when step 7 asks nothing.

7. **Ask once.** When any retirement or any class 3, 4 or 5 proposal remains, first list each
   under the profile's Proposals awaiting an answer with the date and the run or card it
   follows, and commit that on its own on the integration branch, so a run curating at the
   same time drops them. Then ask one question covering them all: which numbers to carry
   out and which to skip, with your recommendation for each and a one-line reason.
   Recommend writing a class 3 or 5 proposal, recommend each retirement, and recommend
   skipping a class 4 proposal for this question, with the document named, since the change
   belongs there and `curate` does not make it. Offer one option that carries out every
   recommendation, never "write every one" when the proposals' classes differ. Ask nothing
   when none remains. On the answer:
   - write each accepted class 5 proposal to Standing answers, and each accepted class 3
     proposal to the section it belongs in, as the rule alone with one short citation of
     the card numbers it came from, such as "(#1088, #1096)"; quotes, spec versions,
     commit ids and dates stay in the gap ledger and git;
   - delete each accepted retirement's entry outright, leaving no pointer, and name in the
     commit message where its substance now lives;
   - record each skipped proposal or retirement under Declined proposals with the date, the
     run or card it was proposed after, and the requester's words.

   Remove this pass's entries from Proposals awaiting an answer in the same change, and
   commit it on its own on the integration branch, so the next curation reads it.
