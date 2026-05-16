# Folder Note: l2_brain

## Status
active

## Folder Path
`layers/l2_brain`

## Purpose
cognitive runtime layer

## Canonical Sources
- `layers/l2_brain`
- `.aiwg/world_model/project_world_model.json`
- `.aiwg/reports/spec_coverage_matrix.json`

## Linked Specs
- `doc/specs/107_cognitive_artifact_protocol.md`
- `doc/specs/108_truth_hierarchy_canonicality_policy.md`
- `doc/specs/110_project_world_model.md`

## Linked Tests
- `layers/l2_brain/tests/conftest.py`
- `layers/l2_brain/tests/infrastructure/test_kuzu_path_hardening.py`
- `layers/l2_brain/tests/infrastructure/test_kuzu_repository.py`
- `layers/l2_brain/tests/test_adapters_cypher_injection.py`
- `layers/l2_brain/tests/test_agent_office_models.py`
- `layers/l2_brain/tests/test_architectural_boundaries.py`

## Linked Capabilities
- `PhaseLedger`
- `ContextBudgetManager`
- `SemanticRetrievalRuntime`
- `MemoryGraphRuntime`
- `MissionWorkbench`
- `OutcomeEvaluator`
- `TokenCostLedger`
- `SessionStore`
- `LearningEpisode`
- `VaultCurator`
- `CognitiveHooks`
- `ModelRouter`


## Layer / Language Context
- Layer: `L2`
- Languages: Python

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
