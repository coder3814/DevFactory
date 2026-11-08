# Definition of Done

A change is **Done** when every condition below holds. Done is the stopping case for
development: the Done judge applies it to the delivered result before the requester is asked
to accept, and a condition that fails is fixed as development work.

Every condition is evaluated over three objects:

- the **spec** that governed the work, with its amendments, laid out by
  [`spec-template.md`](spec-template.md), and the card criteria it cites;
- the **base revision**, the revision the change was built from;
- the **revision under evaluation**, the delivered change. Every comparison of before and
  after compares exactly these two.

Every check carries a mode, as in [`definition-of-ready.md`](definition-of-ready.md):
`[machine]` the command its tag names decides it, a command of
`${CLAUDE_PLUGIN_ROOT}/scripts/devfactory.py` or, for 1.1, the profile's own
test gate, and `[machine: the judge reads]` marks a condition no command covers yet, which
the Done judge decides by a mechanical reading; `[rubric]` an agent applies a named rubric;
`[judgment]` an agent exercises adversarial judgment, looking for the way the result fails.

**Intent is not gated.** Whether the result is what the requester wanted is judged by the
requester at acceptance, criterion by criterion against the evidence, never here.

## Conditions

### 1. The tests exist and pass

1.1 The profile's test gate passes at the revision under evaluation.
    `[machine: the profile's test gate]`

1.2 The test types the request type requires exist and pass: a feature has a test per
    criterion; a bug fix has a test that fails at base and passes now; a refactor shows the
    declared surface unchanged; a data correction has the dry run's counts matching the
    apply's. `[machine: the judge reads]`
    A mixed request takes the union of its types' requirements. For "other", the spec states
    the test types.

### 2. The tests test the spec

2.1 Every criterion is exercised by at least one test or evidence artifact.
    `[machine: evidence-check]`
    The link is the criterion ID, cited by the test or by the artifact's folder under
    `evidence/`.

2.2 Each test asserts an observable outcome and would survive a reimplementation.
    `[judgment]`
    A test fails this when it asserts internal calls or structure, so that a different
    implementation behind the same interface would fail it.

### 3. The evidence fulfils its promises

3.1 Every evidence row has its artifact, showing what the row promised under the stated
    condition, captured at the stated checkpoint. `[rubric: the row]`
    When the interface determination is non-trivial, the approved wireframe is the reference
    an interface artifact is compared with.

3.2 Each artifact records the revision, the checkpoint and the command or procedure that
    produced it. `[machine: evidence-check]`

### 4. The work is grounded

4.1 Every decision embodied in the work is grounded in the spec or recorded as a delegated
    call in the spec's log. `[judgment]`
    A decision the requester owns under [`decision-line.md`](decision-line.md) cannot be
    grounded by the log.

4.2 The gap record is closed: every gap has a resolving amendment. `[machine: gaps check]`

4.3 Every disposition is still true of the delivered result. `[judgment]`
    The approach can falsify a disposition that was true of the request, such as a change
    declared to leave existing data alone that rewrites it.

### 5. Nothing beyond the request

5.1 Every change in the change set serves a criterion, a delegated call or the work's own
    scaffolding. `[judgment]`
    The change set is everything from the base revision to the revision under evaluation.

### 6. For a parent issue

6.1 Every parent criterion is met by the combined result, including what no single sub-issue
    could show. `[judgment]`

## Exclusions

- **Intent is not gated.** The requester judges it at acceptance.
- **Nothing is checked by taste.** Every check above carries a mode.
- **Readiness is not re-checked.** That every concern has a disposition and every criterion
  an evidence row is a Ready guarantee; Done checks what the delivered result did to them.

## Machine conditions without a script yet

- **1.2** The test types the request type requires: the Done judge runs and reads them
  until a command of `scripts/devfactory.py` covers them.

Condition 1.1 needs no script: the profile's test gate command decides it. Condition 2.1 is
decided by `evidence-check`, given the criterion IDs `criteria-ids` prints, because every
criterion has an evidence row (Ready 7.1) and so an evidence folder of its own.
