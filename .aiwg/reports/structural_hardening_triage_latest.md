# Structural Hardening Pack 2 - Contract-First Triage

## Status
- pack_status: PASS_WITH_WARNINGS
- repo_health_status: FAIL
- base_commit: f5029ba306f5e89ffc1ce64819effeffa254d7ae
- analysis_base_commit: f5029ba306f5e89ffc1ce64819effeffa254d7ae
- report_generated_at_commit: f5029ba306f5e89ffc1ce64819effeffa254d7ae
- head_commit: f5029ba306f5e89ffc1ce64819effeffa254d7ae
- files_analyzed: 1362

## Explicit Metrics
- CRITICAL: 0
- HIGH: 50
- SHADOW_CANDIDATE: 50
- ORPHAN_TEST_CANDIDATE: 0
- bound_active_runtime: 31
- deferred_no_safe_action: 0
- toolchain_validated: 5
- toolchain_missing: 0
- smoke_passed: 0
- smoke_failed: 0
- contract_bound: 2
- repo_health_status: FAIL

## Counts by Class
- ACTIVE_RUNTIME: 281
- ACTIVE_SPEC: 634
- ACTIVE_TEST: 243
- CONFIG: 72
- EXPERIMENTAL: 1
- GENERATED: 42
- LEGACY: 30
- ORPHAN_TEST_CANDIDATE: 0
- REPORT: 9
- SHADOW_CANDIDATE: 50
- UNKNOWN: 0

## Counts by Recommendation
- KEEP_AND_TEST: 267
- MAP_TO_RUNTIME: 629
- MAP_TO_SPEC: 269
- MAP_TO_TEST: 18
- MARK_EXPERIMENTAL: 1
- MARK_GENERATED: 42
- MARK_LEGACY: 20
- NO_ACTION: 116

## Bindings Summary
- bound_active_runtime: 31
- needs_manual_owner: 0
- deferred_no_safe_action: 0
- toolchain_validated: 5
- toolchain_missing: 0
- smoke_passed: 0
- smoke_failed: 0
- contract_bound: 2

## Counts by Risk
- CRITICAL: 0
- HIGH: 50
- LOW: 418
- MEDIUM: 894

## Top 30 High-Risk Actions
1. layers/l2_brain/golden_path.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
2. layers/l2_brain/human_intent.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
3. layers/l2_brain/infrastructure/adapters/external.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
4. layers/l2_brain/infrastructure/semantic_adapters.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
5. layers/l2_brain/lifecycle_integration_mapper.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
6. layers/l2_brain/metacognition/deliberation_hooks.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
7. layers/l2_brain/metacognition/input_hooks.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
8. layers/l2_brain/metacognition/output_hooks.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
9. layers/l2_brain/metacognition/reasoning_hooks.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
10. layers/l2_brain/metacognition/semantic_hooks.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
11. layers/l2_brain/metagateway_adapter.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
12. layers/l2_brain/metagateway_benchmark.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
13. layers/l2_brain/model_discovery.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
14. layers/l2_brain/model_executor.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
15. layers/l2_brain/nervous_pulse.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
16. layers/l2_brain/neuron_ledger.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
17. layers/l2_brain/observability.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
18. layers/l2_brain/operational_truth_collectors.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
19. layers/l2_brain/operationalization_pack_2_runner.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
20. layers/l2_brain/prompt_preprocessor.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
21. layers/l2_brain/safe_fallbacks.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
22. layers/l2_brain/sdk/client.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
23. layers/l2_brain/semantic_cache.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
24. layers/l2_brain/semantic_graph_rag.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
25. layers/l2_brain/skill_binder.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
26. layers/l2_brain/source_of_truth_conflict_detector.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
27. layers/l2_brain/spec_frontmatter_repair.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
28. layers/l2_brain/src/brain/application/interfaces.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
29. layers/l2_brain/src/brain/application/use_cases/crystallization.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
30. layers/l2_brain/src/brain/application/use_cases/lessons_use_case.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84

## False-Positive Corrections
- init_runtime_low_risk_corrections: 25

## Frozen / No-Touch Candidates
- frozen_count: 1
- layers/l4_ext/shannon_entropy_mock.py | MARK_EXPERIMENTAL | risk=MEDIUM

## Generated / Legacy Summary
- generated: 42
- legacy: 30

## Orphan Test Candidates
- orphan_test_candidates: 0
- shadow_candidates: 50

## Next Phase
Structural Hardening Pack 2.3 - Compilation Sandbox and Orchestration Boundary Hardening

## Limitations
- Deterministic evidence only; no embedding or ML-based reasoning used.
- No physical file moves/deletes performed in this phase.
- Classification depends on currently indexed artifacts and deterministic references.
