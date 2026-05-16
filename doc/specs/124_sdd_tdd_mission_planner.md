# Spec 124: SDD/TDD Mission Planner

## Purpose
Translate architectural goals and phase seeds into actionable, multi-level mission plans (L1/L2/L3) following SDD and TDD principles.

## Scope
- L1: Macro objective (from next_phase_seed).
- L2: Phase breakdown (outputs to produce).
- L3: Microphase tasks (atomic actions).
- SDD/TDD requirement injection.

## Runtime Behavior
1. Read `current_position.json` and `next_phase_seed.json`.
2. Analyze `repo_probe_latest.json` for gaps.
3. Map each required output to a sequence of microphases (Draft -> Verify).
4. Inject standard SDD/TDD constraints.
5. Produce `mission_plan_latest.json` and `.md`.

## Safety Rules
- Do not execute any changes; only plan.
- Do not store private reasoning or chain-of-thought.
