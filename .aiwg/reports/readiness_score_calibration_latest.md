# Readiness Score Calibration Report

**Decision:** PASS_WITH_WARNINGS
**Generated At:** 2026-05-16T16:42:32Z

## Calibrated Scores (0-10)

- **daily_use_readiness:** 6.50
- **memory_spine_readiness:** 6.50
- **token_economy_readiness:** 10.00
- **entrypoint_sovereignty_readiness:** 10.00
- **autonomy_readiness:** 2.50

## Findings

### [HIGH] score_1_with_degraded_kuzu
- **Description:** Kuzu/4D-TES persistence is DEGRADED. No physical graph writes occur.
- **Impact:** Memory Spine is logical-only. Causal retrieval depends on file parsing.
- **Penalty:** -3.5

### [MEDIUM] score_1_with_partial_context_coverage
- **Description:** Partial context coverage: 177 missing runtime tests.
- **Impact:** Validation integrity is not absolute.
- **Penalty:** -2.0

