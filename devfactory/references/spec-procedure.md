# Spec procedure

The passages `grill` and `check-ready` both carry out, stated once. Each skill points here by
heading and keeps no copy. `devfactory` below means running the plugin's script with
`python`: the script is `${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`, or
`../scripts/devfactory.py` relative to this file's folder.

## The criteria file

The scripts that check criteria take them as a file of IDs, one per line. Write it with
`devfactory criteria-ids --card <n>` into a file outside the repository; a non-zero exit
means a duplicate criterion ID, a breach of the card standard: stop work on that card and
send it back to request grilling, as the request gate in `grill` does.

## The card revision

A card's revision is what `devfactory stamp --card <n>` prints, never a hash you compute or
a reading of the card. For a card the script cannot read with `gh`, write its text to a file
as "The stamp" in [`spec-template.md`](spec-template.md) lays it out (the title on the first
line, then the body, then each other field the profile writes a part to) and pass
`--text <file>` in place of `--card <n>`.

## Dispatching the checker

First run `devfactory spec-lint <spec dir> --criteria <file>` on every spec the check covers,
and fix every finding it reports before going on. A parent card has no spec, so nothing is
linted for it. Then start the `readiness-checker` agent by name with the Agent tool; it
carries its own definition, tools and model, so pass no model. Pass every input its Inputs
section lists:

- the path to the plugin's references folder (the folder this file is in);
- the repository path, the branch to read and its head commit: the integration branch
  before development, the card's own branch during it;
- for each card checked, its ID, its current text as the tracker holds it, its revision
  as "The card revision" says, and its stage, which is the point the work is at (Grilling
  before approval, Development during a build), never its board column; for a parent issue,
  the parent card and every sub-issue, saying which are released;
- each spec folder path (a sub-issue's or a standalone card's; a parent has none), and the
  profile path;
- the gap sources to read first: the project ledger `.devfactory/gaps.md` and every live
  `gaps.md` under the profile's specs path, a parent's records folder included;
- the moment: at creation, or at development start;
- the kind: **fresh**, with nothing about earlier checks; **follow-up**, with the fresh
  check's report and the spec version it measured, re-checking those findings and the
  changed text only; or **re-derive**, with the conditions this re-derivation re-runs.

The checker's report names the branch head it read. That commit is the stamp's Repo commit
and the ready receipt's `--commit`.

## The review rule

The readiness checker measures a spec once fresh, then at most once in a follow-up.
Whatever the follow-up still finds goes to the requester; there is no third check, because a
fresh checker finds something different every time and repeated rounds never converge.
Never measure a spec yourself.

## Asking the requester

A question first passes "Before anything is asked" in [`decision-line.md`](decision-line.md):
a standing answer that settles it is followed and cited, and one on the developer's side is
delegated, not asked. Ask one question at a time. Each question says what you need to know
and why the spec needs it, gives the options, and puts your recommendation first with a
one-line reason. When several cards share a gap, ask for the rule once, not the case per
card. Never invent an answer. A question the requester cannot answer yet stays open in your
report and keeps the spec `drafting`; it is never written onto the card.

## Folding an answer

An answer that leaves the card as it is (edge behaviour the card leaves to the tests, an
owner step's moment, a choice between ways of delivering the same outcome) goes into the
spec section it settles, and only there. An answer that would change the card takes the
route "A card-changing answer" gives.

## A card-changing answer

An answer the requester has given that would change the card (its outcome, what needs to be
achieved, a criterion, its scope or the work order) is never written into the spec as an
amendment. It goes onto the card through
`add-to-card` in settled mode, as "Settled mode" in that skill says, with the requester's
words and the question they answer; the requester's answer is the acceptance. Then `grill`
Re-derive brings the spec along, given the changed parts. When the answer came after the spec
had earned Ready, Re-derive is also given the question, the stage the work is at, the
condition that let it through, written `Ready <id>` or `Done <id>`, and whether the requester
changed their mind rather than answered a miss, and it writes the gap entry. For a parent
card, the specs brought along are those of the sub-issues the change touches, and the gap
entry goes in the parent's records folder.

## The ready receipt

Write the ready receipt after a check found the spec Ready, or once the requester settled
everything it found, and at no other time. List, one per line, the folder of every spec the
check measured, and run `devfactory receipt write <dir> --check ready --specs <file>
--commit <commit>`, where the commit is the branch head the checker reported reading and
`<dir>` is the folder of the card the check was run for. For a parent's set, `<dir>` is the
parent's records folder, `<specs path>/<parent id>/`, and `--parent <parent id>` is added (on
a tracker `gh` does not reach, `--parent-text <file>` with the parent card's text in the form
"The stamp" in [`spec-template.md`](spec-template.md) gives). Compare a receipt with
`devfactory receipt check <dir> --check ready --specs <file>`, with the same `--parent` for a
parent's set; `receipt check` takes no `--commit`.

## Landing a commit

A spec folder, or a file of a parent's records folder, is committed on its own, and nothing
else with it. Before development the commit lands directly on the integration branch when
the profile's Branches and merging allows a direct commit there; otherwise it is made on a
branch that is then fast-forwarded onto the integration branch, which the git guard allows
under `grill`'s marker. During development it is made on the card's own branch.
