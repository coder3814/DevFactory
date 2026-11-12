---
name: accept
description: Show the requester every criterion of a card, or of every sub-issue in a parent issue run, with its evidence, ask once whether to accept them all or which to refuse, ask whether the whole is what was wanted, sort any refusal into a defect, a request change or a new request, and hand to release, without asking again when the release is authorised ahead of time. Use when a parent run has the Done judge's DONE verdict, or a standalone card has passed its change review, or either carried on past its review limit after spec-only amendments.
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
already naming what it refuses. Every criterion is shown at once and asked about in one
question, never one criterion at a time. A parent issue has no criteria of its own: in a
parent run, the criteria shown are the sub-issues'. Under a coordinator, every read, write
and event below is done by a session or an agent it starts, as `coordinate` says.

`devfactory` below means running the plugin's script with `python`: the script is
`${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py`; if that variable is empty in your shell, it
is `../../scripts/devfactory.py` relative to this skill's folder.

**Markers.** Run `devfactory begin accept` as your first action and
`devfactory end accept` as your last. Whenever you end your turn to wait for the
requester's answer, or to report, run `devfactory end accept` first, and
`devfactory begin accept` again when you resume. A marker expires after the profile's
Marker lifetime (12 hours by default), and `begin` refreshes it. Markers and the profile
are found at the repository (worktree) root, wherever the shell's working directory is.
When `begin` prints `plugin-changed`, load this skill again before you continue.

Every question first passes "Before anything is asked" in
[`../../references/decision-line.md`](../../references/decision-line.md): the profile's
Standing answers, then the decision line. What survives is asked one question at a time,
the recommended option first with a one-line reason, except that steps 2 and 3 are put
together when the platform can ask both at once.

## Read these first, in full

A file you have already read in full in this session, under the plugin version `begin`
printed, need not be read again.

- [`../../references/working-a-card.md`](../../references/working-a-card.md): loading the
  profile and reading a card.
- [`../../references/spec-template.md`](../../references/spec-template.md): the evidence
  plan, `evidence/`, `gaps.md` and the amendments table.
- [`../../references/definition-of-done.md`](../../references/definition-of-done.md): the
  conditions a defect's gap entry names.
- [`../../references/definition-of-ready.md`](../../references/definition-of-ready.md): the
  conditions a request change's gap entry names.

## Steps

1. **Load and read.** Load the profile as `working-a-card.md` says. Read the card and its
   spec with its evidence, or for a parent run the parent and every sub-issue the run
   built, with each sub-issue's spec and evidence. Start only once the result is Done: the
   Done judge's DONE for a parent run, the change review's PASS for a standalone card, or,
   for either, a round past the review or judgment limit whose findings were all fixed by
   spec-only amendments, as "Findings after the review limit" in
   `../../references/decision-line.md` says. Leave every card where it sits on the board.

2. **Show every criterion, then ask once.** In one message, take each sub-issue's criteria
   in the work order, or a standalone card's criteria. For each criterion show its ID and
   text, the evidence row's artifact (the image itself, the test and its result, the log or
   query output), what the row promised it shows and under what condition, and the revision
   and checkpoint from its sidecar. Flag each caveat where it applies: an artifact that does
   not show what its row promised, a checkpoint or revision other than the one the row
   names, or anything left unverified. A row marked post-release in the evidence plan has
   no artifact yet: show it as pending, with its checkpoint and what `release` will capture
   there once the deploy is live, never as a caveat against accepting. When the build's
   report carries the line "no review passed this revision", show that line in the
   acceptance question, word for word, with the last review's findings and their
   amendments. Then ask one question: accept every criterion, or name the refused ones by
   ID. Recommend accepting all when every artifact shows what its row promised; when one
   does not, name it and recommend refusing it. When the release is not yet authorised
   (step 6), offer accepting all and releasing as an option of its own.

3. **Ask about the whole.** Ask whether the result is the outcome the requester wanted, or
   something is missing that no criterion covers. When the platform can ask more than one
   question at once, such as the `AskUserQuestion` tool, ask this together with step 2's
   question; otherwise ask it next.

4. **Sort a refusal.** A refusal names the criterion the result fails or the outcome that is
   missing; when it names neither, ask which. State the class below with its reason, and
   when the refusal reads two ways, ask which is meant. Once it is sorted as a defect
   or a request change, fire `refused` for the card that owns the refused criterion or
   outcome, and in a parent run for the parent as well, with `devfactory event refused
   --card <n>`, as `../../references/events.md` says; a hook that fails is reported
   with its output. A refusal that becomes a new card fires nothing.
   - **Fails a stated criterion.** A defect, not a change. Send it back to the build
     session, or in a parent run to the coordinator, which has it fixed as its Done
     findings are: by the kept session of the sub-issue it belongs to, or, when no
     sub-issue owns it, by the kept session of the sub-issue whose files it touches most.
     Add a gap entry to that criterion's spec at stage Acceptance, let through by the Done
     condition that should have caught it, resolved by an amendment that records the fix
     and its commit and changes nothing else; write it with `devfactory gaps add <spec dir>
     --stage Acceptance --question <the refusal> --condition "Done <id>" --resolved
     <version>`, each value quoted as one argument. The fix is reviewed and, in a parent
     run, judged again, and the refused criterion, with any other the fix touched, is
     shown and asked again as step 2 says, in one question.
   - **Meets every criterion but is not what was wanted.** A request change. Record the
     requester's words on the card through `add-to-card` in settled mode (its "Settled
     mode" heading), the words being the acceptance, then have `grill` Re-derive bring the
     spec along for the conditions those criteria feed, naming stage Acceptance and the
     Ready condition that let it through, written `Ready <id>`, with `--kind
     request-change` when the requester changed their mind rather than the spec missing
     what they asked for; Re-derive writes the gap entry and resolves it by its amendment.
     The build continues, through review and, in a parent run, the Done judge, to a second
     acceptance: in a parent run, by the kept session of the sub-issue it belongs to, or by
     the kept session of the sub-issue whose files it touches most when no sub-issue owns
     it, as a Done finding is built.
   - **Wants something the request never asked for.** A new card through `create-card` by
     default, and this card is accepted as specified: carry on with the acceptance. Amend it into
     this card, as a request change, only when the addition is inseparable from the outcome
     under review. Ask which, recommending the new card unless it is inseparable.

5. **Record the acceptance.** When every criterion and the whole are accepted, record the
   requester's words verbatim on the card, and in a parent run on the parent and each
   sub-issue it covers, through `add-to-card` in settled mode. Then fire `accepted` for
   each card accepted, with `devfactory event accepted --card <n>`, as
   `../../references/events.md` says; a hook that fails is reported with its output.
   Acceptance ends here; a
   parent run's sessions, worktrees and branches stay until `release` reaps them.

6. **Hand to release.** `release` runs only on the requester's word, never on an agent's
   own judgment. The requester's word may come ahead of time: their starting instruction
   for the run or the card (such as "you have pre-approval to drive all the way to the
   end"), or their acceptance answer, such as the accept-and-release option of step 2.
   What that word covers is stated once, in `release` under "What an authorisation
   covers". When it has come, tell the requester the work is accepted, quoting their
   words, and start `release` in this session without asking again, quoting the words that
   authorised it. When it has not, tell them the work is accepted and ready to release,
   quoting their words, and ask once whether to release; when they say yes, start
   `release` in this session yourself.
