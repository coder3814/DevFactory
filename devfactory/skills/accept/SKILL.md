---
name: accept
description: Walk the requester through accepting a card or a parent issue run, criterion by criterion against the evidence plan, and sort any refusal into a defect, a request change or a new request. Use when a parent run has the Done judge's DONE verdict, or a standalone card has passed its change review.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(python *devfactory.py*)
  - Bash(gh issue view *)
  - Bash(gh project item-list *)
  - Bash(az boards work-item show *)
  - Bash(git log *)
  - Bash(git show *)
---

# Accept a card or a parent run

The requester judges intent here, once, against the evidence. Nothing is checked by taste:
each criterion is shown with the artifact its evidence row promised, so a refusal arrives
already naming what it refuses. Under a coordinator, every read, write and board move below
is done by a session or a subagent it starts, as `coordinate` says.

`devfactory` below means running the plugin's script with `python`: the script is
`${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`; if that variable is empty in your shell, it
is `../../scripts/devfactory.py` relative to this skill's folder.

**Markers.** Run `devfactory begin accept` as your first action and
`devfactory end accept` as your last. Whenever you end your turn to wait for the
requester's answer, or to report, run `devfactory end accept` first, and
`devfactory begin accept` again when you resume. A marker expires after the profile's
Marker lifetime (12 hours by default), and `begin` refreshes it. Markers and the profile
are found at the repository (worktree) root, wherever the shell's working directory is.

The requester is asked one question at a time, the recommended option first with a
one-line reason.

## Read these first, in full

- [`../../references/working-a-card.md`](../../references/working-a-card.md): loading the
  profile and reading a card.
- [`../../references/spec-template.md`](../../references/spec-template.md): the evidence
  plan, `evidence/`, `gaps.md` and the amendments table.
- [`../../references/definition-of-done.md`](../../references/definition-of-done.md): the
  conditions a defect's gap entry names.
- [`../../references/definition-of-ready.md`](../../references/definition-of-ready.md): the
  conditions a request change's gap entry names.

## Steps

1. **Load and read.** Load the profile as `working-a-card.md` says. Read the card, or for a
   parent run the parent and every sub-issue the run built, and each spec with its evidence.
   Start only once the result is Done: the Done judge's DONE for a parent run, the change
   review's PASS for a standalone card. As acceptance begins, move the card, or the parent
   and every sub-issue the run built, to Acceptance.

2. **Walk the criteria.** Take the parent's criteria first, then each sub-issue's in the
   work order. For each criterion show its ID and text, the evidence row's artifact (the
   image itself, the test and its result, the log or query output), what the row promised it
   shows and under what condition, and the revision and checkpoint from its sidecar. Ask
   whether to accept it. Recommend accepting when the artifact shows what the row promised;
   when it does not, say so and recommend refusing.

3. **Ask about the whole.** After the last criterion, ask whether the result is the outcome
   the requester wanted, or something is missing that no criterion covers.

4. **Sort a refusal.** A refusal names the criterion the result fails or the outcome that is
   missing; when it names neither, ask which. State the class below with its reason, and
   when the refusal reads two ways, ask which is meant.
   - **Fails a stated criterion.** A defect, not a change. Send it back to the build
     session, or in a parent run to the coordinator, which has it fixed as its Done
     findings are: by the kept session of the sub-issue it belongs to, or by a new session
     cut from the parent branch when no sub-issue owns it. Add a gap entry to that
     criterion's spec at stage Acceptance, let through by the Done condition that should
     have caught it, resolved by an amendment that records the fix and its commit and
     changes nothing else; write it with `devfactory gaps add <spec dir> --stage
     Acceptance --question <the refusal> --condition <Done condition> --resolved
     <version>`, each value quoted as one argument. The fix is reviewed and judged again, and the refused criterion, with any other the fix touched, is asked
     again.
   - **Meets every criterion but is not what was wanted.** A request change. Record the
     requester's words on the card through `add-to-card` in settled mode, the words being
     the acceptance, and let its hand-off to `grill` re-derive bring the spec along for the
     conditions those criteria feed. The build continues, through review and, in a parent
     run, the Done judge, to a second acceptance: in a parent run, by the kept session of
     the sub-issue it belongs to, or by a new session cut from the parent branch when no
     sub-issue owns it, as a Done finding is built. The gap entry, at stage Acceptance, notes that
     Ready was earned on a spec that did not ground the outcome, names the Ready condition
     that let it through, and is resolved by the re-derivation's amendment; it is written
     with `devfactory gaps add` the same way, at stage Acceptance.
   - **Wants something the request never asked for.** A new card through `create-card` by
     default, and this card is accepted as specified: carry on with the walk. Amend it into
     this card, as a request change, only when the addition is inseparable from the outcome
     under review. Ask which, recommending the new card unless it is inseparable.

5. **Record the acceptance.** When every criterion and the whole are accepted, record the
   requester's words verbatim on the card, and in a parent run on the parent and each
   sub-issue it covers, through `add-to-card` in settled mode. Acceptance ends here; a
   parent run's sessions, worktrees and branches stay until `release` reaps them.

6. **Hand to release.** `release` runs only when the requester starts it, never on an
   agent's own invocation. Tell the requester the work is accepted and ready to release,
   quoting their words, and ask them to start `release` in this session; whether their
   acceptance also answers a release question is the profile's to say.
