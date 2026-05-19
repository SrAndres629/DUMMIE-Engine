# DUMMIE Engine - Structural Hardening Triage Report

## Status Calibration
- pack_name: Structural Hardening Pack 2
- pack_status: triage_completed
- repo_health_status: FAIL
- base_commit: 894978ba00bc6324408fe01d30aa5a620c165dd4
- generated_at: 2026-05-19T00:01:35.759683Z
- files_analyzed: 1340

## Summary Counts by Structural Class
- ACTIVE_RUNTIME: 187
- ACTIVE_SPEC: 515
- ACTIVE_TEST: 135
- CONFIG: 8
- EXPERIMENTAL: 1
- GENERATED: 35
- LEGACY: 29
- ORPHAN_TEST_CANDIDATE: 86
- REPORT: 0
- SHADOW_CANDIDATE: 176
- UNKNOWN: 168

## Summary Counts by Recommendation
- FREEZE_UNTIL_REVIEW: 0
- KEEP_AND_TEST: 712
- MAP_TO_RUNTIME: 86
- MAP_TO_SPEC: 57
- MAP_TO_TEST: 44
- MARK_EXPERIMENTAL: 1
- MARK_GENERATED: 35
- MARK_LEGACY: 29
- NEEDS_DOC_CONTRACT: 0
- NEEDS_IMPORT_CHECK: 168
- NEEDS_OWNER: 176
- NEEDS_SECURITY_REVIEW: 0
- NO_ACTION: 32

## Summary Counts by Risk Level
- CRITICAL: 0
- HIGH: 176
- LOW: 977
- MEDIUM: 187

## False-Positive Corrections
- empty_init_packaging_glue_active: 24 (Classified as ACTIVE_RUNTIME with LOW risk to avoid shadow candidate bloat.)

## Top Unresolved High-Risk Actions
Refer to structural_hardening_actions_latest.md for full descriptive details.
- total_high_risk_actions: 363

## Limitations & Heuristics
- Deterministic heuristic analysis only. No real embeddings used.
- Packaging __init__.py files treated as Active Runtime by design.

## Next Recommended Phase
- next_phase: Structural Hardening Pack 2.1 — Physics Cleanup