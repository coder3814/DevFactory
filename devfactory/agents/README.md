# Agents

The three files here are self-contained agent definitions: each carries its character,
inputs, procedure, report format and checklist inline, and the skills start them by name.

- `readiness-checker.md` applies the Definition of Ready; started by `grill` and
  `check-ready`.
- `change-reviewer.md` applies Definition of Done conditions 1 to 5 to one card's change;
  started by `build`.
- `done-judge.md` applies the whole Definition of Done to a parent branch; started by
  `coordinate`.

The card reviewer is not here. Its instructions are
[`../references/card-reviewer.md`](../references/card-reviewer.md), a brief the card skills
hand to a generic read-only agent, as
[`../references/working-a-card.md`](../references/working-a-card.md) says. The card skills
were carried over from the card standard with that brief before this folder existed, and the
brief carries its own measure, the card standard, so a second copy here would be a second
source of truth.

No agent names a model. The skill that starts one passes the model and effort the card's
Suggested model and effort names, or the profile's default under Sessions when the card
names none.
