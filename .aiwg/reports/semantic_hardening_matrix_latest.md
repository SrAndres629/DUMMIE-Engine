# DUMMIE Engine - Semantic Hardening Matrix

## Decision
FAIL

## Summary counts
- files_scanned: 4149
- files_indexed: 4069
- degraded_embeddings: 4069
- vector_spaces_used: 2
- active_runtime_candidates: 223
- shadow_candidates: 111
- orphan_test_candidates: 306
- generated_candidates: 617
- legacy_candidates: 1152

## Top risks
- medium: archive_or_delete_later (1152)
- medium: move_to_legacy (1041)
- low: mark_generated (617)
- medium: needs_test (565)
- medium: map_to_runtime (306)
- low: keep_and_test (146)
- medium: map_to_spec (130)
- high: map_to_spec (111)
- medium: needs_security_review (1)

## Top 20 hardening actions
1. map_to_spec | layers/l0_overseer/cmd/dummied/main_test.go | risk=high | class=SHADOW_CANDIDATE
2. map_to_spec | layers/l0_overseer/internal/orchestrator/integrity_test.go | risk=high | class=SHADOW_CANDIDATE
3. map_to_spec | layers/l0_overseer/internal/orchestrator/security_test.go | risk=high | class=SHADOW_CANDIDATE
4. map_to_spec | layers/l0_overseer/internal/orchestrator/skills.go | risk=high | class=SHADOW_CANDIDATE
5. map_to_spec | layers/l0_overseer/internal/orchestrator/socket_path.go | risk=high | class=SHADOW_CANDIDATE
6. map_to_spec | layers/l0_overseer/internal/orchestrator/socket_path_test.go | risk=high | class=SHADOW_CANDIDATE
7. map_to_spec | layers/l0_overseer/lib/overseer/application.ex | risk=high | class=SHADOW_CANDIDATE
8. map_to_spec | layers/l0_overseer/lib/proto/proto/dummie/v2/core.pb.ex | risk=high | class=SHADOW_CANDIDATE
9. map_to_spec | layers/l0_overseer/lib/proto/proto/dummie/v2/memory.pb.ex | risk=high | class=SHADOW_CANDIDATE
10. map_to_spec | layers/l0_overseer/lib/proto/proto/dummie/v2/orchestration.pb.ex | risk=high | class=SHADOW_CANDIDATE
11. map_to_spec | layers/l0_overseer/mix.exs | risk=high | class=SHADOW_CANDIDATE
12. map_to_spec | layers/l0_overseer/supervisor.py | risk=high | class=SHADOW_CANDIDATE
13. map_to_spec | layers/l0_overseer/test/overseer_ipc_test.exs | risk=high | class=SHADOW_CANDIDATE
14. map_to_spec | layers/l1_nervous/application/use_cases.py | risk=high | class=SHADOW_CANDIDATE
15. map_to_spec | layers/l1_nervous/bootstrap.py | risk=high | class=SHADOW_CANDIDATE
16. map_to_spec | layers/l1_nervous/compressive_memory.py | risk=high | class=SHADOW_CANDIDATE
17. map_to_spec | layers/l1_nervous/context_quantizer.py | risk=high | class=SHADOW_CANDIDATE
18. map_to_spec | layers/l1_nervous/domain/services.py | risk=high | class=SHADOW_CANDIDATE
19. map_to_spec | layers/l1_nervous/internal/skill/blueprint.go | risk=high | class=SHADOW_CANDIDATE
20. map_to_spec | layers/l1_nervous/internal/skill/mcp_client.go | risk=high | class=SHADOW_CANDIDATE

## Next recommended phase
Structural Hardening Pack 2: contract enforcement and targeted cleanup of high/medium-risk modules.

## Explicit limitations
- Reranker is deterministic hybrid fallback (no ML cross-encoder wired in this phase).
- Non-TEXT_FAST capabilities are placeholder providers with deterministic fallback.
- Repo index is JSON-based in this phase; no external vector DB integration.
