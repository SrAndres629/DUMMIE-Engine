# Evolution Blindspot Audit — Pack 2.2

## Status
- repo_health_status: FAIL
- CRITICAL: 0
- HIGH: 65
- SHADOW_CANDIDATE: 65
- ORPHAN_TEST_CANDIDATE: 3
- bound_active_runtime: 11
- deferred_no_safe_action: 0
- toolchain_validated: 4
- toolchain_missing: 1
- smoke_passed: 0
- smoke_failed: 0
- contract_bound: 2

## Targets Still HIGH Due Toolchain
- layers/l1_nervous/ssh_sandbox_wrapper.sh | decision=TOOLCHAIN_MISSING | command=`bash -n layers/l1_nervous/ssh_sandbox_wrapper.sh` | result=shellcheck missing; fallback bash -n passed [see shell_probe_pack_2_2_latest.log].

## Targets With Executable Evidence
- layers/l0_overseer/lib/overseer/application.ex | decision=CONTRACT_BOUND | risk_after=MEDIUM
- layers/l1_nervous/internal/skill/blueprint.go | decision=TOOLCHAIN_VALIDATED | risk_after=MEDIUM
- layers/l1_nervous/internal/skill/mcp_client.go | decision=TOOLCHAIN_VALIDATED | risk_after=MEDIUM
- layers/l1_nervous/internal/skill/types.go | decision=TOOLCHAIN_VALIDATED | risk_after=MEDIUM
- layers/l1_nervous/sidecar.go | decision=TOOLCHAIN_VALIDATED | risk_after=MEDIUM
- layers/l1_nervous/tools_impl/nervous.py | decision=CONTRACT_BOUND | risk_after=MEDIUM

## Tests Still Superficial (Heuristic)
- count: 13
- layers/l2_brain/tests/test_embedding_memory_router.py | asserts=0 | skips=0
- layers/l2_brain/tests/test_polyglot_probe_orchestrator.py | asserts=0 | skips=0
- layers/l1_nervous/tests/industrial/test_observe_swarm_perf.py | asserts=0 | skips=0
- layers/l2_brain/tests/test_cognitive_bias_detector.py | asserts=1 | skips=0
- layers/l2_brain/tests/test_four_dtes_persistence_preflight.py | asserts=0 | skips=0
- doc/.deprecated/scratchpad/test_kuzu.py | asserts=0 | skips=0
- layers/l1_nervous/tests/conftest.py | asserts=0 | skips=0
- layers/l2_brain/tests/test_daemon_gateway_heartbeat_bridge.py | asserts=0 | skips=0
- layers/l1_nervous/tests/test_swarm_perf_run.py | asserts=0 | skips=0
- layers/l2_brain/tests/test_six_dimensional_context_runtime.py | asserts=0 | skips=0
- layers/l2_brain/tests/test_semantic_hardening_index.py | asserts=48 | skips=0
- layers/l2_brain/tests/conftest.py | asserts=0 | skips=0

## Files Not Fully Analyzed
- count: 0

## Scoped-Only Spec Links
- count: 17
- layers/l1_nervous/bootstrap.py | status=BOUND_ACTIVE_RUNTIME | scoped_hits=4 | direct_hits=0
- layers/l1_nervous/application/use_cases.py | status=BOUND_ACTIVE_RUNTIME | scoped_hits=4 | direct_hits=0
- layers/l1_nervous/domain/services.py | status=BOUND_ACTIVE_RUNTIME | scoped_hits=4 | direct_hits=0
- layers/l1_nervous/knowledge_adapters.py | status=BOUND_ACTIVE_RUNTIME | scoped_hits=4 | direct_hits=0
- layers/l1_nervous/mcp_registry.py | status=BOUND_ACTIVE_RUNTIME | scoped_hits=4 | direct_hits=0
- layers/l1_nervous/mcp_transport.py | status=BOUND_ACTIVE_RUNTIME | scoped_hits=4 | direct_hits=0
- layers/l1_nervous/repo_guard.py | status=BOUND_ACTIVE_RUNTIME | scoped_hits=4 | direct_hits=0
- layers/l1_nervous/runtime_paths.py | status=BOUND_ACTIVE_RUNTIME | scoped_hits=5 | direct_hits=0
- layers/l1_nervous/tools_impl/nervous.py | status=CONTRACT_BOUND | scoped_hits=2 | direct_hits=0
- layers/l1_nervous/tools_impl/patch_transactions.py | status=BOUND_ACTIVE_RUNTIME | scoped_hits=4 | direct_hits=0
- layers/l1_nervous/utils.py | status=BOUND_ACTIVE_RUNTIME | scoped_hits=4 | direct_hits=0
- layers/l0_overseer/supervisor.py | status=BOUND_ACTIVE_RUNTIME | scoped_hits=3 | direct_hits=0

