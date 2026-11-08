# Working a card

The steps every card skill shares. The rules they apply are in
`card-standard.md` (what a good card is) and `card-process.md` (how a card is
created and changed); this file says how an agent carries those out.

## Load the project profile

Read the project profile, `.devfactory/profile.md` at the project's root, as
`profile-template.md` beside this file describes, with every team module its
board section names, from `.devfactory/modules/`. Read the binding the profile's
board section names, such as `bindings/azure-devops.md` beside this file, and
reach the tracker exactly as that section's access entry says. The plugin's script reads
the profile the same way the hooks do: `profile` prints it, and `profile --field <name>`
prints one entry, run as `node ${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.js`.

If the project has no profile, touch no tracker: tell the user, and offer to run
`configure-project` first.

## Read a card

Read the whole card before judging it: every field the profile writes a part
to, every additional field it names, every comment with its date and author, the
names of its attachments, the column it is in on the profile's board, whether
it is a parent issue or a sub-issue and of which parent, as the binding says to
read it, the spec line if it has one, and the related data any team module
names. Note the highest criterion ID the card has ever carried, from its
criteria, its comments and, where the tracker keeps one, its revision history;
`criteria-ids --card <n>` lists the IDs the criteria carry now. A card
written before the profile, or under an earlier one, may hold a part in another
rich-text field, such as an acceptance criteria field: read every rich-text
field that holds content, and take each part from wherever it is. Note each
rich-text field's current format before writing to it. When you write a part
that sits in a field other than its mapped one, move it to its mapped field and
clear the old one.

## Shape a draft

Gather what you need first. Research is for getting the card right — confirming
how things stand today, finding related cards, checking a claim — not material
for the card. Put in only what a reader needs to agree on the outcome and to
check it, and leave the rest of what you found out. However much you were given
at creation, curate it into the description and acceptance criteria and attach
any files provided; none of it is posted as a comment.

Then re-read `card-standard.md`, its modules and `card-template.md`, so the rules
are fresh when you write rather than remembered from before the research, and
shape the card from the template. Check each section against its module's rules,
and hand the card to the reviewer only once you believe it meets the standard.
Give every criterion its stable ID as the acceptance criteria module says,
keeping each existing ID with its criterion, and run `criteria-ids --text <file>`
on the draft, which fails on a duplicate ID. Write the suggested model and
effort for the card as it now stands, and on a parent issue the work order, with
the tracker's sub-issue order set to match it when the card is written. On a
sub-issue, open the description with the line naming its parent.
Your own check earns the handoff; it is not the verdict.

Once the card's parts are shaped, apply each team module in the profile to the
card as a whole, with the related data it names: write a free-text team field to its module's rules, and for a
field with set values recommend one, with a one-line reason, from its module's
"Choosing a value".

## Measure

Start the `card-reviewer` agent by name with the Agent tool. It carries its
whole brief, its read-only tools and its own model, so pass no model and no
brief. Give it the full paths to `card-standard.md` and the project profile and
its team modules, and the card's full content — each part with the field it is in or
will be written to, each team field's value, the related data any team module
names, whether the card is a parent issue or a sub-issue and of which parent,
for a parent issue its sub-issues in the tracker's order, and for a draft, the
names of the files to be attached; for an existing card, the card's current column and
whether folding applies to it — always yes for a restructure, which folds
whatever the column — and for a rewrite, also any comments you will post with
it, the criteria with their IDs as they stand on the card now, and the highest
criterion ID the card has ever carried. The reviewer only
reads and changes nothing. Never measure a card you drafted yourself; the
reviewer is always a separate agent.

A review is one of two kinds, and you tell the reviewer which:

- **Fresh:** the reviewer gets the current card and nothing about earlier
  reviews.
- **Follow-up:** the reviewer also gets the previous review's report and the
  version of the card that review measured.

The review returns its verdict, the breaches it found, the questions that need
the user, and suggestions. Then:

1. The first review is fresh. If it finds no breach and no question, the card
   passes as it stands, and is ready for acceptance.
2. Otherwise ask the user every question the review raised, as "Grill"
   describes. Fold the answers in, and fix each breach by removing or narrowing
   text, or by restating a criterion more generally, wherever that closes it;
   add text only when nothing else does. Take or
   leave each suggestion.
