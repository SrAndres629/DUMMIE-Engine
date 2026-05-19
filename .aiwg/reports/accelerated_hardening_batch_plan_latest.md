# Accelerated Hardening Batch Plan (Pack 2.3)

In order to optimize developer bandwidth and mitigate the latency of iterative single-file modifications (the 7-by-7 pattern), this plan consolidates structural debt into 5 robust batch execution vectors.

---

## 📅 Summary of Batches

| Batch ID | Focus Area | Targets | Risk Before | Expected After | Estimated Blast Radius |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Batch 1** | HIGH L2 scoped-only spec bindings | 20 | `HIGH` | `MEDIUM` | `LOW` |
| **Batch 2** | Superficial tests (empty/import-only) | 10 | `MEDIUM` | `LOW` | `LOW` |
| **Batch 3** | UNKNOWN fan-in (non-python metadata) | 20 | `MEDIUM` | `LOW` | `LOW` |
| **Batch 4** | ORPHAN_TEST_CANDIDATE resolution | 3 | `MEDIUM` | `LOW` | `LOW` |
| **Batch 5** | Shellcheck / ssh_sandbox_wrapper toolchain | 1 | `HIGH` | `MEDIUM` | `LOW` |

---

## 🛠️ Detailed Batch Specification

### Batch 1 — HIGH L2 scoped-only spec bindings
- **Target Count**: 20
- **Risk Before**: `HIGH`
- **Expected Risk After**: `MEDIUM`
- **Estimated Blast Radius**: `LOW` (only updates the static binding ledger to map existing architecture)
- **Should Execute Now**: `false`
- **Targets**:
  1. `layers/l2_brain/action_graph.py`
  2. `layers/l2_brain/application/cognitive/use_cases.py`
  3. `layers/l2_brain/ast_indexer.py`
  4. `layers/l2_brain/auditor_port.py`
  5. `layers/l2_brain/branch_memory.py`
  6. `layers/l2_brain/cognition/pattern_miner_v2.py`
  7. `layers/l2_brain/context_circulation_runtime.py`
  8. `layers/l2_brain/cypher_codec.py`
  9. `layers/l2_brain/domain/dtos.py`
  10. `layers/l2_brain/domain/hypothesis_service.py`
  11. `layers/l2_brain/domain/reasoning_logic.py`
  12. `layers/l2_brain/domain/retrieval_service.py`
  13. `layers/l2_brain/domain/semantic_ports.py`
  14. `layers/l2_brain/embedding_provider.py`
  15. `layers/l2_brain/entity_voice.py`
  16. `layers/l2_brain/event_bus.py`
  17. `layers/l2_brain/evolution_feedback_loop.py`
  18. `layers/l2_brain/expansion_policy.py`
  19. `layers/l2_brain/formal_bridge.py`
  20. `layers/l2_brain/gateway_contract.py`
- **Commands**:
  ```bash
  python3 scripts/build_structural_hardening_triage.py --write-reports
  ```
- **Tests**:
  ```bash
  layers/l2_brain/.venv/bin/pytest layers/l2_brain/tests/test_structural_hardening_triage.py
  ```
- **Rollback Policy**:
  ```bash
  git checkout layers/l2_brain/structural_hardening/bindings.py
  ```
- **Done Criteria**: Every L2 shadow candidate is successfully bound to a specific contract spec or test in the registry, leaving them as `ACTIVE_RUNTIME` with downgraded risk.

---

### Batch 2 — Superficial tests
- **Target Count**: 10
- **Risk Before**: `MEDIUM`
- **Expected Risk After**: `LOW`
- **Estimated Blast Radius**: `LOW` (test files only)
- **Should Execute Now**: `false`
- **Targets**:
  1. `layers/l2_brain/tests/test_philosophical_ontology_runtime.py`
  2. `layers/l2_brain/tests/test_dialectical_reasoning_runtime.py`
  3. `layers/l2_brain/tests/test_entropy_governor.py`
  4. `layers/l2_brain/tests/test_consensus.py`
  5. `layers/l2_brain/tests/test_cognitive_bias_detector.py`
  6. `layers/l2_brain/tests/test_cognitive_frame_builder.py`
  7. `layers/l2_brain/tests/test_epistemic_state_runtime.py`
  8. `layers/l2_brain/tests/test_metacognitive_loop_runtime.py`
  9. `layers/l2_brain/tests/test_metacognitive_quality_gate.py`
  10. `layers/l2_brain/tests/test_polyglot_probe_orchestrator.py`
- **Commands**:
  ```bash
  layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_consensus.py
  ```
- **Tests**:
  ```bash
  layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/
  ```
