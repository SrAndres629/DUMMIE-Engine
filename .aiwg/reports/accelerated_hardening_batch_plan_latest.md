# Accelerated Snowball Hardening Plan — Pack 2.3 (Planning Only)

- generated_from_commit: `656c90d72790fa8d471234e907eb1fea079affa8`
- analysis_base_commit: `656c90d72790fa8d471234e907eb1fea079affa8`
- pack_2_2_closure_commit: `f0345c8e981664dd06f7ec2f71dde619c8ea4b62`

## Baseline Metrics
- repo_health_status: FAIL
- HIGH: 65
- SHADOW_CANDIDATE: 65
- ORPHAN_TEST_CANDIDATE: 3
- deferred_no_safe_action: 0
- toolchain_validated: 4
- toolchain_missing: 1
- contract_bound: 2

## Governance Locks
- no_force_push: True
- no_file_delete: True
- no_file_move: True
- repo_health_must_remain_fail_until_debt_closed: True
- must_not_hide_go_root_failure: True
- must_not_hide_shellcheck_missing: True
- planning_only_no_batch_execution: True

## Recommended Execution Order
1. B5
2. B1
3. B2
4. B4
5. B3
- first_batch_recommendation: B5
- reason: Fastest uncertainty reduction: closes the only remaining toolchain-missing blocker with minimal blast radius.

## Batches
### B1 — HIGH L2 scoped-only spec bindings
- target_count: 20
- risk_before: HIGH
- expected_risk_after: MEDIUM
- estimated_blast_radius: LOW
- should_execute_now: false
- depends_on: none
- done_criteria: Every target has direct_spec_hit >= 1 OR direct linked test OR explicit NEEDS_OWNER with evidence_refs.
- commands:
  - `python3 scripts/build_structural_hardening_triage.py --repo-root . --write-reports --max-actions 50`
- tests:
  - `layers/l2_brain/.venv/bin/pytest -q layers/l2_brain/tests/test_structural_hardening_triage.py`
- rollback: `git restore layers/l2_brain/structural_hardening/bindings.py .aiwg/reports/structural_hardening_triage_latest.json .aiwg/reports/structural_hardening_triage_latest.md`

### B2 — Superficial tests to behavior contracts
- target_count: 10
- risk_before: MEDIUM
- expected_risk_after: LOW
- estimated_blast_radius: LOW
- should_execute_now: false
- depends_on: B1
- done_criteria: Each test includes at least one assertion of behavior/invariant and fails on contract regression.
- commands:
  - `layers/l2_brain/.venv/bin/pytest -q layers/l2_brain/tests/test_consensus.py`
- tests:
  - `layers/l2_brain/.venv/bin/pytest -q layers/l2_brain/tests`
- rollback: `git restore layers/l2_brain/tests`

### B3 — UNKNOWN fan-in classification
- target_count: 20
- risk_before: MEDIUM
- expected_risk_after: LOW
- estimated_blast_radius: LOW
- should_execute_now: false
- depends_on: B1
- done_criteria: No UNKNOWN without reason+evidence and explicit class assignment.
- commands:
  - `python3 scripts/build_structural_hardening_triage.py --repo-root . --write-reports --max-actions 50`
- tests:
  - `layers/l2_brain/.venv/bin/pytest -q layers/l2_brain/tests/test_structural_hardening_triage.py`
- rollback: `git restore layers/l2_brain/structural_hardening/bindings.py .aiwg/reports/structural_hardening_triage_latest.json .aiwg/reports/structural_hardening_triage_latest.md`

### B4 — ORPHAN_TEST_CANDIDATE closure
- target_count: 3
- risk_before: MEDIUM
- expected_risk_after: LOW
- estimated_blast_radius: LOW
- should_execute_now: false
- depends_on: B3
- done_criteria: Every orphan test is mapped to runtime or marked legacy with evidence; orphan count <= 1 with explicit reason.
- commands:
  - `python3 scripts/build_structural_hardening_triage.py --repo-root . --write-reports --max-actions 50`
- tests:
  - `layers/l2_brain/.venv/bin/pytest -q layers/l2_brain/tests/test_structural_hardening_triage.py`
- rollback: `git restore layers/l2_brain/structural_hardening/bindings.py .aiwg/reports/structural_hardening_triage_latest.json .aiwg/reports/structural_hardening_triage_latest.md`

### B5 — Shellcheck/toolchain closure for ssh wrapper
- target_count: 1
- risk_before: HIGH
- expected_risk_after: MEDIUM
- estimated_blast_radius: LOW
- should_execute_now: false
- depends_on: none
- done_criteria: shellcheck present, executed, and ledger updated; only then risk downgrade allowed.
- commands:
  - `shellcheck layers/l1_nervous/ssh_sandbox_wrapper.sh`
- toolchain_install_commands:
  - debian_ubuntu: `sudo apt update && sudo apt install -y shellcheck`
  - fedora: `sudo dnf install -y ShellCheck`
  - arch: `sudo pacman -S shellcheck`
- tests:
  - `python3 scripts/build_structural_hardening_triage.py --repo-root . --write-reports --max-actions 50`
- rollback: `git restore .aiwg/reports/structural_polyglot_toolchain_ledger_latest.json .aiwg/reports/structural_hardening_triage_latest.json .aiwg/reports/structural_hardening_triage_latest.md`

## Global Post-Batch Gates
- `python3 scripts/build_structural_hardening_triage.py --repo-root . --write-reports --max-actions 50`
- `layers/l2_brain/.venv/bin/pytest -q layers/l2_brain/tests/test_structural_hardening_contracts.py layers/l2_brain/tests/test_structural_hardening_classifier.py layers/l2_brain/tests/test_structural_hardening_triage.py`
- `layers/l2_brain/.venv/bin/pytest -q layers/l1_nervous/tests/test_l1_contract_imports.py layers/l0_overseer/tests/test_l0_contract_imports.py`
- `layers/l2_brain/.venv/bin/pytest -q layers/l2_brain/tests/test_embedding_mesh_contracts.py layers/l2_brain/tests/test_embedding_mesh_router.py layers/l2_brain/tests/test_semantic_hardening_index.py`
- `python3 scripts/validate_specs_docs.py`