## Debt Lowered But Not Closed
- count: 18
- layers/l1_nervous/bootstrap.py | status=BOUND_ACTIVE_RUNTIME | risk_after=MEDIUM
- layers/l1_nervous/application/use_cases.py | status=BOUND_ACTIVE_RUNTIME | risk_after=MEDIUM
- layers/l1_nervous/domain/services.py | status=BOUND_ACTIVE_RUNTIME | risk_after=MEDIUM
- layers/l1_nervous/knowledge_adapters.py | status=BOUND_ACTIVE_RUNTIME | risk_after=MEDIUM
- layers/l1_nervous/mcp_registry.py | status=BOUND_ACTIVE_RUNTIME | risk_after=MEDIUM
- layers/l1_nervous/mcp_transport.py | status=BOUND_ACTIVE_RUNTIME | risk_after=MEDIUM
- layers/l1_nervous/repo_guard.py | status=BOUND_ACTIVE_RUNTIME | risk_after=MEDIUM
- layers/l1_nervous/runtime_paths.py | status=BOUND_ACTIVE_RUNTIME | risk_after=MEDIUM
- layers/l1_nervous/tools_impl/nervous.py | status=CONTRACT_BOUND | risk_after=MEDIUM
- layers/l1_nervous/tools_impl/patch_transactions.py | status=BOUND_ACTIVE_RUNTIME | risk_after=MEDIUM
- layers/l1_nervous/utils.py | status=BOUND_ACTIVE_RUNTIME | risk_after=MEDIUM
- layers/l0_overseer/supervisor.py | status=BOUND_ACTIVE_RUNTIME | risk_after=MEDIUM

## Next 10 Objectives
1. Resolve shell toolchain gap: install and run shellcheck on ssh_sandbox_wrapper.sh to remove TOOLCHAIN_MISSING.
2. Fix L1 root Go module blockers (AuthorityLevel/proto init + duplicated main) so go test ./... becomes actionable.
3. Add direct module-level spec links for 7 polyglot targets currently scoped-only.
4. Promote internal/skill Go probes from compile-only to behavior tests with deterministic assertions.
5. Add FastMCP double test for register_nervous_tools to validate tool registration behavior, not only shape/signature.
6. Add triage freshness gate in CI/local pre-commit to fail stale base_commit/head_commit mismatches.
7. Reconcile 3 ORPHAN_TEST_CANDIDATE files with runtime mapping or explicit freeze rationale.
8. Reduce UNKNOWN backlog (143) using import fan-in prioritization and owner assignment.
9. Add provenance field in ledger entries (log path + exit code) for audit-grade replayability.
10. Prepare Pack 2.3 action plan constrained to highest-value HIGH risks with executable commands.

## Risks If Advancing Too Fast
- Treating compile-only checks as full runtime validation can mask integration breakage.
- Keeping scoped-only specs without direct module references inflates confidence.
- Global Go module failures can hide in per-package green probes if not tracked explicitly.
- Toolchain gaps (shellcheck missing) can persist indefinitely without explicit install/verify commands.
- Behavioral gaps in optional-dependency modules can pass import contracts but fail at runtime.

## Next Phase
Structural Hardening Pack 2.3 - High-Risk Runtime Contract Deepening
