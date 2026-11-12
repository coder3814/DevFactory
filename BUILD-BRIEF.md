# Build brief for DevFactory authors

Read this, then `DESIGN.md` in full, before writing any file. `DESIGN.md` is the design of
record; where your task and it disagree, follow it and report the disagreement.

## Voice and form

- Match the existing references in `devfactory/references/`: plain prose,
  wrapped at about 90 columns, present tense, rules stated as what is true or must hold.
- Rule text names roles ("the requester", "the owner", "the developer", "the coordinator"),
  never people.
- Write for Claude Code. DevFactory is designed for it alone; portability to another agent
  system is not a goal. Name Claude Code's tools, hooks and frontmatter wherever they do the
  job: "start the `card-reviewer` agent with the Agent tool", a script command for a machine
  check, a hook for enforcement, `allowed-tools` in a skill's frontmatter.
  Name no model, except in an agent's frontmatter; a build session's model comes from the
  card's suggested model or the profile.
- Project-agnostic. Nothing about any one project, its domain, its pages, its databases or
  its cloud. When you need an example, invent a neutral one or use a generic shape.
- Every skill's `SKILL.md` has YAML frontmatter with `name` and a `description` that says
  what it does and when to use it, as the carried-over skills do. Paths in a skill are
  relative to the skill's directory (`../../references/...`).
- Every skill's "Read these first, in full" section and its Markers paragraph carry the two
  sentences `CLAUDE-FIRST.md` gives under "Skills", word for word. No skill tells a session
  to read another skill's `SKILL.md`: a passage two skills need lives in a reference, and
  its owner updates both ends.
- Every agent definition in `devfactory/agents/` carries its character, inputs, rules,
  report format and checklist, and reads the references its Inputs section names, with
  frontmatter `name`, `description`, `tools` (read-only tools for reviewers and judges) and
  `model`. A skill that starts an agent reads that definition's Inputs section, not the
  whole definition.
- Concise: say each thing once, in the place a reader needs it, and cross-reference by
  path and heading rather than restating. When a rule is removed, remove every trace of it.
- Describe current behaviour only: no history notes, and no words that estimate time or
  effort.

## Terms

- **Card**: the request on the tracker. **Spec**: the specification folder beside the code.
  **Profile**: the project's `.devfactory/profile.md`. **Gap**: an entry in `gaps.md`.
  **Stamp**: the spec header's card revision hash, repo commit and date.
- **Parent issue**: a card with sub-issues, holding a title, a purpose, the work order and a
  suggested model and effort, and no spec. **Records folder**: a parent's
  `<specs path>/<parent id>/`, holding only `receipts.md`, `gaps.md` and `reviews.md`.
- **Requester**: whoever owns the request (the owner on a one-person project).
  **Coordinator**: the session running a parent issue. **Build session**: one session
  developing one card.
- Stages: Request, Grilling, Approval, Development, Done, Acceptance, Release.

## Done for your task

Report, in your final message: each file written with its path and a one-line summary,
every place you deviated from `DESIGN.md` and why, and any question you could not settle
from the design (make the call, state it, and flag it). Change no file outside your task's
list. Start no subagents.
