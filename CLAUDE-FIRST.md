# Claude Code-first contracts

Binding for every author in this wave. The owner decided on 2026-11-07 that DevFactory is
designed for Claude Code alone; portability to another agent system is not a goal. These
contracts fix the interfaces several files share so authors working in parallel agree.

## Runtime

- Node, standard library only, no package install. Every script runs as
  `node <plugin>/devfactory/scripts/devfactory.js <command> ...`. Inside a hook or skill the
  plugin path is `${CLAUDE_PLUGIN_ROOT}`; a skill may also say "the plugin's `scripts/`
  folder". Scripts exit 0 on success, 1 on a failed check (findings on stdout, one per line,
  as `<code> <message>`), 2 on usage or environment error (stderr).
- Markers: `<cwd>/.devfactory/.active/<skill>` holds an ISO timestamp. `begin` writes it,
  `end` removes it. The hooks treat any marker in that folder as "a card skill is running".
  `configure-project` adds `.devfactory/.active/` to `.gitignore`.

## Script commands (`scripts/devfactory.js`)

| Command | Does | Exit |
|---|---|---|
| `stamp --card <n> [--repo owner/name]` | Reads the card with `gh issue view <n> --json title,body`, drops every line matching `^Spec: .+ @ [0-9a-f]+$`, normalises line endings to LF, trims trailing LFs, hashes `title + "\n" + body` with SHA-256, prints the lowercase hex. `--text <file>` hashes a file (first line title, rest body) instead, for tests and Azure DevOps. | 0 |
| `stamp-check --card <n> --spec <dir>` (or `--text <file>`) | Compares `stamp` with the Card revision row in `<dir>/spec.md`; prints `match` or `changed <old> <new>`. Also checks the stamped Repo commit is an ancestor of HEAD in cwd (`git merge-base --is-ancestor`) and prints `ancestor` or `not-ancestor`. | 0 match+ancestor, 1 otherwise |
| `spec-lint <dir> [--criteria <file>]` | Checks `spec.md`: header rows present (Card, Version, Status, Card revision, Repo commit, Stamped, Request type(s)); status one of drafting, Ready, approved; every required section heading present in order; dispositions table has no blank Disposition cell; evidence plan has a row per criterion ID given in `--criteria` (one ID per line) and no row for an unknown ID; owner-steps rows have a Moment; amendments table has at least one row; `gaps.md`, if present, parses. | 0 clean, 1 findings |
| `criteria-ids --card <n>` or `--text <file>` | Prints the criterion IDs found (`C<n>` at the start of a criterion line) and fails on a duplicate, a gap is fine. | 0 / 1 |
| `gaps add <dir> --stage <s> --question <q> --condition <c> [--resolved <v>]` | Appends an entry to `<dir>/gaps.md` in the spec template's format with today's date. | 0 |
| `gaps check <dir>` | Fails if any entry has `Resolved by: open`. | 0 / 1 |
| `gaps ledger <dir> --card <n> --types <t> --ledger <file>` | Appends every entry of `<dir>/gaps.md` to the ledger with heading `## <card> (<types>) — <date> — <stage>`. | 0 |
| `evidence-check <dir> --criteria <file>` | For each ID, `evidence/<ID>/` exists, is non-empty, and every artifact has a `<name>.txt` sidecar whose single line has `revision:`, `checkpoint:` and `produced by:`. | 0 / 1 |
| `begin <skill>` / `end <skill>` | Marker write/remove in `<cwd>/.devfactory/.active/`. `begin` lists any other marker present with its age. | 0 |
| `profile [--section <heading>] [--field <name>]` | Prints the profile (`<cwd>/.devfactory/profile.md`) or one `- Name: value` field by name, so hooks and skills read it the same way. | 0 / 2 |

## Hooks (`hooks/hooks.json`, scripts in `hooks/`)

