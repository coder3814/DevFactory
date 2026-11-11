# The card standard

What a good card looks like at any moment. How a card is created and changed over
time is not part of this standard; it lives in the skills that work with cards.

## Purpose

A card is the mechanism that tracks one change to the system through its life:
the request for it, its definition, the work, its validation and, where the
change has one, its deployment. What the card defines is the outcome the change
must achieve — the behaviour the system will exhibit and what that behaviour
produces — so that everyone working from it shares one understanding of the
goal. It prescribes the outcome, never the method of reaching it.

## Throughout the card

- Readable by anyone who uses it: the stakeholder, the business analyst, the
  developer, the QA tester, or an agent.
- Runs from general to specific, so a reader can stop once they understand
  enough and keep reading only for more detail.
- Conveys its information in the best explanation possible and as concisely as
  possible, trading neither for the other: a passage falls short if a reader
  would understand less from it, or if it could say the same in fewer words.
- Holds what its readers need to agree on the outcome and to check it, and
  nothing more. Text a reader does not need is a defect to remove, just as a gap
  is one to fill.
- Requires only what every card can supply. Everything else appears where it is
  known and a reader needs it.
- States the card's current state. The description and acceptance criteria
  carry no dates and no change log.
- Names code only when the change itself concerns that code. It never brings
  code in as background or as a pointer for whoever does the work.

## The parts of a card

A card is made of these parts, in this order. Each is a core module with its own
rules, in the file beside this one; read every module in full alongside this
file.

1. [Title](modules/title.md)
2. [Summary](modules/summary.md)
3. [The issue or request](modules/issue-or-request.md)
4. [What needs to be achieved](modules/what-needs-to-be-achieved.md)
5. [Scope](modules/scope.md)
6. [Supporting information](modules/supporting-information.md)
7. [Open questions](modules/open-questions.md)
8. [Acceptance criteria](modules/acceptance-criteria.md)
9. [Work order](modules/work-order.md), on a parent issue only
10. [Suggested model and effort](modules/model-and-effort.md)

Every module has the same shape: **Holds** says what the part carries, **Rules**
what it must and must not be, and **Examples**, where there are any, show the
rules applied.

## Where each part is written

The board section of the project profile, `.devfactory/profile.md`, described in
[`profile-template.md`](profile-template.md), says which field each part is
written to. By default:

- The title is written to the card's title field, always.
- Every other part is written to the card's description, in the order above,
  each under its own heading. The suggested model and effort is the
  description's last section, after the acceptance criteria and, on a parent
  issue, the work order.

A profile may move any part other than the title into another field, where
the board has one. Parts that share a field keep the standard's order, each
under its heading; a part alone in a field is written there without its
heading.
Where a part is written never changes its rules.

## Parent issues

A parent issue is a card whose outcome is that every one of its sub-issues is
done. It meets this standard like any other card, and carries a work order as
well. Each sub-issue opens its description with one line naming its parent,
before its summary. How a card is marked as a parent or a sub-issue on the
tracker is the profile's, in its board section and the binding it names.

## Team modules

The profile's board section may add fields to a team's cards, as many as the
team wants or none, each worked by a team module the team writes. A team module has the same
shape as a core module, and for a field with set values adds **Choosing a
value**: the allowed values and how to choose between them.

Team fields are the team's layer, not part of this standard. A team field is
judged by its own module; a free-text team field also follows "Throughout the
card". No team module changes a core module's rules.

## Attachments

Supporting files are attached to the card; existing files the card refers to may
simply be pointed to rather than copied onto it. Each attachment is referred to
by name in the section it supports, with a few words on what it shows. The description refers only to attachments
that reflect the card's current state.

## Comments

The dated record of every question, answer, discussion and change after the card
is created, including any stakeholder's verbatim words and where they came from,
and the evidence behind them. Nothing given when the card is created is recorded
here: it is curated into the description and acceptance criteria, and any files
are attached. The description and acceptance criteria carry whatever in the comments
changes the outcome, and never contradict them; nothing else in a comment is
restated on the card.

## The spec line

