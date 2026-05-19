# Evolution Blindspot Audit (Post Pack 2.1)

## Snapshot
- files_analyzed: 1340
- shadow_candidates: 71
- orphan_test_candidates: 3
- unknown: 144
- critical: 0
- high: 71
- bound_active_runtime: 11
- deferred_no_safe_action: 7

## Files Not Fully Analyzed
- count: 0

## Frozen Modules (Sample)
- README.md | risk=MEDIUM | reason=insufficient structural evidence; referenced in CORE_SPEC
- doc/ATLAS.md | risk=MEDIUM | reason=insufficient structural evidence
- doc/CORE_SPEC.md | risk=MEDIUM | reason=insufficient structural evidence; referenced in PHYSICAL_MAP
- doc/ENGINEERING_PRINCIPLES.md | risk=MEDIUM | reason=insufficient structural evidence
- doc/PHYSICAL_MAP.md | risk=MEDIUM | reason=insufficient structural evidence; referenced in CORE_SPEC
- scripts/install_tools_user_space.sh | risk=MEDIUM | reason=insufficient structural evidence; spec links found
- scripts/benchmark_local_reasoning.py | risk=MEDIUM | reason=insufficient structural evidence; spec links found
- scripts/bootstrap.sh | risk=MEDIUM | reason=insufficient structural evidence
- scripts/bootstrap_memory_native.sh | risk=MEDIUM | reason=insufficient structural evidence
- scripts/build_factory.sh | risk=MEDIUM | reason=insufficient structural evidence

## Superficial Test Signals
- count: 8
- layers/l1_nervous/tests/test_swarm_perf_run.py
- layers/l2_brain/tests/test_context_packet_optimizer.py
- layers/l2_brain/tests/test_daemon_gateway_heartbeat_bridge.py
- layers/l2_brain/tests/test_embedding_memory_router.py
- layers/l2_brain/tests/test_four_dtes_persistence_preflight.py
- layers/l2_brain/tests/test_polyglot_probe_orchestrator.py
- layers/l2_brain/tests/test_semantic_hardening_index.py
- layers/l2_brain/tests/test_six_dimensional_context_runtime.py

## Generic Spec Linkage Signals
- count: 11
- layers/l1_nervous/bootstrap.py | direct_spec_hits=0 | scoped_hits=4 | test_hits=1
- layers/l1_nervous/application/use_cases.py | direct_spec_hits=0 | scoped_hits=4 | test_hits=1
- layers/l1_nervous/domain/services.py | direct_spec_hits=0 | scoped_hits=4 | test_hits=1
- layers/l1_nervous/knowledge_adapters.py | direct_spec_hits=0 | scoped_hits=4 | test_hits=2
- layers/l1_nervous/mcp_registry.py | direct_spec_hits=0 | scoped_hits=4 | test_hits=1
- layers/l1_nervous/mcp_transport.py | direct_spec_hits=0 | scoped_hits=4 | test_hits=1
- layers/l1_nervous/repo_guard.py | direct_spec_hits=0 | scoped_hits=4 | test_hits=1
- layers/l1_nervous/runtime_paths.py | direct_spec_hits=0 | scoped_hits=5 | test_hits=2

## Debt Lowered But Not Closed
- count: 18
- layers/l1_nervous/bootstrap.py | risk_after=MEDIUM | status=BOUND_ACTIVE_RUNTIME | action=MAP_TO_SPEC
- layers/l1_nervous/application/use_cases.py | risk_after=MEDIUM | status=BOUND_ACTIVE_RUNTIME | action=MAP_TO_SPEC
- layers/l1_nervous/domain/services.py | risk_after=MEDIUM | status=BOUND_ACTIVE_RUNTIME | action=MAP_TO_SPEC
- layers/l1_nervous/knowledge_adapters.py | risk_after=MEDIUM | status=BOUND_ACTIVE_RUNTIME | action=MAP_TO_SPEC
- layers/l1_nervous/mcp_registry.py | risk_after=MEDIUM | status=BOUND_ACTIVE_RUNTIME | action=MAP_TO_SPEC
- layers/l1_nervous/mcp_transport.py | risk_after=MEDIUM | status=BOUND_ACTIVE_RUNTIME | action=MAP_TO_SPEC
- layers/l1_nervous/repo_guard.py | risk_after=MEDIUM | status=BOUND_ACTIVE_RUNTIME | action=MAP_TO_SPEC
- layers/l1_nervous/runtime_paths.py | risk_after=MEDIUM | status=BOUND_ACTIVE_RUNTIME | action=MAP_TO_SPEC
- layers/l1_nervous/tools_impl/nervous.py | risk_after=HIGH | status=DEFERRED_NO_SAFE_ACTION | action=FREEZE_UNTIL_REVIEW
- layers/l1_nervous/tools_impl/patch_transactions.py | risk_after=MEDIUM | status=BOUND_ACTIVE_RUNTIME | action=MAP_TO_SPEC
- layers/l1_nervous/utils.py | risk_after=MEDIUM | status=BOUND_ACTIVE_RUNTIME | action=MAP_TO_SPEC
- layers/l0_overseer/supervisor.py | risk_after=MEDIUM | status=BOUND_ACTIVE_RUNTIME | action=MAP_TO_SPEC

## Top 10 Objectives
1. Bind deferred polyglot files to executable toolchain checks (go test/mix test/shellcheck) without moving files.
2. Add direct file-level spec evidence for 11 BOUND_ACTIVE_RUNTIME modules; reduce scoped-only spec linkage.
3. Replace import-only L1 contract tests with behavior contracts for bootstrap/runtime_paths/mcp transport primitives.
4. Add contract tests for repo_guard invariants (non-destructive git guardrails).
5. Add deterministic smoke checks for sidecar.go and internal/skill/*.go entrypoints in CI-like local probe.
6. Classify UNKNOWN (144) by highest fan-in imports first to reduce ambiguous runtime surface.
7. Add orphan test reconciliation for the 3 ORPHAN_TEST_CANDIDATE files with runtime mapping evidence.
8. Introduce report freshness gate: fail if base_commit != HEAD when reports are regenerated.
9. Add binding quality metric (direct_spec_hit_rate) to triage summary for anti-overclaiming.
10. Generate Pack 2.2 action ledger with owners, evidence command, and done-definition per deferred file.

## Risks If We Move Too Fast
- Premature physical cleanup can orphan polyglot runtime contracts and hide real ownership debt.
- Import-only test green status may mask runtime regressions until integration time.
- Scoped spec links without direct module evidence can overstate readiness and mis-prioritize hardening.
- Skipping deferred toolchain validation keeps HIGH risk latent in L0/L1 execution boundary.
- Regenerating reports from stale commits can create false confidence during phase handoff.

## Next Phase
Structural Hardening Pack 2.2 - Deferred Polyglot Toolchain Binding

