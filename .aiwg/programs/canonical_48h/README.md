# DUMMIE Canonical Recovery 48H

Start date: 2026-05-19
Mode: SDD + TDD + AIWG evidence gates
Toolchain: `uv` only

## Objective
In 48 hours, stabilize the repository into a canonical operational state without destructive cleanup, with explicit contracts for:
- runtime identity
- L2 path/import compatibility
- AIWG truth integrity
- token/context governance
- memory/Kuzu safety

## Scope
- No mass deletion.
- No irreversible migrations.
- No secret exposure.
- No `READY` without runtime evidence.

## Deliverables
- SDD blueprint (`sdd/system_design.yaml`)
- TDD matrix (`tdd/test_matrix.yaml`)
- 48h schedule (`execution_schedule.json`)
- Quality gates (`quality_gates.yaml`)
- Risk register (`risk_register.yaml`)
- UV command profile (`uv_command_profile.yaml`)
- Canon runner (`scripts/canonical_48h_runner.py`)

## Success Definition
Canonical in 48h means:
1. preflight and pack guard pass
2. syntax and targeted tests pass
3. docs/spec evidence mismatch reduced to tracked queue with automated bridge plan
4. context killers and bloatware blocked from commit paths
5. Kuzu/4D-TES safety checks pass without mutating sovereign DB
6. AIWG receipts/reports emitted for each phase
