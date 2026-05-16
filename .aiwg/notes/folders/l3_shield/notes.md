# Folder Note: l3_shield

## Status
active

## Folder Path
`layers/l3_shield`

## Purpose
security/shield layer

## Canonical Sources
- `layers/l3_shield`
- `.aiwg/world_model/project_world_model.json`
- `.aiwg/reports/spec_coverage_matrix.json`

## Linked Specs
- `doc/specs/L3_Shield/04_anti_ignorance_shields.md`
- `doc/specs/L3_Shield/22_sdd_executable_contracts.md`

## Linked Tests
- `layers/l3_shield/tests/test_authority_gate.py`
- `layers/l3_shield/tests/test_knowledge_policy.py`
- `layers/l3_shield/tests/test_topological_auditor.py`

## Linked Capabilities
- capability linkage deferred or indirect


## Layer / Language Context
- Layer: `L3`
- Languages: Python, Rust

## Truth Policy
- This note is derived, not canonical.
- Code/tests/specs outrank this note.
- This note must be refreshed when source_hash changes.

## Token Role
summary_only

## What To Load Instead Of Raw Folder
- `.aiwg/notes/folder_notes_manifest.json`
- `.aiwg/world_model/project_world_model.json`
- This folder note and its noteplan.

## Risks
- Potential freshness drift if source files change and note is not refreshed.


## Refresh Triggers
- source_file_changed
- linked_spec_changed
- linked_test_failed
- coverage_matrix_changed

## Next Actions
- Recompute source hash in P10 freshness ledger.
- Expand test/spec linkage depth where confidence is medium or low.
- Promote to retrieval_candidate only when fresh and task-relevant.
