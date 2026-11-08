# Fix decisions after the first review

Binding for every author in the fix wave. Each item names the rule as it now stands and the
files that must say it. Where a file says otherwise, change it. Read BUILD-BRIEF.md and
DESIGN.md first; this file amends DESIGN.md where it says so, and DESIGN.md gains an
Amendments section recording each.

1. **Gap ledger.** Gap records survive release. At release, before a spec folder is deleted,
   its `gaps.md` entries are appended to the project ledger `.devfactory/gaps.md`, each
   prefixed with the card id. The readiness checker and `curate` read the ledger plus every
   live `gaps.md`. (spec-template, profile-template, release, curate, grill, check-ready,
   readiness-checker, DESIGN 3.6)

2. **One rule for card writes.** `add-to-card` has two modes named by its caller:
   - **interactive** (default): record, fold, show, the user accepts, write, verify.
   - **settled**: the requester has already answered (a grilling question, a relayed
     question in a run, a refusal's words at acceptance): record the answer as the comment,
     fold, write, verify, report the folded text; the requester may object afterwards.
   `grill` always calls it settled, and passes `no-rederive`, so `add-to-card` skips its
   spec step; every other caller lets `add-to-card` hand off to `grill` re-derive when a
   part changed. DESIGN 12.1 now reads: acceptance of the rewritten wording stays for
   interactive additions made outside grilling and outside a run; the requester's answer is
   the acceptance everywhere else. The card-process rationale bullets say the same.
   (card-process, working-a-card, add-to-card, grill, check-ready, build, coordinate, accept)

3. **Checker dispatch.** `grill` and `check-ready` pass every input `readiness-checker.md`
   requires: references folder, repository path and branch head, each card's text, revision
   (computed per "The stamp") and stage, spec paths, profile path, gap sources (ledger and
   live files), the moment, and the kind (fresh, follow-up with the earlier report and spec
   version, or re-derive with the conditions to re-run). (grill, check-ready)

4. **Buildable means approved.** A build starts only on a spec whose status is `approved`.
   `coordinate` and `build` both check the spec status, not the column. (build, coordinate)

5. **Data access.** `configure-project` asks for the profile's Data access section (each
   population a card's rules might act on; how it is read without writing). `grill` and the
   checker run data rules through it. (configure-project, grill)

6. **Gaps start at Ready.** A question answered before a spec first earns Ready is folded,
   not a gap. From Ready onward, every question, refusal and Done miss is a gap, with its
   stage being the card's current stage (Approval, Development, Done or Acceptance). `grill`
   amend is "after Ready", not "during development". `check-ready` routes every answer for a
   stamped spec through amend only; re-derive is for card changes, not answers.
   (spec-template gap format, grill, check-ready)

7. **Condition 9.2.** The stamp's Repo commit is the branch head the checker read. 9.2 holds
   when the card's revision equals the stamp's and the stamped commit is an ancestor of the
   current branch head. At creation, before the stamp exists, 9.2 is not applicable and the
   checker reports the revision and head it checked for `grill` to stamp. (definition-of-
   ready gloss, readiness-checker, grill)

8. **The spec line.** Exactly one line, the last line of the description body, in the form
   `Spec: <path> @ <commit>`, where the commit is the spec folder's own commit. The stamp
   excludes any line matching that form. `grill` writes it directly after committing the
   spec (its one direct card write, not an addition; no comment is recorded). Order in
   `grill` new: stamp, commit the spec, write the line. (card-standard "The spec line",
   spec-template "The stamp", grill, add-to-card says it never writes the line)

9. **Grilling a parent.** `grill` on a parent issue grills every sub-issue not yet Ready,
   one spec each, then the parent's own spec (its dispositions, evidence rows for parent
   criteria, owner steps, bindings). The parent moves to Approval only when every sub-issue
   is Ready, and one approval covers the set. (grill, check-ready)

10. **Sessions live until acceptance.** `coordinate` keeps every sub-issue session, worktree
    and branch until `accept` ends in acceptance; a request-change refusal in a parent run
    is built by a new session cut from the parent branch, the same way a Done-judge finding
    is. Reaping happens in `release`. (coordinate, accept, release)

11. **Bounded loops.** After a review or judge FAIL, at most two further rounds; if the third
    still fails, stop and report to the coordinator (or the requester for a standalone card)
    with the findings. (build, coordinate)

12. **Order and hand-offs.**
    - Merge in finish order, a waiting card after the card it waits on; DESIGN 4 is amended
      to say so.
    - A card moves to the Acceptance column when acceptance begins, to Release when released.
    - `coordinate` hands to `accept`; `accept` hands to `release`; `coordinate` does not call
      `release` itself.
    - A standalone card: `build` stops after its PASS without merging; `accept`, then
      `release` merges once.
    - `check-ready` runs at parent creation, when a card is added, and at development start.
    - The coordinator runs no git or tracker command itself; following `check-ready` it
      delegates every read and write to subagents.
    (coordinate, accept, build, release, check-ready)

13. **Profile gains three entries** under Branches and merging and Sessions: the sub-issue
    branch name pattern; the release procedure (the project's steps or the skill it names);
    the design-review procedure (how a wireframe is shown and approved), under a new
    "Design review" line in Wireframe fidelity. The change reviewer's base revision is the
    merge-base of the card's branch with the parent branch (or integration branch) at review
    time. (profile-template, configure-project, build)

14. **Models.** Every skill that starts an agent passes a model: the card's Suggested model
    and effort, else the profile's default. `working-a-card.md` says the card reviewer runs
    on the profile's default. (working-a-card, build, coordinate, grill, check-ready,
    create-card, add-to-card, re-evaluate-card)

15. **Example module.** `examples/work-type-module.md` loses the product-specific values:
    generic work types (Expansion, Improvement, Internal, Maintenance, Fixes) with generic
    examples, no tool or industry names. (examples)

16. **DESIGN.md** gets an "Amendments" section after section 13 listing, by number, each
    change made during the build: 3.4 data access and the three profile entries; 3.6 the
    ledger; 4 the Approval and Done exits, merge order and column timing; 9 the agents
    folder; 12.1 restated; 12.5 deferred (the owner has not yet decided; flagged). Its header
    status becomes "accepted 2026-11-07; amended during the build as the Amendments section
    records".
