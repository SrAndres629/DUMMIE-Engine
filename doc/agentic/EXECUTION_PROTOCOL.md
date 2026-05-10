# EXECUTION_PROTOCOL

## Purpose
Define end-to-end execution protocol for agentic tasks from request to closure.

## Phases
1. Understand
- capture objective, constraints, and success criteria.
- inspect physical repo state before proposing edits.

2. Plan
- produce decision-complete plan with assumptions.
- define validation commands before implementation.

3. Implement
- execute smallest safe diff per step.
- keep docs in sync when contracts or architecture claims change.

4. Verify
- run relevant tests/checks.
- report command evidence, not assumptions.

5. Close
- summarize outcome,
- list remaining risks,
- record next actions.

## Required Evidence
- `git status --short`
- validation command outputs for changed behavior
- updated documentation references when applicable

## Completion Criteria
A task is complete only when acceptance criteria are met and evidence is present.
