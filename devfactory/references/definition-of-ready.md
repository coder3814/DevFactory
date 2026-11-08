# Definition of Ready

**The purpose of a spec is to carry development to Done without a single additional
question.** Ready is the claim that this purpose is met: the card, the spec, the profile and
the repository already hold everything the work will consume. Every condition below is a
cheaply checkable way a spec commonly falls short of that purpose, and condition 9.3 tests
the purpose itself, end to end. A spec that meets every condition and still forces a question
mid-build has failed Ready by definition: the question is a readiness miss, recorded as a gap
and routed back as a spec amendment, never answered as chat
([`spec-template.md`](spec-template.md) gives the gap entry's form).

A spec is **Ready** when every condition holds, evaluated over four objects:

- the **card** on the tracker, written to [`card-standard.md`](card-standard.md), which holds
  the criteria and their stable IDs;
- the **spec** folder beside the code, laid out by [`spec-template.md`](spec-template.md);
- the **profile**, `.devfactory/profile.md`, laid out by
  [`profile-template.md`](profile-template.md);
- the **repository** at the commit the spec is stamped against, including the recorded
  decisions the profile says where to find.

Every check carries a mode:

- `[machine]` a script or a mechanical reading decides it: present or absent, matching or
  not.
- `[rubric]` an agent applies a named rubric, such as the row of an evidence plan.
- `[judgment]` an agent exercises adversarial judgment, looking for the way the spec fails.

A mode written `[machine: presence; judgment: adequacy]` splits one condition: the presence
part is mechanical, the adequacy part is judged. Cheap presence checks come first; the
end-to-end test, 9.3, is last.

**Ready is not approved.** Ready says the spec is complete enough to build from unattended,
not that it is what the requester wants. The requester approves the Ready spec once, and
judges intent once at acceptance; a rejection at approval is a spec amendment that re-earns
Ready. Who draws which decisions is fixed by [`decision-line.md`](decision-line.md).

## Conditions

### 1. The request is classified

1.1 The spec declares the request type(s): feature, bug fix, refactor, data correction,
    other. `[machine]`
    A mixed request declares every type it has; the Definition of Done takes the union of
    their test requirements.

1.2 The type fits the request. `[judgment]`
    A request declared a refactor that changes what an observer sees, or a bug fix that adds
    behaviour nobody had, does not fit.

1.3 For a bug fix, the failing scenario at the base revision is stated.
    `[machine: presence]`
    The scenario names the input or state that triggers the defect and the observed and
    expected behaviour, so the regression test's fails-at-base half can be derived from it.

1.4 For a refactor, the observable surface that must not change is named.
    `[machine: presence]`
    Any requested change to that surface is listed and excluded from it.

### 2. The criteria are addressable and testable

2.1 Every criterion carries a stable ID. `[machine]`
    IDs are `C1`, `C2`, and so on, survive amendment, and are never reused once removed.

2.2 Every criterion names observable behaviour a test could exercise and a result could
    fail. `[judgment]`
    A criterion fails this when it describes internal structure, when no delivered result
    could contradict it, or when it holds only for one implementation.

2.3 No criterion is marked provisional, and the card has no open question. `[machine]`

### 3. The boundaries are defined

3.1 Exclusions and deferrals are listed, each with a reason.
    `[machine: presence; judgment: adequacy]`
    An exclusion is out of scope for good; a deferral is kept alive elsewhere and says where.
    A reason is adequate when it is true of the request and explains the choice, so a
    considered exclusion can be told from one never considered.

3.2 Each requirement's edge behaviour is specified, excluded with a reason, or delegated to
    the developer. `[judgment]`
    Edge behaviour covers limits, empty and extreme inputs, failure paths, and concurrent or
    repeated actions. Delegation fits only an edge the developer's side of
    [`decision-line.md`](decision-line.md) covers.

3.3 Scope moves since the last Ready are reflected in both the card and the spec.
    `[machine]`

### 4. The fixed concerns are disposed

4.1 Every concern on the list has a disposition; "not applicable, because X" is one.
    `[machine: presence]`
    The core list: existing data changed; security; performance; release sequencing (does
    the change need anything before or after the deploy); owner steps. The profile may
    extend it. Silence is not a disposition.

4.2 Each disposition is true of the request as specified. `[judgment]`

4.3 A non-trivial disposition's demands appear as criteria or evidence rows. `[machine]`
    A disposition is non-trivial when it requires something to be done or shown, such as a
    permission check, a measured limit, or a step before the deploy.

### 5. The data population is checked

These conditions apply when the request's rules act on existing data.

5.1 The rules were run read-only against the population the spec names, with counts per
    rule. `[machine: presence]`

5.2 Every row no rule covers is resolved by a rule, an exclusion or a delegation.
    `[judgment]`

### 6. The interface surface is grounded

6.1 The determination is stated: non-trivial, trivial because, or not applicable because.
    `[machine]`
    Non-trivial means the work renders or serves something a person looks at with more than
    one obvious element to lay out. The determination is re-derived after any change to the
    card, not latched.

6.2 When non-trivial, the wireframe is present and approved, and grounds structure, fields,
    states and interaction. `[machine: presence; judgment: grounding]`
    States include empty, loading, error and populated where the surface has them. The
    wireframe fixes structure, not aesthetics, unless the profile chooses another fidelity.

### 7. The evidence plan is complete

7.1 Every criterion has an evidence row naming artifact, what it shows, condition, how it is
    generated and the checkpoint. `[machine]`

7.2 Every row could be failed by a delivered artifact. `[judgment]`
    A row fails this when what it promises to show would appear whether or not the criterion
    holds, such as a log line written before the behaviour runs.

7.3 Every checkpoint named is one the profile's environments can provide. `[machine]`
    A checkpoint names a profile environment whose "can show" covers what the row promises.

### 8. The owner's part is scheduled

8.1 Every owner step has a moment in the run. `[machine: presence]`
    A moment is a point a session can recognise, such as before the build starts, after a
    named sub-issue merges, or after the deploy.

8.2 For a parent issue, the work order's waits each cite an allowed reason, no pair marked
    parallel would collide, and no wait holds back work that could run. `[judgment]`
    The allowed reasons are: needs the other's result; changes the same files; both need
    something only one session can hold.

### 9. The spec grounds the work

9.1 Every project binding the spec relies on exists in the profile. `[machine]`

9.2 The spec is stamped with the card revision and repo commit it was checked against, and
    the card matches the stamp. `[machine]`

9.3 A fresh agent could decompose and build the work from the card, the spec, the profile
    and the repository without a single new question, every decision either grounded in them
    or delegated under principle 5. `[judgment]`
    Principle 5 is the line in [`decision-line.md`](decision-line.md). This is the purpose of
    the definition tested directly; conditions 1 to 8 catch its common failures cheaply.

## Exclusions

- **Approval is not gated.** Ready asserts the spec is complete enough to build from
  unattended, not that it is what the requester wants. Approval follows Ready and is the
  requester's.
- **Nothing is checked by taste.** Every check above carries a mode.

## What this definition leaves out and why

- **Per-criterion tag traceability from commits**: it needs tooling and a commit discipline
  the plugin cannot enforce.
- **Video evidence**: capture capability is the project's.
- **The per-spec rubric set and its instantiation**: the profile binds the few terms that
  vary.
- **The existing-behaviour gate as a spec entry**: it is a profile entry, the test gate.
