# Creating and updating a card

How a card is brought to, and kept at, the standard in
[`card-standard.md`](card-standard.md). The standard says what a good card looks
like at any moment; this process says how a card gets there and changes over
time. The two are deliberately separate.

## Creating a card

### From scratch

1. The user gives the agent the basic idea of the card, whatever information they
   can think of, and any links to files or file attachments.
2. If what the user gives holds more than one outcome, the agent proposes the
   set of cards, one outcome line each, and the user decides the set before any
   card is drafted.
3. The agent shapes each card into the card structure, checking each section
   against the standard, and hands the draft on only once it believes the draft
   meets the standard. Its research is for getting the card right, not material
   for the card.
4. A reviewer measures the draft once, fresh, including, when an existing card
   is restructured, any comments to be posted with it. Only a breach of the standard, or a question for the user,
   fails a card; anything that is a matter of judgement is a suggestion, which
   the agent may take or leave. This is request grilling: the agent asks the
   user every question the review raises and every open question on the card,
   as "Request grilling" in [`working-a-card.md`](working-a-card.md) says, and
   folds the answers in — what the user does not know yet stays an open question
   on the card, which keeps it short of the
   [Definition of Request](definition-of-request.md) — and fixes each breach, by removing or narrowing
   text wherever that closes it and adding text only when nothing else does. If
   the review passes the card, it is done. Otherwise one follow-up review checks
   the earlier findings and the changed text only. Whatever it still finds goes
   to the user with the card, at step 5, rather than into another round.
5. The user sees the whole card, with the verdict, anything the follow-up
   review still found, and the suggestions the agent left, and accepts it or
   asks for changes. Changes the user asks for are folded in and shown to them again; they do not reopen the review.
6. The card is created exactly as accepted, with any files provided attached.
   Anything that must change on the way goes back to the user to accept. When it
   meets the Definition of Request, the `request-met` event fires
   ([`events.md`](events.md)); the card is never moved by the agent.

Nothing gathered during creation is recorded as a comment; it goes straight into
the description and acceptance criteria, and any files are attached.

### From an existing card

The same steps from step 3, starting from the existing card's content. The card
is edited in place, never replaced by a new card.

Everything already on the card is treated as creation: it is reshaped into the
structure without being recorded as comments, and its criteria are written
afresh from the outcome rather than edited from the old ones. A card whose
criteria have no IDs yet is numbered from `C1`. Where they already carry IDs, a
rewritten criterion that carries an old one's outcome keeps that ID, the IDs no
longer carried are retired, and each new criterion takes the next number above
the highest the card has ever carried. Any question asked in request grilling,
and the user's answer, is a new addition, so it is recorded as a comment and then
folded in, as with any update.

## Updating a card

Once a card exists, every addition is recorded as a comment on the card, however
it arrives, and then folded into the description and acceptance criteria.

Every update is made in one of two modes, which whoever asks for the update
names:

- **Interactive**, the default: the addition is recorded and folded, the user
  sees the rewritten sections, and nothing is written to the card's parts until
  they accept them or ask for changes.
- **Settled**: the requester has already answered, and another skill hands the
  answer to `add-to-card`; "Settled mode" in that skill lists who does. The
  answer is recorded as the comment, folded and written without a further round
  on its wording, the write is verified, and the folded text is reported to the
  requester as done. The requester may object afterwards; an objection is a new
  addition, recorded and folded like any other.

So the user accepts the rewritten wording of every interactive addition, and a
settled answer is its own acceptance.

### Additions through an agent

Anything given to an agent for an existing card — an answer, new information, a
file — is recorded by the agent as a comment, with any file attached, and then
folded in. In interactive mode the user then accepts the rewritten sections or
asks for changes; in settled mode the fold is written and reported as done, as
above.

### Re-evaluating a card

An agent cannot tell when someone has changed a card directly, so re-evaluation
is a procedure in its own right rather than a reaction to an edit. It runs when
someone asks for it, and checks the card against the standard whatever has
changed on it and however. It is also how a parent issue that still carries
criteria, supporting information or a spec line is brought to "Parent issues" in
the standard, as the `re-evaluate-card` skill says. It takes no answer handed
over by another skill: that goes through `add-to-card`.

1. **Measure** the title, description and acceptance criteria against the
   standard, including whether they carry what in the comments changes the
   outcome and contradict none of them.
2. **Fold in** any comment whose outcome-changing content is missing. A comment a user added directly is
   already the record, so folding it adds nothing further.
3. **Request grilling.** Ask the user about any gap and any open question on the
   card, as "Request grilling" in `working-a-card.md` says. Their answers are
   new additions, so they are recorded as comments and then folded in.
4. **Measure again** with one follow-up review of the changed text; whatever it
   still finds goes to the user.
5. **Accept.** The user sees the rewritten sections, the verdict, anything the
   follow-up still found and the suggestions the agent left, and accepts them
   or asks for changes. Changes the user asks for are folded in and shown to them again; they do not reopen the review.

A direct edit to the card's details is not recorded by re-evaluation; the edit is
itself the change.

### Folding

In every case, folding means rewriting the affected sections to say what the card
asks for now — never appending the change or its date.

