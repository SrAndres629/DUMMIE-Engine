# Folder Note: l1_nervous

## Status
active

## Folder Path
`layers/l1_nervous`

## Purpose
protocol/gateway layer

## Canonical Sources
- `layers/l1_nervous`
- `.aiwg/world_model/project_world_model.json`
- `.aiwg/reports/spec_coverage_matrix.json`

## Linked Specs
- `doc/specs/L1_Nervous/10_protobuf_contracts.md`
- `doc/specs/109_polyglot_architecture_registry.md`

## Linked Tests
- `layers/l1_nervous/tests/conftest.py`
- `layers/l1_nervous/tests/industrial/test_e2e_flow.py`
- `layers/l1_nervous/tests/industrial/test_fencing.sh`
- `layers/l1_nervous/tests/industrial/test_observe_swarm_perf.py`
- `layers/l1_nervous/tests/industrial/test_swarm_race.py`
- `layers/l1_nervous/tests/test_causal_chaining.py`

## Linked Capabilities
- capability linkage deferred or indirect


## Layer / Language Context
- Layer: `L1`
- Languages: Python, Go

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
