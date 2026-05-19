# DUMMIE Engine - Semantic Hardening Matrix

## Status Calibration
- pack_status: PASS_WITH_WARNINGS
- repo_health_status: FAIL
- index_mode: deterministic_index_mode
- semantic_mode: degraded_semantic_mode

## Summary Counts
- files_scanned: 1379
- files_indexed: 1362
- degraded_embeddings: 717
- excluded_files_count: 120956
- excluded_dirs_count: 11943
- indexed_first_party_files: 1316
- indexed_legacy_files: 21
- indexed_generated_files: 25
- indexed_vendor_files: 0
- vector_spaces_used: fallback_hash_384, none, text_fast_bge_small_384
- active_runtime_candidates: 203
- shadow_candidates: 139
- orphan_test_candidates: 244
- generated_candidates: 25
- legacy_candidates: 21

## Exclusion Metrics
- binary: 4
- exclude_dir: 97114
- exclude_prefix: 7364
- not_included: 16461
- too_large: 13

## Top risks
- medium: needs_test (565)
- medium: map_to_runtime (244)
- low: keep_and_test (172)
- high: map_to_spec (139)
- medium: map_to_spec (110)
- medium: move_to_legacy (85)
- low: mark_generated (25)
- medium: archive_or_delete_later (21)
- medium: needs_security_review (1)

## Top 20 hardening actions
1. map_to_spec | layers/__init__.py | risk=high | class=SHADOW_CANDIDATE
2. map_to_spec | layers/l0_overseer/__init__.py | risk=high | class=SHADOW_CANDIDATE
3. map_to_spec | layers/l0_overseer/cmd/dummied/main_test.go | risk=high | class=SHADOW_CANDIDATE
4. map_to_spec | layers/l0_overseer/internal/orchestrator/integrity_test.go | risk=high | class=SHADOW_CANDIDATE
5. map_to_spec | layers/l0_overseer/internal/orchestrator/security_test.go | risk=high | class=SHADOW_CANDIDATE
6. map_to_spec | layers/l0_overseer/internal/orchestrator/skills.go | risk=high | class=SHADOW_CANDIDATE
7. map_to_spec | layers/l0_overseer/internal/orchestrator/socket_path.go | risk=high | class=SHADOW_CANDIDATE
8. map_to_spec | layers/l0_overseer/internal/orchestrator/socket_path_test.go | risk=high | class=SHADOW_CANDIDATE
9. map_to_spec | layers/l0_overseer/lib/overseer/application.ex | risk=high | class=SHADOW_CANDIDATE
10. map_to_spec | layers/l0_overseer/lib/proto/proto/dummie/v2/core.pb.ex | risk=high | class=SHADOW_CANDIDATE
11. map_to_spec | layers/l0_overseer/lib/proto/proto/dummie/v2/memory.pb.ex | risk=high | class=SHADOW_CANDIDATE
12. map_to_spec | layers/l0_overseer/lib/proto/proto/dummie/v2/orchestration.pb.ex | risk=high | class=SHADOW_CANDIDATE
13. map_to_spec | layers/l0_overseer/mix.exs | risk=high | class=SHADOW_CANDIDATE
14. map_to_spec | layers/l0_overseer/supervisor.py | risk=high | class=SHADOW_CANDIDATE
15. map_to_spec | layers/l0_overseer/test/overseer_ipc_test.exs | risk=high | class=SHADOW_CANDIDATE
16. map_to_spec | layers/l1_nervous/__init__.py | risk=high | class=SHADOW_CANDIDATE
17. map_to_spec | layers/l1_nervous/application/__init__.py | risk=high | class=SHADOW_CANDIDATE
18. map_to_spec | layers/l1_nervous/application/use_cases.py | risk=high | class=SHADOW_CANDIDATE
19. map_to_spec | layers/l1_nervous/bootstrap.py | risk=high | class=SHADOW_CANDIDATE
20. map_to_spec | layers/l1_nervous/compressive_memory.py | risk=high | class=SHADOW_CANDIDATE

## Next recommended phase
ready_for_structural_hardening_input — Structural Hardening Pack 2: contract enforcement and targeted cleanup of high/medium-risk modules.

## Explicit limitations
- Reranker is deterministic hybrid fallback (no ML cross-encoder wired in this phase).
- Non-TEXT_FAST capabilities are placeholder providers with deterministic fallback.
- Repo index is JSON-based in this phase; no external vector DB integration.