- New information goes to the section it belongs in.
- An answered question leaves open questions and lands where it changes the card.
- A new case in a criterion is preferably folded by restating the criterion more
  generally, not by adding a clause.
- Every criterion keeps its ID through the fold. A restated criterion keeps
  its ID; a removed one's ID is retired and never reused; a new one takes the
  next number above the highest the card has ever carried. Criteria are never
  renumbered, as the [acceptance criteria module](modules/acceptance-criteria.md)
  says.
- The work order is revised whenever sub-issues are added, removed or
  reordered, and the suggested model and effort whenever the card no longer
  fits it.
- Nothing beyond the request enters scope unless the requester agrees.

### Where folding happens

Everywhere. An addition is folded wherever the card sits on the board; no card
skill reads the card's column. A card that already has a spec is protected by
its stamp instead: the fold changes the card's revision, the spec is re-derived
for what the change feeds, and a build never starts on a spec whose stamp no
longer matches the card.

## The spec

A card may have a spec: the specification folder beside the code that
development reads, laid out in [`spec-template.md`](spec-template.md) and stamped
with the card revision it was derived from. Once a card has one, the card and
its spec change together. A parent issue never has one, as "Parent issues" in
[`card-standard.md`](card-standard.md) says.

- Every write to the card through a card skill is followed by re-deriving the
  spec for the conditions the changed part feeds, re-stamping it with the card's
  new revision, and reporting what changed in it. The `grill` skill does the
  re-derivation, which first checks the changed card against the Definition of
  Request. A caller that hands `add-to-card` an answer with `no-rederive` owns
  that re-derivation itself.
- The spec line is not an addition: `grill` writes it directly, as
  [`card-standard.md`](card-standard.md) says, and records no comment for it.
- A change to the interface determination or to a scope boundary re-grounds the
  whole spec, not only the conditions the changed part feeds.
- A comment that changes no part of the card changes nothing: the spec is
  neither re-derived nor re-stamped.
- A direct edit on the tracker, made outside the card skills, leaves the stamp
  behind the card, and the next check of the spec finds it and handles it the
  same way.

## Team fields

Wherever the card's content changes — when it is created, restructured or
folded — each team module in the profile's board section recommends its field's value
from the card as a whole, and from any related data the module names, with a
reason. The user accepts those values with the
rest of the card, and they are written only then.

## Left to people

- Whether a card should be split.
- Whether a file is suitable to attach.

## Why the process is shaped this way

The owner made each of these choices when the process was settled.

- **Recording starts once the card exists.** What is gathered at creation goes
  into the description and acceptance criteria, with files attached; none of it
  is recorded as a comment.
- **Restructuring an existing card splits old from new:** what the card already
  held is treated as creation; request grilling's questions and answers are
  recorded.
- **A user's own comment is not re-recorded** when it is folded in; recording it
  again would duplicate the record.
- **Re-evaluation runs on request,** not automatically before work starts or on a
  schedule; it is also the route that restructures a parent issue still
  carrying criteria, supporting information or a spec line.
- **An interactive update ends with the user accepting the rewrite,** because
  folding is the agent's interpretation of the user's words and is where meaning
  drifts.
- **The writer hands on only what it believes is done; the reviewer measures,
  and the user decides.** The writer's own check earns the handoff, not a
  verdict.
- **One fresh review, then at most one follow-up.** A fresh reviewer finds
  something different every time, so repeated fresh reviews never converge and
  each round adds text. What the follow-up still finds goes to the user.
- **Breaches are fixed by cutting first.** Removing or narrowing text resolves a
  breach as well as adding text does, and keeps the card from growing.
- **Only breaches and questions for the user fail a card.** A judgement call is
  a suggestion, so the card can reach a pass; the user sees the suggestions
  left untaken.
- **The user is asked before the next review.** A gap only the user can fill is
  never closed by another review.
- **Folding never depends on the board.** The plugin works a card wherever it
  sits, and a project moves cards by its own rules, through the events. A card
  being built is protected by its spec's stamp, not by a frozen column.
- **Team modules recommend; the user accepts.** A team module's value is a
  judgement on the card, so it goes to the user like any other rewrite.
- **The set of cards is settled before drafting,** so a split is the user's
  decision before any card exists, not a cleanup after large cards are written.
- **A settled answer is its own acceptance.** The requester has just said what
  they want, in their own words; a second round on the wording of the fold
  would stall the work for no new decision. The fold is reported as done, so
  drift is still caught, and an objection is folded like any other addition.
  Interactive additions keep the acceptance, because nothing there replaces it.
- **A card-changing answer takes one route.** Whichever skill receives it, it
  goes through `add-to-card` in settled mode and the spec is re-derived from the
  changed card, so every such answer is recorded and folded the same way.
- **Criteria keep their IDs through every fold.** What cites a criterion — a
  work order, a comment, a spec, a gap, evidence — must still point at the same
  criterion after the card changes.
- **The spec follows the card on every write.** A spec stamped against an old
  card is a spec development cannot trust, so each card skill re-derives what
  the change feeds and re-stamps, rather than leaving staleness for a later
  check to find. A change to the interface or a scope boundary moves too much to
  re-derive in part. A comment that changes no part leaves nothing to re-derive.