| Event | Matcher | Script | Behaviour |
|---|---|---|---|
| PreToolUse | Bash | `guard-tracker.js` | If the command contains a tracker write (`gh issue edit`, `gh issue comment`, `gh issue create`, `gh project item-edit`, `gh project item-add`, `gh api` with `-X PATCH|POST|PUT|DELETE` on `/issues`, `az boards work-item update|create`, `az boards work-item relation`) and no marker exists, deny with reason "DevFactory: card writes go through the card skills (create-card, add-to-card, re-evaluate-card, grill); none is running." Otherwise allow. No profile → allow. |
| PreToolUse | Bash | `guard-git.js` | If the command is `git push`, or `git merge`/`git merge --ff-only`/`git rebase` whose target is the profile's integration branch or a branch matching the profile's parent-branch pattern (run from that branch's worktree), and no `release` or `coordinate` marker exists, deny with reason naming the skill. No profile → allow. |
| UserPromptSubmit | — | `stamp-notice.js` | If the prompt contains `#<n>` or `card <n>` and `<specs path>/<n>/spec.md` exists, run `stamp-check` and print one line: "DevFactory: card <n>'s spec is current (Ready at <commit>)" or "DevFactory: card <n> changed since its spec earned Ready; run grill re-derive before building." Never blocks. |
| SessionStart | — | `session-context.js` | If `<cwd>/.devfactory/profile.md` exists, print: the profile path; the lifecycle stages and their columns; "use create-card / add-to-card / re-evaluate-card for cards, grill for specs, coordinate for a parent issue, build for one card, accept, release"; the decision line in one sentence; and whether any marker is active. Under 25 lines. |

Hook input is the JSON Claude Code sends on stdin (`tool_name`, `tool_input.command`,
`prompt`, `cwd`, `session_id`). A PreToolUse deny is the JSON
`{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"..."}}`
on stdout with exit 0. Context for UserPromptSubmit is the JSON
`{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"..."}}`; for
SessionStart plain stdout with exit 0 is enough. Every hook exits 0 and prints nothing when it has nothing to say, and never throws:
a malformed input or a missing file is silence, not an error.

## Agents (`agents/*.md`)

Frontmatter: `name`, `description`, `tools` (a list), `model`. Reviewers and judges:
`tools: Read, Glob, Grep, Bash` and `model: opus`. The card reviewer becomes an agent,
`agents/card-reviewer.md`, carrying the whole of `references/card-reviewer.md` inline; that
reference is deleted and every pointer to it moves to the agent. Skills start agents by name
with the Agent tool. A skill that starts an agent passes the card's Suggested model and
effort only for build sessions; agents keep their own `model`.

## Skills (`skills/*/SKILL.md`)

Frontmatter may use `allowed-tools` (pre-approve the reads the skill makes, such as
`Bash(gh issue view *)`, `Bash(gh project item-list *)`, `Bash(git log *)`, `Bash(node *devfactory.js*)`), `disable-model-invocation: true` for `release`. Every card
and spec skill calls `begin <skill>` as its first action and `end <skill>` as its last,
including on the path where it stops to ask. Every `[machine]` condition is checked by the
script named in the definitions, never by reading. The coordinator names the desktop
session tools directly (`start_session`, `SendMessage`, `stop_session`,
`archive_session`) and the runtime file is folded into it and deleted.

## Decisions taken during the build

- `context: fork` is not used: a forked skill cannot start agents or ask the requester, which is what `check-ready` and `curate` do.
- `release` has `disable-model-invocation: true`, so `accept` and `coordinate` end by asking the owner to run it; pushing stays the owner's word.
- The agents' README moved to `references/agents.md`, because plugin validation treats every file in `agents/` as an agent.

## Verified facts (code.claude.com, 2026-11-07)

- The manifest is `devfactory/.claude-plugin/plugin.json`; skills, agents and `hooks/hooks.json`
  are discovered by folder. `claude plugin validate ./devfactory` is the check.
- `hooks/hooks.json` needs the `hooks` wrapper; `${CLAUDE_PLUGIN_ROOT}`, `CLAUDE_PROJECT_DIR`
  are exported to hook processes. Stdin always has `session_id`, `cwd`, `hook_event_name`;
  PreToolUse adds `tool_name`, `tool_input`; UserPromptSubmit adds `prompt`; SessionStart
  adds `source`.
- A PreToolUse deny is the JSON above with exit 0; exit 2 with stderr also blocks; exit 1
  does not block.
- Agent frontmatter: `name`, `description`, `tools` (comma-separated), `model` (`opus`,
  `sonnet`, `haiku`, `inherit`). Plugin agents ignore `hooks`, `mcpServers`,
  `permissionMode`.
- Skill frontmatter: `allowed-tools` applies to the invoking turn only; `context: fork` with
  `agent`; `disable-model-invocation`; `user-invocable`; `model`; `effort`.
- Plugins cannot ship permission rules: `configure-project` writes them to the project's
  `.claude/settings.json` under `permissions.allow`, or a PreToolUse hook returns `allow`.

## Profile additions (`.devfactory/profile.md`)

- `## Hooks`: `- Tracker guard: on|off`, `- Git guard: on|off`, `- Stamp notice: on|off`,
  `- Session context: on|off`. Default all on. A hook reads its own line and exits silently
  when off.
- `## Permissions`: the allowlist entries `configure-project` writes to
  `.claude/settings.json` in the project (read commands only).
- The Sessions `Runtime` line is removed; the coordinator needs the Claude desktop app and
  says so.
