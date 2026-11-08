# Agents

The four files here are self-contained agent definitions: each carries its character,
inputs, procedure, rules, report format and checklist inline. A skill starts one by its
`name` with the Agent tool and puts every input the definition lists in the prompt; nothing
else briefs it.

- `card-reviewer` measures one card against the card standard; started by `create-card`
  and `re-evaluate-card` in their Measure step.
- `readiness-checker` applies the Definition of Ready; started by `grill` and
  `check-ready`.
- `change-reviewer` applies Definition of Done conditions 1 to 5 to one card's change;
  started by `build`.
- `done-judge` applies the whole Definition of Done to a parent branch; started by
  `coordinate`.

Each agent's frontmatter fixes its own `model` and its `tools`: all four run on `opus`
with read-only tools (`Read, Glob, Grep, Bash`, Bash for read commands and the plugin's
check commands only), and the skill that starts one passes no model. A card's Suggested
model and effort sets the model of a build session, never of these agents.

The readiness checker, the change reviewer and the Done judge decide every `[machine]`
condition by running the `scripts/devfactory.js` command the definition names for it and
quoting its output. They decide by reading only the conditions tagged `[judgment]` or
`[rubric]` and the few each definition lists under "Machine conditions without a script
yet". The card reviewer's measure is the card standard alone.
