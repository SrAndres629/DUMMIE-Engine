# Evolution Blindspot Audit — Pack 2.3 Ready

- repo_health_status: FAIL
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

## Targets Still HIGH Due Toolchain
- none

## Targets With Executable Evidence
- layers/l0_overseer/lib/overseer/application.ex | decision=CONTRACT_BOUND | risk_after=MEDIUM
- layers/l1_nervous/internal/skill/blueprint.go | decision=TOOLCHAIN_VALIDATED | risk_after=MEDIUM
- layers/l1_nervous/internal/skill/mcp_client.go | decision=TOOLCHAIN_VALIDATED | risk_after=MEDIUM
- layers/l1_nervous/internal/skill/types.go | decision=TOOLCHAIN_VALIDATED | risk_after=MEDIUM
- layers/l1_nervous/sidecar.go | decision=TOOLCHAIN_VALIDATED | risk_after=MEDIUM
- layers/l1_nervous/ssh_sandbox_wrapper.sh | decision=TOOLCHAIN_VALIDATED | risk_after=MEDIUM
- layers/l1_nervous/tools_impl/nervous.py | decision=CONTRACT_BOUND | risk_after=MEDIUM

## Tests Still Superficial (Heuristic)
- count: 13
- layers/l2_brain/tests/test_six_dimensional_context_runtime.py | asserts=0 | skips=0
- layers/l2_brain/tests/test_daemon_gateway_heartbeat_bridge.py | asserts=0 | skips=0
- layers/l2_brain/tests/test_embedding_memory_router.py | asserts=0 | skips=0
- layers/l2_brain/tests/test_semantic_hardening_index.py | asserts=48 | skips=0
- layers/l2_brain/tests/conftest.py | asserts=0 | skips=0
- doc/.deprecated/scratchpad/test_kuzu.py | asserts=0 | skips=0
- layers/l1_nervous/tests/test_swarm_perf_run.py | asserts=0 | skips=0
- layers/l1_nervous/tests/conftest.py | asserts=0 | skips=0
- layers/l1_nervous/tests/industrial/test_observe_swarm_perf.py | asserts=0 | skips=0
- layers/l2_brain/tests/test_polyglot_probe_orchestrator.py | asserts=0 | skips=0
- layers/l2_brain/tests/test_context_packet_optimizer.py | asserts=0 | skips=0
- layers/l2_brain/tests/test_cognitive_bias_detector.py | asserts=1 | skips=0

## Files Not Fully Analyzed
- count: 0

## Scoped-Only Spec Links
- count: 20
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
1. Raise direct_spec_hit_rate for the 20 remaining Batch 1 L2 candidates before changing physical files.
2. Convert the top 10 superficial tests into behavior assertions with invariant checks.
3. Classify the most-imported UNKNOWN files in L0/L1 first to reduce uncertainty fastest.
4. Resolve the 3 orphan tests with explicit runtime or legacy evidence.
5. Track root Go module failure as visible debt until the package layout is fixed intentionally.
6. Split scoped-only spec links into direct module evidence for runtime-critical surfaces.
7. Add freshness gates so reports must match HEAD at generation time.
8. Prepare Pack 2.3 batch runners with rollback and done-criteria per file set.
9. Keep shellcheck in the verification loop so wrapper regressions do not reappear.
10. Use the validated batch plan as the only source of execution order; do not improvise mid-pack.

## Risks If Advancing Too Fast
- Treating scoped-only spec coverage as direct module evidence can overstate readiness.
- Ignoring root Go module failure can hide integration debt behind local package green checks.
- Reclassifying UNKNOWN to LEGACY without evidence destroys auditability.
- Running Pack 2.3 before freshness gates are obeyed creates stale-report drift.
- Batching too many runtime surfaces without behavior tests can preserve shallow green status.

## Next Phase
Structural Hardening Pack 2.3 - High-Risk Runtime Contract Deepening
