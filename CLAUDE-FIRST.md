# Claude Code-first contracts

Binding for every author of the plugin's files. The owner decided on 2026-11-07 that
DevFactory is designed for Claude Code alone; portability to another agent system is not a
goal. These contracts fix the interfaces several files share so authors working in parallel
agree. A contract `DESIGN.md` or `devfactory/scripts/README.md` already states is pointed to
here, not repeated.

## Runtime

- Python 3, standard library only, no package install (the owner wants no Node dependency
  anywhere). Every script runs as `python <plugin>/scripts/devfactory.py <command> ...`. Inside a hook or skill the
  plugin path is `${CLAUDE_PLUGIN_ROOT}`; a skill says once that the script is
  `${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`, or `../../scripts/devfactory.py` relative
  to the skill's folder when that variable is empty in the shell. Scripts exit 0 on
  success, 1 on a failed check (findings on stdout, one per line, as `<code> <message>`), 2
  on usage or environment error (stderr), an unknown flag included.
- Repository root: the script and the hooks find `.devfactory/` (the profile, the markers,
  the ledgers) at the repository (worktree) root of the working directory, wherever the
  shell's working directory is inside it.
- Markers: `<root>/.devfactory/.active/<skill>` holds an ISO timestamp and the plugin
  version it was written under. What `begin`, `end` and `markers` print is in
  `scripts/README.md`; what a marker allows, how it expires, the reload on `plugin-changed`
  and the same-command `begin` are in `DESIGN.md` section 8, "Markers" and "Hooks".
  `configure-project` adds `.devfactory/.active/` to `.gitignore`.

## Script commands (`scripts/devfactory.py`)

`devfactory/scripts/README.md` states every command, its flags, its output and its exit
codes, and `python devfactory/scripts/devfactory.py --help` prints the commands and their
flags. The commands are `stamp`, `stamp-check`, `spec-lint`, `criteria-ids`, `gaps add`,
`gaps check`, `gaps ledger`, `evidence-check`, `spec-only`, `reviews add`, `reviews show`,
`reviews ledger`, `receipt write`, `receipt check`, `begin`, `end`, `markers`, `profile` and
`event`. A
document that calls one uses the form the README gives, and a change to a command changes
the README, the `--help` text and the tests together.

## Hooks (`hooks/hooks.json`, scripts in `hooks/`)

| Event | Matcher | Script |
|---|---|---|
| PreToolUse | `Bash\|PowerShell` | `guard_tracker.py` |
| UserPromptSubmit | — | `stamp_notice.py` |
| SessionStart | — | `session_context.py` |

What each hook refuses, allows or prints is stated in `DESIGN.md` section 8, "Hooks", and
in full in each script's header comment.

Hook input is the JSON Claude Code sends on stdin (`tool_name`, `tool_input.command`,
`prompt`, `cwd`, `session_id`); the Bash and the PowerShell tool both give the command as
`tool_input.command`. A PreToolUse deny is the JSON
`{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"..."}}`
on stdout with exit 0, its reason naming the skill that would allow the command. Context for
UserPromptSubmit is the JSON
`{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"..."}}`; for
SessionStart plain stdout with exit 0 is enough. Every hook exits 0 and prints nothing when it has nothing to say, and never throws:
a malformed input or a missing file is silence, not an error.

## Agents (`agents/*.md`)

Frontmatter: `name`, `description`, `tools` (a list), `model`. Reviewers and judges:
`tools: Read, Glob, Grep, Bash` and `model: opus`. Each definition carries its character,
inputs, rules, report format and checklist, and reads the references its Inputs section
names. Skills start agents by name with the Agent tool, after reading the definition's
Inputs section, not the whole definition. A skill passes the card's Suggested model and
effort only to build sessions; agents keep their own `model`. Which skill starts each agent
and which references each reads is in `references/agents.md`.

## Skills (`skills/*/SKILL.md`)

Frontmatter may use `allowed-tools` (pre-approve the reads the skill makes, such as
`Bash(gh issue view *)`, `Bash(gh project item-list *)`, `Bash(git log *)`, `Bash(python *devfactory.py*)`). Every
skill calls `begin <skill>` as its first action and `end <skill>` as its last, including on
the path where it stops to ask, and its Markers paragraph ends with the sentence "When
`begin` prints `plugin-changed`, load this skill again before you continue." Its "Read these
first, in full" section opens with the sentence "A file you have already read in full in
this session, under the plugin version `begin` printed, need not be read again." No skill
tells a session to read another skill's `SKILL.md`; a passage two skills need lives in a
reference its owner keeps. Every `[machine]` condition is checked by the script named in
the definitions, never by reading. The coordinator names the desktop session tools directly
(`start_session`, `SendMessage`, `stop_session`, `mark_completed`, `archive_session`).

## Decisions taken during the build

- `context: fork` is not used: a forked skill cannot start agents or ask the requester, which is what `check-ready` and `curate` do.
- `release` is model-invocable, but runs only on the requester's explicit word in the conversation: `accept` and `coordinate` ask whether to release and start it themselves on a yes, or start it without asking when the requester authorised the release ahead of time, in their starting instruction or their acceptance answer. It does not set `disable-model-invocation: true`, which refuses the session's call even after the requester said to release. What an authorisation covers is stated once, in `release` under "What an authorisation covers".
- The agents' overview is `references/agents.md`, because plugin validation treats every file in `agents/` as an agent.
- `release` reaps: it stops, marks completed and archives every session the work started, then removes the worktrees, the branches and every detached review or judge checkout the run left. `coordinate`'s last step confirms from `release`'s closing list what was reaped and runs `markers --clear-stale`, which `configure-project`'s troubleshooting also names.
- The hooks read the profile through the script's `profile` command, so hooks and skills read it the same way.
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

The profile's sections and their defaults are in `references/profile-template.md`. Two
rules there bind the hooks:

- `## Hooks`: `- Tracker guard: off`, `- Stamp notice: off`,
  `- Session context: off`, `- Marker lifetime: <hours>h`, each written only when it departs
  from the default of all on and 12h. A hook reads its own line and exits silently when off.
- No `## Permissions` section: `configure-project` writes the read-only allowlist entries to
  `.claude/settings.json` in the project, which is their record.

The Sessions section holds the default model and effort and no runtime line; the
coordinator needs the Claude desktop app and says so.