Once a card has a spec, the card carries exactly one line pointing at it, as the
last line of the description body, in the form `Spec: <path> @ <commit>`, where
the path is the spec folder's and the commit is the spec folder's own commit.
The line belongs to the spec, not to any part of the card. The `grill` skill
writes it directly, straight after committing the spec; that write is not an
addition, so no comment is recorded for it, and no other skill writes the line.
The card revision in the spec's stamp leaves out any line in this form, so
writing or updating it never makes the stamp stale. This standard does not
measure it.

## Why the standard is shaped this way

The owner made each of these choices when the standard was settled; they explain
rules that could otherwise be misread.

- **Outcome, not problem, is the card's centre.** The card prescribes the desired
  behaviour and outcome, in the behaviour-driven sense; the problem is context
  for it.
- **A card holds what its readers need, not everything known.** Being known is a
  reason to consider including something, not a reason to include it.
- **A card can close without being deployed,** especially when the change is not
  deployable, which is why the purpose says "where the change has one".
- **Titles are small, pithy and direct, not sentences.** Uniqueness against
  other titles is not a consideration.
- **Decision cards follow the same standard** rather than being a separate type.
- **The standard holds no splitting rule.** Whether to split is a person's
  judgement, made from the card's scope, never from its title.
- **The requester and the cause are included where known,** never required,
  because they may not be available or clear.
- **The summary is two short sentences,** the outcome and today, so a reader
  gets the point at a glance; the sections below carry the detail.
- **The summary never carries status.**
- **What is given at creation is curated, not recorded.** However much arrives,
  it shapes the description and criteria and its files are attached; comments
  begin with the first change after the card exists.
- **Stakeholder quotes never enter the description;** it carries only what in
  them changes the outcome, so it never carries dated entries.
- **Each part of the outcome is stated once, in the criteria,** apart from the
  summary. Prose appears only where a criterion needs context.
- **Each criterion is one declarative sentence.** It states a result and the
  conditions it depends on; the steps of a check and its cases belong to the
  tests.
- **Edge cases belong to the tests, not the card.**
- **Evidence lives in attachments and in comments on later changes;** the
  description points to it.
- **Code is named only when the change concerns it.** It is neither banned nor
  carried as background.
- **Open questions carry no "waiting on" or "asked yet" line.**
- **An open question carries its own dependencies.** Each is written once, on
  the question, rather than repeated in every part it touches. Only a dependent
  criterion keeps a short mark, because the criteria are judged on their own.
- **Every part is a module, and the core modules are fixed.** A team chooses
  where each part is written and adds fields of its own, but cannot change a
  core module, so the standard means one thing across teams.
- **Everything but the title defaults to the description,** because every card
  in every tracker has one. A dedicated field is a team's choice, never a
  requirement.
- **Team fields sit beside the standard, not in it.** The standard requires only
  what every card can supply; a team's fields are checked against the team's
  own module.
- **Provided files are attached; existing files may be linked.** Whether a file is
  safe or suitable to attach is the people's call, not the standard's.
- **Criteria carry stable IDs, never positions.** Work orders, comments, gap
  records and evidence cite a criterion long after the card is amended, so a
  removed criterion's ID is never reused and a new one takes the next number;
  renumbering would point every citation at the wrong criterion.
- **Every card suggests a model and effort.** Whoever starts a session to
  develop the card needs it, and the card is the handoff, so it is a core part
  rather than a team field. It is kept current as the card changes, and it is
  judged by its own module, never cut as text a reader does not need.
- **A parent issue carries its own work order.** The order and the waits are
  part of what its readers must agree on before any session begins work, so they live
  on the card. Sub-issues run in parallel by default, and only three reasons
  hold one back, so a wait is never a habit or a hunch.
- **A parent waits on another parent only for that parent's work.** Each
  parent's sub-issues merge into its own branch and it releases when they are
  done, so no other wait between parents is needed.
- **A parent issue is a card like any other.** Its outcome is that every
  sub-issue is done; each sub-issue names its parent in its opening line, so a
  reader of either knows the other exists. How the tracker marks the link
  differs by tracker, so it is the profile's.
- **The card points at its spec in one line and holds none of it.** The card
  stays small and outcome-shaped; everything a builder needs beyond that is in
  the spec, which development reads.
