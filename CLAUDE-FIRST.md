# Claude Code-first contracts

Binding for every author in this wave. The owner decided on 2026-11-07 that DevFactory is
designed for Claude Code alone; portability to another agent system is not a goal. These
contracts fix the interfaces several files share so authors working in parallel agree.

## Runtime

- Python 3, standard library only, no package install (the owner wants no Node dependency
  anywhere). Every script runs as `python <plugin>/scripts/devfactory.py <command> ...`. Inside a hook or skill the
  plugin path is `${CLAUDE_PLUGIN_ROOT}`; a skill says once that the script is
  `${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`, or `../../scripts/devfactory.py` relative
  to the skill's folder when that variable is empty in the shell. Scripts exit 0 on
  success, 1 on a failed check (findings on stdout, one per line, as `<code> <message>`), 2
  on usage or environment error (stderr).
- Repository root: the script and the hooks find `.devfactory/` (the profile, the markers,
  the gap ledger) at the repository (worktree) root of the working directory, wherever the
  shell's working directory is inside it.
- Markers: `<root>/.devfactory/.active/<skill>` holds an ISO timestamp. `begin` writes it,
  or refreshes it when it exists, and `end` removes it. The hooks treat any marker in that
  folder younger than the profile's `Marker lifetime` (default 12h) as "a card skill is
  running"; an older one counts for nothing. A skill that holds a marker across a wait runs
  `begin <skill>` again on resume. `configure-project` adds `.devfactory/.active/` to
  `.gitignore`.

## Script commands (`scripts/devfactory.py`)

| Command | Does | Exit |
|---|---|---|
| `stamp --card <n> [--repo owner/name]` | Reads the card with `gh issue view <n> --json title,body`, drops every line matching `^Spec: .+ @ [0-9a-f]+$`, normalises line endings to LF, trims trailing LFs, hashes `title + "\n" + body` with SHA-256, prints the lowercase hex. `--text <file>` hashes a file (first line title, rest body) instead, for tests and Azure DevOps. | 0 |
| `stamp-check --card <n> --spec <dir>` (or `--text <file>`) | Compares `stamp` with the Card revision row in `<dir>/spec.md`; prints `match` or `changed <old> <new>`. Also checks the stamped Repo commit is an ancestor of HEAD in cwd (`git merge-base --is-ancestor`) and prints `ancestor` or `not-ancestor`. | 0 match+ancestor, 1 otherwise |
| `spec-lint <dir> [--criteria <file>]` | Checks `spec.md`: header rows present with non-empty values (Card, Version, Status, Card revision, Repo commit, Stamped, Request type(s)); status set and one of drafting, Ready, approved; each request type one from the spec template's list; when the status is Ready, Card revision a SHA-256 hex and Repo commit a commit hash; every required section heading present in order; the dispositions table has a row for each of the five core concerns and no blank Disposition cell, a cell holding only the template's italic prompt counting as blank; the evidence plan has the six evidence columns, a row per criterion ID given in `--criteria` (one ID per line) and no row for an unknown ID; every owner-step row has a Moment; the amendments table has at least one row; `gaps.md`, if present, parses. | 0 clean, 1 findings |
| `criteria-ids --card <n>` or `--text <file>` | Prints the criterion IDs found (`C<n>` at the start of a criterion line) and fails on a duplicate, a gap is fine. | 0 / 1 |
| `gaps add <dir> --stage <s> --question <q> --condition <c> [--resolved <v>]` | Appends an entry to `<dir>/gaps.md` in the spec template's format with today's date. | 0 |
| `gaps check <dir>` | Fails if any entry has `Resolved by: open`. | 0 / 1 |
| `gaps ledger <dir> --card <n> --types <t> --ledger <file>` | Appends every entry of `<dir>/gaps.md` to the ledger with heading `## <card> (<types>) — <date> — <stage>`. | 0 |
| `evidence-check <dir> --criteria <file> [--base <rev>]` | For each ID, `evidence/<ID>/` exists, is non-empty, and every artifact has a `<name>.txt` sidecar whose single line has `revision:`, `checkpoint:` and `produced by:`; in a repository, every file there is committed as it stands, each sidecar revision is an ancestor of HEAD or a commit whose change a rebase carried into HEAD unaltered, and each checkpoint is one the criterion's evidence plan row names. With `--base`, a sidecar revision is stale when a code file changed from the base to HEAD differs between it and HEAD; the specs path, `.devfactory/` and the profile's Specs "Not code" paths are not code, and a revision at or before the base is exempt. | 0 / 1 |
| `begin <skill>` / `end <skill>` | Marker write (or refresh)/remove in `<root>/.devfactory/.active/`. `begin` lists any other marker present with its age. | 0 |
| `markers [--clear-stale]` | Lists each marker in `<root>/.devfactory/.active/` with its age and whether it is past the profile's Marker lifetime; `--clear-stale` removes those past it. | 0 |
| `profile [--section <heading>] [--field <name>]` | Prints the profile (`<root>/.devfactory/profile.md`); `--section` alone prints that section; `--field` prints one `- Name: value` field's value, within the section when both are given. The hooks read the profile through this command, so hooks and skills read it the same way. | 0 / 2 |

