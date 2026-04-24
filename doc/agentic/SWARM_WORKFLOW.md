# SWARM_WORKFLOW

## Goal
Coordinate multiple specialized agents with explicit ownership, deterministic handoffs, and measurable validation.

## Roles
- `Architect`: owns contracts/interfaces and scope boundaries.
- `Builder`: implements code/doc changes within assigned scope.
- `Validator`: runs checks and reports evidence.
- `Integrator`: resolves conflicts and consolidates final state.

## Lifecycle
1. Intake: define objective, constraints, and acceptance criteria.
2. Partition: split work into disjoint ownership slices.
3. Execute: each slice progresses independently with local validation.
4. Validate: run shared checks and cross-slice consistency review.
5. Integrate: merge accepted slices and update operational docs.

## Handoff Contract
Every handoff must include:
- changed artifacts,
- assumptions made,
- validation run and result,
- unresolved risks.

## Conflict Resolution
- First criterion: deterministic tests/checks.
- Second criterion: lower complexity and clearer invariants.
- Third criterion: better traceability and rollback safety.
