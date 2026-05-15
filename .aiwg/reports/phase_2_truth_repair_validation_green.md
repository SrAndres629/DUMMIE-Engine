# Phase 2 Truth Repair Validation Green

## What Was Fixed
SPEC-75 and SPEC-76 no longer list dynamic runtime directories as static
Physical Evidence.

- SPEC-75 moved `.aiwg/workbench/{mission_id}/` to `## Runtime Paths`.
- SPEC-76 moved `.aiwg/vault/` to `## Runtime Paths`.
- Both specs now keep `## Physical Evidence` limited to stable repo files.

## Files Changed
- `doc/specs/75_mission_workbench.md`
- `doc/specs/76_knowledge_vault.md`

## Commands Run
- `python3 scripts/validate_specs_docs.py --check doc/specs/75_mission_workbench.md`
  - Before: failed because `.aiwg/workbench/{mission_id}/` did not exist.
  - After: `DOC/SPEC VALIDATION OK (1 specs)`.
- `python3 scripts/validate_specs_docs.py --check doc/specs/76_knowledge_vault.md`
  - Before: failed because `.aiwg/vault/` did not exist.
  - After: `DOC/SPEC VALIDATION OK (1 specs)`.
- `python3 scripts/validate_specs_docs.py`
  - Before: failed only on SPEC-75 and SPEC-76 dynamic paths.
  - After: `DOC/SPEC VALIDATION OK (71 specs)`.
- `git diff --check -- doc/specs/75_mission_workbench.md doc/specs/76_knowledge_vault.md`
  - Result: exit 0, no whitespace errors.

## Evidence
- `scripts/validate_specs_docs.py` reads paths only from `## Physical Evidence`.
- The validator requires those paths to exist.
- The validator rejects most directory evidence unless the directory name is one
  of `docs`, `specs`, `.agents`, `doc`, or `infra`.
- Static source, test, and schema files for both specs exist.
- `.aiwg/workbench` and `.aiwg/vault` were not created as fake evidence.

## Validation Status
Global docs/spec validation is green:

```text
DOC/SPEC VALIDATION OK (71 specs)
```

## Conceptual Rule Learned
Physical Evidence must be stable, existing files that verify the contract.
Runtime Paths document dynamic storage roots created during execution and must
not be used as static evidence.

## Remaining Risks
- SPEC-76 still contains the preexisting typo `promovoted`.
- Phase 3 should avoid expanding scope beyond L1/L2 model contract alignment.

## Phase 3 Recommendation
Proceed to:

```text
FASE 3 - CONTRACT ALIGNMENT: L1/L2 MODEL SSoT
```

Focus first on the official PHYSICAL_MAP debt:

```text
Contratos de modelos (`AuthorityLevel`, `IntentType`, `AgentIntent`) no alineados entre L1 y L2.
```

Use a narrow Architect/Builder pass followed by an adversarial Validator pass.
