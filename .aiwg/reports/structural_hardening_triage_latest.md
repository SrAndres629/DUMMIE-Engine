# Structural Hardening Pack 2 - Contract-First Triage

## Status
- pack_status: PASS_WITH_WARNINGS
- repo_health_status: FAIL
- base_commit: 05c11513ea9eb3ed3373e01029a54fa770e4106b
- files_analyzed: 1351

## Counts by Class
- ACTIVE_RUNTIME: 241
- ACTIVE_SPEC: 559
- ACTIVE_TEST: 238
- CONFIG: 12
- EXPERIMENTAL: 1
- GENERATED: 38
- LEGACY: 30
- ORPHAN_TEST_CANDIDATE: 3
- SHADOW_CANDIDATE: 84
- UNKNOWN: 145

## Counts by Recommendation
- FREEZE_UNTIL_REVIEW: 145
- KEEP_AND_TEST: 252
- MAP_TO_RUNTIME: 561
- MAP_TO_SPEC: 249
- MAP_TO_TEST: 20
- MARK_EXPERIMENTAL: 1
- MARK_GENERATED: 38
- MARK_LEGACY: 30
- NEEDS_OWNER: 18
- NO_ACTION: 37

## Counts by Risk
- CRITICAL: 18
- HIGH: 66
- LOW: 327
- MEDIUM: 940

## Top 30 High-Risk Actions
1. layers/l0_overseer/lib/overseer/application.ex | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
2. layers/l0_overseer/supervisor.py | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
3. layers/l1_nervous/application/use_cases.py | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
4. layers/l1_nervous/bootstrap.py | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
5. layers/l1_nervous/domain/services.py | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
6. layers/l1_nervous/internal/skill/blueprint.go | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
7. layers/l1_nervous/internal/skill/mcp_client.go | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
8. layers/l1_nervous/internal/skill/types.go | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
9. layers/l1_nervous/knowledge_adapters.py | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
10. layers/l1_nervous/mcp_registry.py | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
11. layers/l1_nervous/mcp_transport.py | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
12. layers/l1_nervous/repo_guard.py | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
13. layers/l1_nervous/runtime_paths.py | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
14. layers/l1_nervous/sidecar.go | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
15. layers/l1_nervous/ssh_sandbox_wrapper.sh | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
16. layers/l1_nervous/tools_impl/nervous.py | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
17. layers/l1_nervous/tools_impl/patch_transactions.py | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
18. layers/l1_nervous/utils.py | proposed=SHADOW_CANDIDATE | risk=CRITICAL | rec=NEEDS_OWNER | confidence=0.84
19. layers/l2_brain/action_graph.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
20. layers/l2_brain/application/cognitive/use_cases.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
21. layers/l2_brain/ast_indexer.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
22. layers/l2_brain/auditor_port.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
23. layers/l2_brain/branch_memory.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
24. layers/l2_brain/cognition/pattern_miner_v2.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
25. layers/l2_brain/context_circulation_runtime.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
26. layers/l2_brain/cypher_codec.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
27. layers/l2_brain/domain/dtos.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
28. layers/l2_brain/domain/hypothesis_service.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
29. layers/l2_brain/domain/reasoning_logic.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84
30. layers/l2_brain/domain/retrieval_service.py | proposed=SHADOW_CANDIDATE | risk=HIGH | rec=MAP_TO_SPEC | confidence=0.84

## False-Positive Corrections
- init_runtime_low_risk_corrections: 25

## Frozen / No-Touch Candidates
- frozen_count: 146
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
- scripts/build_structural_hardening_triage.py | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/consciousness_audit.py | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/context_oracle.py | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/dummie-ctl | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/dummie-doctor-repair.sh | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/dummie-engine.service | FREEZE_UNTIL_REVIEW | risk=MEDIUM
- scripts/dummie_mcp_doctor.py | FREEZE_UNTIL_REVIEW | risk=MEDIUM

## Generated / Legacy Summary
- generated: 38
- legacy: 30

## Orphan Test Candidates
- orphan_test_candidates: 3
- shadow_candidates: 84

## Next Phase
Structural Hardening Pack 2.1 - targeted contract binding and safe physical changes

## Limitations
- Deterministic evidence only; no embedding or ML-based reasoning used.
- No physical file moves/deletes performed in this phase.
- Classification depends on currently indexed artifacts and deterministic references.
