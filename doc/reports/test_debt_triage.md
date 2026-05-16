# 🔬 Detailed Test Debt Triage Report

**Total Passed:** 450
**Total Failures:** 19 files (36 tests)
**Total Errors:** 1 files

## ❌ Blocked (Errors)
| File | Category | Note |
| :--- | :--- | :--- |
| layers/l2_brain/tests/test_industrial_phases.py | Contract Drift | Bridge/Orchestrator integration mismatch |

## ⚠️ Failing (Logic/Drift)
| File | Category | Note |
| :--- | :--- | :--- |
| layers/l2_brain/tests/infrastructure/test_kuzu_path_hardening.py | Infrastructure | Kuzu/Path hardening constraints |
| layers/l2_brain/tests/infrastructure/test_kuzu_repository.py | Infrastructure | Kuzu/Path hardening constraints |
| layers/l2_brain/tests/test_adapters_cypher_injection.py | Needs Investigation | Review logic |
| layers/l2_brain/tests/test_architectural_boundaries.py | Contract Drift | Shield/Auditor API changes |
| layers/l2_brain/tests/test_auto_evolution.py | Needs Investigation | Review logic |
| layers/l2_brain/tests/test_causal_integrity.py | Needs Investigation | Review logic |
| layers/l2_brain/tests/test_cognitive_loop_e2e.py | Needs Investigation | Review logic |
| layers/l2_brain/tests/test_daemon_causal_gates.py | Needs Investigation | Review logic |
| layers/l2_brain/tests/test_daemon_cognitive_preflight.py | Needs Investigation | Review logic |
| layers/l2_brain/tests/test_daemon_hierarchical_planner.py | Needs Investigation | Review logic |
| layers/l2_brain/tests/test_graph_traversal.py | Needs Investigation | Review logic |
| layers/l2_brain/tests/test_local_reasoning.py | Contract Drift | DeterministicReasoningProvider API changes |
| layers/l2_brain/tests/test_metacognitive_pipeline.py | Logic Drift | Authority levels or pipeline flow mismatch |
| layers/l2_brain/tests/test_metagateway_hardening.py | Needs Investigation | Review logic |
| layers/l2_brain/tests/test_pattern_miner.py | Logic Drift | PatternMiner detection rules changed |
| layers/l2_brain/tests/test_pattern_to_mission_loop.py | Needs Investigation | Review logic |
| layers/l2_brain/tests/test_repository_retrieval_paths.py | Needs Investigation | Review logic |
| layers/l2_brain/tests/test_self_programming.py | Logic Drift | Autonomous logic drift |
| layers/l2_brain/tests/test_self_worktree_orchestrator.py | Needs Investigation | Review logic |
