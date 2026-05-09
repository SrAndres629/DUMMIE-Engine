# Sovereign SDD Governance Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the first physical implementation of causal Spec-Driven Development governance on top of the 4D-TES.

**Architecture:** Implement pure L2 modules first: spec compiler, admission control, evidence graph, contradiction checks, decision decay, failure taxonomy, causal replay, and runtime guards. L1 write blocking and formal verification are later phases once the policy proves stable.

**Tech Stack:** Python dataclasses/enums, pytest, existing L2 flat module layout.

---

## Chunk 1: L2 Governance Foundation

### Task 1: Spec Compiler And Admission Control

- [ ] Write failing tests for compiling approved specs and blocking orphan changes.
- [ ] Implement `layers/l2_brain/sdd_governance.py`.
- [ ] Run focused tests.

### Task 2: Evidence, Contradictions, Decay, Coverage

- [ ] Write failing tests for evidence verification and contradiction detection.
- [ ] Implement pure helpers.
- [ ] Run focused tests.

### Task 3: Replay And Runtime Guards

- [ ] Write failing tests for replay frames and runtime guards.
- [ ] Implement `causal_replay.py` and `runtime_guards.py`.
- [ ] Run focused tests.

## Chunk 2: Verification

- [ ] Run full L2 tests.
- [ ] Run import smoke.
- [ ] Commit scoped changes only.
