# DUMMIE PLAN V1 — P3 Artifact Lifecycle Reconciliation Audit

## Decision

PASS_WITH_WARNINGS

## Summary

P3 audited existing artifact families, mapped canonicality and runtime consumers, and formalized named counting profiles to resolve the P2 Codex/Gemini count discrepancy as a semantics issue. No runtime code was modified.

## Artifact Types Found

- Total audited artifact types: 39
- Types with count > 0: 26

## Canonical Artifacts

- specs (`spec_md`, `spec_feature`, `spec_rules_json`)
- schemas (`schema_json`)
- mission state artifacts (`phase_ledger`, `mission_state`, `recovery_packet`, `next_action`)
- session/evolution governance (`session_contract`, `evolution_roadmap`)
- runtime source and tests (`source_code_runtime`, `test_file`)

## Derived Artifacts

- reports (`report_md`, `report_json`)
- vault/memory-related entries where freshness/hash controls are still weak (`vault_entry`, `memory_ref`)

## Dead Documentation Candidates

- `legacy_doc` artifacts, including known unresolved spec references in `doc/guides/mcp_server_usage.md`.

## Duplicate Truth Risks

- Overlapping truth in registries and roadmap/report artifacts (`registry`, `evolution_roadmap`, `report_md`, `report_json`).
- Potential overlap between vault and memory references (`vault_entry`, `memory_ref`).

## Stale-Prone Artifacts

- `spec_md`
- `legacy_doc`
- `vault_entry`
- `memory_ref`
- report artifacts when reused as operational truth

## Runtime Consumers

- Specs: `scripts/validate_specs_docs.py`, `future:SpecCoverageGate`
- Mission artifacts: `PhaseLedger`, `LongRunningMissionRuntime`, `MissionRecoveryRuntime`
- Vault/memory: `VaultCurator`, `VaultEmbeddingIndex`, `SemanticRetrievalRuntime`, `MemoryGraphRuntime`
- Session contracts: `all_agents`, `per_message_operating_contract`
- Evolution roadmap: `current_position`, `next_phase_seed`, `phase_dependencies`

## Counting Semantics

P3 deprecates a single ambiguous `.aiwg` file count and replaces it with named profiles in `.aiwg/reports/plan_v1_phase_3_artifact_counting_semantics.json`.

## What P4 Must Govern

- lifecycle states by artifact class
- canonicality and truth hierarchy hooks
- freshness and source-hash requirements
- promotion/demotion and invalidation rules
- duplicate-truth controls for registry/report/memory-vault overlap

## Known Debt

- `DEBT-SPEC-LEGACY-MCP-GUIDE`
- `DEBT-AIWG-COUNTING-SEMANTICS`

## Remaining Risks

- Legacy docs still reference missing specs and can inflate false negatives in validation.
- Several artifact types are not yet materialized and remain governance placeholders.

## Next Phase

P4 — Cognitive Artifact Protocol
