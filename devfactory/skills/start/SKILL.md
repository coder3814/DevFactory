---
name: start
description: Start work on a card — read it once, tell a parent issue from a standalone card, and hand over in the same session, to `coordinate` for a parent issue and to `build` for a standalone card; a parent that still carries a part beyond its title, purpose, work order and suggested model and effort, such as criteria or supporting information, is not started and goes through `re-evaluate-card` first. Use when the requester says to start work on card N, or runs `/devfactory:start N`.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(python *devfactory.py*)
  - Bash(gh issue view *)
  - Bash(gh project item-list *)
  - Bash(gh api -X GET *)
  - Bash(az boards work-item show *)
---

# Start work on a card

"Start work on card N", or `/devfactory:start N`, comes here and nowhere else. This skill
decides which skill works the card and hands over to it in the same session and the same
turn, so the turn stays the requester's own. It writes nothing, fires no event and asks
nothing: the skill it hands to does all of that.

`devfactory` below means running the plugin's script with `python`: the script is
`${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`; if that variable is empty in your shell, it
is `../../scripts/devfactory.py` relative to this skill's folder.

**Markers.** Run `devfactory begin start` as your first action and `devfactory end start`
before you hand over, as step 4 says. Markers and the profile are found at the repository
(worktree) root, wherever the shell's working directory is. When `begin` prints
`plugin-changed`, load this skill again before you continue.

## Read these first, in full

A file you have already read in full in this session, under the plugin version `begin`
printed, need not be read again.

- [`../../references/working-a-card.md`](../../references/working-a-card.md): loading the
  profile and reaching the tracker through the binding.

## Steps

1. **Begin.** Run `devfactory begin start`.

2. **Load the profile** as `working-a-card.md` says, with the binding it names. With no
   profile, start nothing: say so and offer `configure-project`.

3. **Read the card once**, with the tracker read the binding gives, and decide what it is.
   A card with sub-issues is a parent issue; any other card is a standalone card. A parent
   issue holds a title, a purpose, the work order and the suggested model and effort, and
   nothing else. One that still carries a part beyond those four, such as acceptance
   criteria or supporting information, is not started: tell the requester it goes through
   `re-evaluate-card` first, which restructures it with them, run `devfactory end start`,
   and stop. A spec line alone on a parent is no reason to stop: `grill` removes it.

4. **End and hand over.** Run `devfactory end start`, then, in this session and this turn:
   - for a parent issue, load the `coordinate` skill for it and follow it from its first
     step;
   - for a standalone card, load the `build` skill for it and follow it from its first
     step.