- **Rollback Policy**:
  ```bash
  git checkout layers/l2_brain/tests/
  ```
- **Done Criteria**: At least one behavior/contract assertion per file verifying state/output instead of empty code blocks.

---

### Batch 3 — UNKNOWN fan-in
- **Target Count**: 20
- **Risk Before**: `MEDIUM`
- **Expected Risk After**: `LOW`
- **Estimated Blast Radius**: `LOW` (classification level only)
- **Should Execute Now**: `false`
- **Targets**:
  1. `layers/l5_muscle/math_ops.mojo`
  2. `layers/l5_muscle/README.md`
  3. `layers/l6_skin/index.html`
  4. `layers/l6_skin/package-lock.json`
  5. `layers/l0_overseer/api/manifest_spec.md`
  6. `layers/l0_overseer/test/overseer_ipc_test.exs`
  7. `layers/l0_overseer/test/test_helper.exs`
  8. `layers/l0_overseer/mix.exs`
  9. `layers/l0_overseer/README.md`
  10. `layers/l1_nervous/go.mod`
  11. `layers/l1_nervous/go.sum`
  12. `layers/l1_nervous/proto/skill.proto`
  13. `layers/l1_nervous/README.md`
  14. `layers/l1_nervous/internal/skill/types.go`
  15. `layers/l2_brain/README.md`
  16. `layers/l2_brain/pyproject.toml`
  17. `layers/l2_brain/uv.lock`
  18. `layers/l2_brain/.python-version`
  19. `layers/l3_shield/README.md`
  20. `layers/l4_edge/README.md`
- **Commands**:
  ```bash
  python3 scripts/build_structural_hardening_triage.py --write-reports
  ```
- **Tests**:
  ```bash
  layers/l2_brain/.venv/bin/pytest layers/l2_brain/tests/test_structural_hardening_triage.py
  ```
- **Rollback Policy**:
  ```bash
  git checkout layers/l2_brain/structural_hardening/bindings.py
  ```
- **Done Criteria**: Every non-python/metadata/config file is formally classified under an explicit `StructuralClass` with documented reasons, resolving the UNKNOWN candidate list.

---

### Batch 4 — ORPHAN_TEST_CANDIDATE
- **Target Count**: 3
- **Risk Before**: `MEDIUM`
- **Expected Risk After**: `LOW`
- **Estimated Blast Radius**: `LOW` (structural mapping only)
- **Should Execute Now**: `false`
- **Targets**:
  1. `layers/l0_overseer/test/overseer_ipc_test.exs`
  2. `layers/l0_overseer/test/test_helper.exs`
  3. `scripts/tests/test_cgroup_hierarchy.sh`
- **Commands**:
  ```bash
  python3 scripts/build_structural_hardening_triage.py --write-reports
  ```
- **Tests**:
  ```bash
  layers/l2_brain/.venv/bin/pytest layers/l2_brain/tests/test_structural_hardening_triage.py
  ```
- **Rollback Policy**:
  ```bash
  git checkout layers/l2_brain/structural_hardening/bindings.py
  ```
- **Done Criteria**: Mapped to active OTP supervisions/applications or marked legacy with explicit reason in matrix config, resulting in 0 orphan test candidates.

---

### Batch 5 — Shellcheck/toolchain closure
- **Target Count**: 1
- **Risk Before**: `HIGH`
- **Expected Risk After**: `MEDIUM`
- **Estimated Blast Radius**: `LOW` (shell check tool validation only)
- **Should Execute Now**: `false`
- **Targets**:
  1. `layers/l1_nervous/ssh_sandbox_wrapper.sh`
- **Commands**:
  - Debian/Ubuntu: `sudo apt update && sudo apt install -y shellcheck`
  - Fedora: `sudo dnf install -y ShellCheck`
  - Arch: `sudo pacman -S shellcheck`
  - Running: `shellcheck layers/l1_nervous/ssh_sandbox_wrapper.sh`
- **Tests**:
  ```bash
  python3 scripts/build_structural_hardening_triage.py --write-reports
  ```
- **Rollback Policy**:
  ```bash
  git checkout layers/l2_brain/structural_hardening/bindings.py
  ```
- **Done Criteria**: Shellcheck successfully installed and executed against the sandboxed wrapper, output registered in ledger, and risk calibrated to MEDIUM.

---

## 🔒 Governance & Safeguards
- **No force push**: Strictly prohibited across all phases.
- **No physical moves/deletions**: All bindings handled through metadata and spec matching.
- **True Debt Tracking**: `repo_health_status` remains `FAIL` as authentic debt is preserved until explicitly solved.
