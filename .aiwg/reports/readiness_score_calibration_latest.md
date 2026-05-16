# Readiness Score Calibration Report

**Decision:** PASS_WITH_WARNINGS
**Generated At:** 2026-05-16T16:16:27Z

## Calibrated Scores (0-10)

- **daily_use_readiness:** 2.50
- **memory_spine_readiness:** 2.50
- **token_economy_readiness:** 8.50
- **entrypoint_sovereignty_readiness:** 6.00
- **autonomy_readiness:** 0.00

## Findings

### [HIGH] score_1_with_degraded_kuzu
- **Description:** Kuzu/4D-TES persistence is DEGRADED. No physical graph writes occur.
- **Impact:** Memory Spine is logical-only. Causal retrieval depends on file parsing.
- **Penalty:** -3.5

### [MEDIUM] score_1_with_partial_context_coverage
- **Description:** Partial context coverage: 177 missing runtime tests.
- **Impact:** Validation integrity is not absolute.
- **Penalty:** -2.0

### [HIGH] score_1_without_entrypoint_memory_retrieval
- **Description:** DUMMIE Chat CLI does not retrieve causal memory before response.
- **Impact:** Chat remains stateless/amnesic despite memory spine availability.
- **Penalty:** -4.0

### [MEDIUM] score_1_without_token_benchmark_evidence
- **Description:** No empirical token economy benchmark exists.
- **Impact:** Context strategy ROI is asserted but not measured.
- **Penalty:** -1.5

