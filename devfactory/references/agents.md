# Agents

The four files in `agents/` are the plugin's agent definitions: each carries its character,
inputs, procedure, rules, report format and checklist, and reads the references its Inputs
section names. A skill starts one by its `name` with the Agent tool, after reading that
definition's Inputs section (not the whole definition), and puts every input it lists in
the prompt.

- `card-reviewer` measures one card against the card standard and the Definition of
  Request. Started by `create-card` and `re-evaluate-card` in their Measure step, and by
  `grill` at its request gate. It reads `card-standard.md` and every module it lists,
  `definition-of-request.md`, and the profile's board section and team modules.
- `readiness-checker` applies the Definition of Ready. Started by `grill` and
  `check-ready`. It reads `definition-of-ready.md`, `decision-line.md` and
  `spec-template.md`, `modules/work-order.md` when the check covers a parent issue, the
  profile, and the gap ledger and every live gap record.
- `change-reviewer` applies Definition of Done conditions 1 to 5 to one card's change.
  Started by `build`. It reads `definition-of-done.md`, `decision-line.md`,
  `spec-template.md` and `test-gate.md`, and the profile's Test gate and Environments.
- `done-judge` applies the whole Definition of Done to a parent branch. Started by
  `coordinate`. It reads `definition-of-done.md`, `decision-line.md`, `spec-template.md`
  and `test-gate.md`, and the profile's Test gate.

Each agent's frontmatter fixes its own `model` and its `tools`: all four run on `opus`
with read-only tools (`Read, Glob, Grep, Bash`, Bash for read commands and the plugin's
check commands only), and the skill that starts one passes no model. A card's Suggested
model and effort sets the model of a build session, never of these agents.

The readiness checker, the change reviewer and the Done judge decide every `[machine]`
condition by running the `scripts/devfactory.py` command the definition names for it and
quoting its output. They decide by reading only the conditions tagged `[judgment]` or
`[rubric]` and the few each definition lists under "Machine conditions without a script
yet". The change reviewer and the Done judge also make the independent run of the full
test gate before a PASS or a DONE ([`test-gate.md`](test-gate.md), "The independent run").
The card reviewer's measure is the card standard alone.