## Hooks (`hooks/hooks.json`, scripts in `hooks/`)

| Event | Matcher | Script | Behaviour |
|---|---|---|---|
| PreToolUse | Bash | `guard_tracker.py` | If the command contains a tracker write (`gh issue edit`, `gh issue comment`, `gh issue create`, `gh project item-edit`, `gh project item-add`, a `gh api graphql` mutation, a `gh api` call with `-f`, `-F`, `--input`, `--method` or a non-GET `-X`, `az boards work-item update|create`, `az boards work-item relation`) and no live marker of a card-writing skill exists (create-card, add-to-card, re-evaluate-card, grill, check-ready, build, coordinate, accept, release; a configure-project or curate marker does not unlock), deny with reason "DevFactory: card writes go through the card skills (create-card, add-to-card, re-evaluate-card, grill); none is running." Otherwise allow. No profile → allow. |
| PreToolUse | Bash | `guard_git.py` | Protects the profile's integration branch and every branch matching its parent-branch pattern. Blocks `git push`, and any change to a protected branch: a merge, fast-forward, rebase, hard reset or amend while HEAD is on a protected branch, or the same through `git -C` into a protected branch's worktree. A rebase or merge of a protected branch into an unprotected one is never blocked. A live `release` or `coordinate` marker allows everything; a `build` marker allows the fast-forward into a parent branch; a `grill` marker allows its spec commit and fast-forward onto the integration branch. A denial names the skill that would allow it. No profile → allow. |
| UserPromptSubmit | — | `stamp_notice.py` | For at most two cards the prompt names (`#<n>` or `card <n>`) whose `<specs path>/<n>/spec.md` exists and whose status is not drafting, run `stamp-check` and print one line each: "DevFactory: card <n>'s spec is current (Ready at <commit>)" or "DevFactory: card <n> changed since its spec earned Ready; run grill re-derive before building." Silent on a drafting spec. Never blocks. |
| SessionStart | — | `session_context.py` | If `<repository root>/.devfactory/profile.md` exists, print: the profile path; the lifecycle stages and their columns; "use create-card / add-to-card / re-evaluate-card for cards, grill for specs, coordinate for a parent issue, build for one card, accept, release"; the decision line in one sentence; and whether any marker is active. Under 25 lines. |

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
`Bash(gh issue view *)`, `Bash(gh project item-list *)`, `Bash(git log *)`, `Bash(python *devfactory.py*)`). Every card
and spec skill calls `begin <skill>` as its first action and `end <skill>` as its last,
including on the path where it stops to ask. Every `[machine]` condition is checked by the
script named in the definitions, never by reading. The coordinator names the desktop
session tools directly (`start_session`, `SendMessage`, `stop_session`,
`mark_completed`, `archive_session`) and the runtime file is folded into it and deleted.

## Decisions taken during the build

- `context: fork` is not used: a forked skill cannot start agents or ask the requester, which is what `check-ready` and `curate` do.
- `release` is model-invocable, but runs only on the requester's explicit word in the conversation: `accept` and `coordinate` ask whether to release and start it themselves on a yes, or start it without asking when the requester authorised the release ahead of time, in their starting instruction or their acceptance answer. `disable-model-invocation: true` was dropped because it refused the session's call even after the requester said to release. Pushing stays the requester's word inside `release`.
- The agents' README moved to `references/agents.md`, because plugin validation treats every file in `agents/` as an agent.
- Git guard semantics: the guard blocks pushes and changes to a protected branch (the integration branch or a parent branch), whether HEAD is on it or `git -C` points into its worktree; it never blocks a rebase or merge of a protected branch into an unprotected one. `release` and `coordinate` allow everything, `build` the fast-forward into a parent branch, and `grill` its spec commit and fast-forward onto the integration branch. So a build session fast-forwards with `git -C <parent worktree> merge --ff-only <branch>` from its own worktree, never by changing into the parent worktree, and `grill` holds its marker through its spec commit and spec line, ending it only after both. The spec commit lands directly on the integration branch when the profile's branching allows a direct commit, else on a branch fast-forwarded under `grill`'s marker.
- A coordinated build session runs `begin build` first, then rebases onto the parent branch, then follows `build`.
- Markers expire after the profile's `Marker lifetime` (default 12h), so a marker an interrupted skill left behind stops counting; `begin` refreshes a marker, and every skill that holds one across a wait runs `begin` again on resume. `markers --clear-stale` removes expired ones, from `configure-project`'s troubleshooting and `coordinate`'s final reap.
- The script and the hooks find `.devfactory/` at the repository (worktree) root, not the shell's working directory, and the hooks read the profile through the script's `profile` command.
- Skills pre-approve the script as `Bash(python *devfactory.py*)`, with no spaces around the name, and name it as `${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`, or `../../scripts/devfactory.py` relative to the skill's folder when that variable is empty in the shell.

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
  `- Session context: on|off`, `- Marker lifetime: <hours>h`. Default all on and 12h. A hook
  reads its own line and exits silently when off.
- `## Permissions`: the allowlist entries `configure-project` writes to
  `.claude/settings.json` in the project (read commands only).
- The Sessions `Runtime` line is removed; the coordinator needs the Claude desktop app and
  says so.
