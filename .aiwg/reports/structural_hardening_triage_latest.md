# Structural Hardening Pack 2 - Contract-First Triage

## Status
- pack_status: PASS_WITH_WARNINGS
- repo_health_status: FAIL
- base_commit: 06478a1fa387c7bdbaab6b87ffc20d7ecb2e7702
- analysis_base_commit: 06478a1fa387c7bdbaab6b87ffc20d7ecb2e7702
- report_generated_at_commit: 06478a1fa387c7bdbaab6b87ffc20d7ecb2e7702
- head_commit: 06478a1fa387c7bdbaab6b87ffc20d7ecb2e7702
- files_analyzed: 1340

## Explicit Metrics
- CRITICAL: 0
- HIGH: 44
- SHADOW_CANDIDATE: 44
- ORPHAN_TEST_CANDIDATE: 3
- bound_active_runtime: 31
- deferred_no_safe_action: 0
- toolchain_validated: 5
- toolchain_missing: 0
- smoke_passed: 0
- smoke_failed: 0
- contract_bound: 2
- repo_health_status: FAIL

## Counts by Class
- ACTIVE_RUNTIME: 274
- ACTIVE_SPEC: 559
- ACTIVE_TEST: 235
- CONFIG: 12
- EXPERIMENTAL: 1
- GENERATED: 38
- LEGACY: 30
- ORPHAN_TEST_CANDIDATE: 3
- REPORT: 0
- SHADOW_CANDIDATE: 44
- UNKNOWN: 144

## Counts by Recommendation
- FREEZE_UNTIL_REVIEW: 144
- KEEP_AND_TEST: 255
- MAP_TO_RUNTIME: 561
- MAP_TO_SPEC: 255
- MAP_TO_TEST: 20
- MARK_EXPERIMENTAL: 1
- MARK_GENERATED: 38
- MARK_LEGACY: 30
- NO_ACTION: 36

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
- HIGH: 44
- LOW: 322
- MEDIUM: 974

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
- init_runtime_low_risk_corrections: 24

## Frozen / No-Touch Candidates
- frozen_count: 145
- README.md | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- doc/ATLAS.md | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- doc/CORE_SPEC.md | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- doc/ENGINEERING_PRINCIPLES.md | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- doc/PHYSICAL_MAP.md | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/install_tools_user_space.sh | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/benchmark_local_reasoning.py | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/bootstrap.sh | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/bootstrap_memory_native.sh | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/build_factory.sh | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/build_inventory.py | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/build_repo_maps.py | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/build_semantic_hardening_index.py | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/consciousness_audit.py | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/context_oracle.py | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/dummie-ctl | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/dummie-doctor-repair.sh | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/dummie-engine.service | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/dummie_mcp_doctor.py | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/dummie_orchestrator.py | FREEZE_UNTIL_REVIEW | risk=MEDIUM

## Generated / Legacy Summary
- generated: 38
- legacy: 30

## Orphan Test Candidates
- orphan_test_candidates: 3
- shadow_candidates: 44

## Next Phase
Structural Hardening Pack 2.3 - Compilation Sandbox and Orchestration Boundary Hardening

## Limitations
- Deterministic evidence only; no embedding or ML-based reasoning used.
- No physical file moves/deletes performed in this phase.
- Classification depends on currently indexed artifacts and deterministic references.