3. Send it to one follow-up review. Whatever that still finds, report it to the
   user at acceptance; do not start another round.

There are no further reviews: the user decides on anything the follow-up still
finds. Keep the suggestions you left, for the user at acceptance.

## Grill

Ask the user about each gap the review found, one question at a time, until the
card has what it needs. Ask before anything goes to another review: another
review never closes a gap only the user can fill. Each question is specific and
answerable: what you need to know, and why the card needs it. Do not invent an
answer or fill a gap with an assumption; where the user does not know, the gap becomes an open question on the
card.

Whether each answer is recorded as a comment depends on where you are in the
process — see the skill you are running.

## Fold

Before folding an addition into an existing card, check the card's column
against the profile's fold columns. Outside them, follow "Where folding happens"
in `card-process.md`: the addition stays recorded, you tell the user the card is
in a column where folding does not happen, and they decide whether to fold it
anyway or raise a new card. Record a decision not to fold as a comment, naming
any new card. Restructuring folds whatever the column, and so does a settled
addition.

Fold the same way in either mode; the mode changes only what follows the fold,
as "Accept" says. Rewrite the affected sections so they say what the card asks for now: new
information to the section it belongs in, an answered open question out of open
questions and into the sections it changes. Where a new case lands in a
criterion, prefer restating the criterion more generally to adding a clause for
it. Keep every criterion's ID with it: never renumber, never reuse a removed
ID, and give a new criterion the next number above the highest the card has
ever carried. Never append a change or its date. Revise the work order when
sub-issues are added, removed or reordered, and the suggested model and effort
when the card no longer fits it. Then apply again each team module whose
field the change could affect.
If new information would widen the scope beyond the request, it enters only if
the requester agrees; if you do not know whether they do, ask the user.

## Accept

What happens here depends on the update's mode, interactive or settled, which
whoever asked for the update names, as "Updating a card" in `card-process.md`
says. Interactive is the default, and creating or restructuring a card is always
interactive.

In interactive mode, show the user what you propose to write, in full in the
conversation — the whole card when creating it, with the files to be attached,
and the rewritten sections when changing one, with any comments to be posted
with them, and each team field's value with its reason — and ask them to accept
it or ask for changes. Where the skill you are running measures the card, give
the verdict, anything the follow-up review still found, and the suggestions you
left. Write nothing to the card's parts or team fields until they accept.
Requested changes are folded in; where the skill you are running records
additions as comments, a requested change that carries new information is
recorded first. Requested changes do not reopen the review: show the changed
card to the user again.

In settled mode the requester has already answered — a grilling question, a
question relayed during a run, or an acceptance not given — and that answer is
the acceptance: record it as the comment, write the fold without asking, verify
it, then report the folded text to the requester as done, with the verdict and
anything the review still found where the skill measures the card, and say they
may object. An objection is a new addition: record it and fold it like any
other.

If the card's scope looks like several separately deliverable changes, or a file
might not be suitable to attach, say so and let the user decide; neither is
yours to decide.

## Write and verify

Write exactly what the user accepted, or in settled mode the fold the
requester's answer accepted. Anything that must change on the way goes
back to the user to accept again before it is written. Write each part to the
field the profile maps it to — parts that share a field in the standard's order,
each under its heading, and a part in a field of its own without its heading —
and each team field to its field. Write each field in its own format, then read
the card back and confirm that
every write landed as intended: the revision moved, where the tracker keeps one, each field holds what you
wrote in the format you meant, each comment and attachment is present. Report
anything that did not land rather than assuming it did.

## Re-derive the spec

If the card has a spec, follow "The spec" in `card-process.md` once the writes
are verified. When a part of the card changed, run the `grill` skill's
re-derivation for the conditions the changed part feeds, or for the whole spec
when the interface determination or a scope boundary changed, so the spec is
re-stamped with the card's new revision, and report to the user what changed in
the spec. When only a comment was added and no part changed, do nothing to the
spec. A card with no spec has nothing to re-derive. When the caller passes
`no-rederive`, as `grill` does because it is already deriving the spec, skip
this step.

Never write the spec line: `grill` writes it directly, as "The spec line" in
`card-standard.md` says.
