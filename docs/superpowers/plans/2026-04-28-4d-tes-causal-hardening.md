# 4D-TES Causal Hardening Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the 4D-TES causal and SDD modules stable, executable, and verifiable under real tests and audit conditions.

**Architecture:** First stabilize cross-layer contracts and compatibility surfaces, then repair the broken persistence/audit path, then wire governance primitives into real daemon and retrieval behavior. Each stage adds regression tests before or alongside implementation so every repaired failure is preserved.

**Tech Stack:** Python 3.11, pytest, Kuzu, uv, shell audit scripts

---

## Chunk 1: Contract Stability

### Task 1: Restore canonical/compatibility imports

**Files:**
- Modify: `layers/l2_brain/adapters.py`
- Modify: `layers/l2_brain/domain/*.py` as needed
- Test: `layers/l2_brain/tests/test_hypothesis_bundle.py`
- Test: `layers/l2_brain/tests/test_counterfactual_service.py`
- Test: `layers/l2_brain/tests/test_epistemic_retrieval.py`
- Test: `layers/l1_nervous/tests/test_causal_chaining.py`

- [ ] **Step 1: Reproduce failing imports**

Run:
```bash
cd layers/l2_brain && uv run pytest --collect-only -q tests/test_hypothesis_bundle.py tests/test_counterfactual_service.py tests/test_epistemic_retrieval.py -vv
```

- [ ] **Step 2: Add failing compatibility coverage where needed**

Add tests that exercise repo-root and layer-root compatible imports/contracts.

- [ ] **Step 3: Implement minimal import/compatibility fixes**

Use canonical import fallbacks and explicit compatibility helpers instead of path-dependent behavior.

- [ ] **Step 4: Verify targeted suites pass**

Run:
```bash
cd layers/l2_brain && PYTHONPATH=../.. uv run pytest -q tests/test_hypothesis_bundle.py tests/test_counterfactual_service.py tests/test_epistemic_retrieval.py
```

### Task 2: Reintroduce legacy-safe `MemoryNode4D` compatibility

**Files:**
- Modify: `layers/l2_brain/models.py`
- Modify: `layers/l2_brain/cypher_codec.py` if needed
- Test: `layers/l1_nervous/tests/test_causal_chaining.py`
- Test: `layers/l1_nervous/tests/test_causal_recovery.py`

- [ ] **Step 1: Write or preserve failing regression expectations**

Cover `build_create_cypher`, `parent_hash`, and related legacy expectations without breaking canonical `parent_hashes`.

- [ ] **Step 2: Verify tests fail for the right reason**

Run:
```bash
cd layers/l2_brain && PYTHONPATH=../.. uv run pytest -q ../l1_nervous/tests/test_causal_chaining.py ../l1_nervous/tests/test_causal_recovery.py
```

- [ ] **Step 3: Implement compatibility bridge on top of canonical schema**

- [ ] **Step 4: Re-run targeted suites**

## Chunk 2: Persistence and Audit Hardening

### Task 3: Repair L1 crystallization persistence

**Files:**
- Modify: `layers/l1_nervous/compressive_memory.py`
- Test: `layers/l1_nervous/tests/test_causal_chaining.py`
- Test: `scripts/verify_compression.py`

- [ ] **Step 1: Reproduce the real failure**

Run:
```bash
bash scripts/full_industrial_audit.sh
```

- [ ] **Step 2: Add a regression test for the crystallization failure path**

- [ ] **Step 3: Implement minimal fix**

- [ ] **Step 4: Re-run targeted crystallization tests**

### Task 4: Make the industrial audit trustworthy again

**Files:**
- Modify: `scripts/full_industrial_audit.sh` only if needed
- Modify: `scripts/verify_compression.py` only if needed
- Test: audit command itself

- [ ] **Step 1: Keep the audit strict**

Do not add bypasses that hide persistence problems.

- [ ] **Step 2: Verify full audit passes**

Run:
```bash
bash scripts/full_industrial_audit.sh
```

## Chunk 3: Daemon Execution Hardening

### Task 5: Convert governance primitives into daemon gates

**Files:**
- Modify: `layers/l2_brain/daemon.py`
- Modify: `layers/l2_brain/runtime_guards.py` if needed
- Modify: `layers/l2_brain/domain/hypothesis_service.py` if needed
- Modify: `layers/l2_brain/domain/counterfactual_service.py` if needed
- Test: `layers/l2_brain/tests/test_daemon_hierarchical_planner.py`
- Create/Modify: `layers/l2_brain/tests/test_daemon_causal_gates.py`

- [ ] **Step 1: Write failing tests for blocking/review/collapse/admissibility behavior**

- [ ] **Step 2: Run them and confirm RED**

- [ ] **Step 3: Implement minimal daemon gating**

- [ ] **Step 4: Re-run daemon suites**

## Chunk 4: Retrieval Hardening

### Task 6: Add production retrieval path for minimal proof subgraphs

**Files:**
- Modify: `layers/l2_brain/domain/retrieval_service.py`
- Modify: `layers/l2_brain/adapters.py`
- Create/Modify: `layers/l2_brain/tests/test_epistemic_retrieval.py`
- Create/Modify: `layers/l2_brain/tests/test_repository_retrieval_paths.py`

- [ ] **Step 1: Write failing tests for proof-subgraph retrieval from repository surface**

- [ ] **Step 2: Confirm RED**

- [ ] **Step 3: Implement the smallest production entry point**

- [ ] **Step 4: Re-run retrieval suites**

## Chunk 5: Documentation and Final Verification

### Task 7: Align verification tooling and relevant specs

**Files:**
- Modify: relevant `doc/specs/*.md`
- Modify: `scripts/validate_specs_docs.py` only if policy itself is wrong

- [ ] **Step 1: Reproduce doc/spec validation failures**

Run:
```bash
python3 scripts/validate_specs_docs.py
```

- [ ] **Step 2: Fix only the failing spec/tooling mismatches relevant to this hardening**

- [ ] **Step 3: Re-run validator**

### Task 8: Final verification sweep

**Files:**
- No planned code changes

- [ ] **Step 1: Run targeted L1/L2 suites**

```bash
cd layers/l2_brain && PYTHONPATH=../.. uv run pytest -q tests ../l1_nervous/tests/test_causal_chaining.py ../l1_nervous/tests/test_causal_recovery.py
```

- [ ] **Step 2: Run industrial audit**

```bash
bash scripts/full_industrial_audit.sh
```

- [ ] **Step 3: Run docs/spec validation**

```bash
python3 scripts/validate_specs_docs.py
```

- [ ] **Step 4: Run 4D-TES grep contract check**

```bash
rg -n "kuzu_data|MemoryState|m\\.\\*|rm -f.*kuzu|os\\.remove\\(" layers scripts doc -S
```

- [ ] **Step 5: Inspect final worktree**

```bash
git status --short
git diff --stat
```
