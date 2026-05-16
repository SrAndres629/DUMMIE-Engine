---
spec_id: "DE-V2-L2-108"
title: "Truth Hierarchy & Canonicality Policy"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
version: "1.0.0"
namespace: "dummie.engine.plan_v1"
---
# Spec 108 - Truth Hierarchy & Canonicality Policy

## Purpose
Define how DUMMIE resolves conflicting claims across code, tests, specs, schemas, runtime ledgers, reports, notes, mirrors, and chat.

## Scope
Applies to all artifacts governed by P4 and all future artifacts that may influence context selection, truth decisions, and governance outcomes.

## Why P5 Exists
P4 defined artifact metadata; P5 defines decision policy so truth is chosen by evidence hierarchy instead of recency, availability, or narrative noise.

## Current State
Implemented as policy contracts (schema + spec + rules + scenarios). Runtime enforcement is intentionally deferred.

## Physical Evidence
- `.aiwg/schemas/truth_hierarchy.schema.json`
- `.aiwg/reports/plan_v1_phase_5_truth_hierarchy_policy.md`
- `.aiwg/reports/plan_v1_phase_5_truth_hierarchy_policy.json`
- `doc/specs/108_truth_hierarchy_canonicality_policy.md`
- `doc/specs/108_truth_hierarchy_canonicality_policy.feature`
- `doc/specs/108_truth_hierarchy_canonicality_policy.rules.json`

## Relationship to P4 Cognitive Artifact Protocol
P4 defines artifact fields/lifecycle/canonicality/truth-rank metadata. P5 defines conflict resolution and precedence logic over that metadata.

## Truth Source Ranks
- 100: physical source code with passing tests
- 95: passing tests and validation results
- 90: active specs/rules/features
- 85: schemas and machine contracts
- 80: phase ledger and mission runtime state
- 75: daemon outcome and validation result
- 70: learning episode with evidence
- 65: vault entry with evidence
- 60: active cognitive artifact
- 50: report with evidence
- 40: note/folder note with freshness
- 30: human mirror / Obsidian export
- 20: chat transcript or agent memory
- 10: unknown legacy doc
- 0: rejected/deprecated/unsafe artifact

## Effective Truth Rank
Policy formula:
`effective_truth_rank = base_truth_rank + evidence_bonus - staleness_penalty - risk_penalty`

Evidence bonus:
- passing_tests: +5
- schema_validated: +3
- has_evidence_refs: +3
- runtime_owned: +2

Staleness penalty:
- stale: -30
- unknown_freshness: -15
- linked_test_failed: -40
- source_hash_changed: -30

Risk penalty:
- duplicate_truth_detected: -10
- missing_owner_runtime: -10
- weak_or_no_evidence: -10
- legacy_unknown: -20

Hard zero:
- rejected/deprecated-for-reasoning
- secret_detected
- private_reasoning_detected

## Canonical Source Policy
- Code + passing tests are strongest behavioral truth.
- Specs are canonical intent/contracts, not implementation proof.
- Schemas are canonical shape contracts.
- Ledgers are canonical operational history if append-only and validated.
- Reports are evidence, not primary truth.
- Vault entries are reusable memory, not automatic truth.
- Notes are compressed understanding, not truth unless fresh and linked.
- Obsidian/human mirrors are non-canonical by default.
- Chat history is non-canonical by default.
- Agent claims are non-canonical until backed by evidence.

## Conflict Resolution Algorithm
1. Collect candidate sources.
2. Reject unsafe artifacts (secrets, credentials, private chain-of-thought, `.env` assignments).
3. Normalize source metadata (`canonicality`, `truth_rank`, `lifecycle_state`, `freshness`, `evidence_refs`, `linked_specs`, `linked_tests`, `runtime_consumers`).
4. Apply lifecycle demotion (stale penalty, deprecated/rejected rank=0, unknown freshness blocked for high-confidence).
5. Apply canonicality preference (`canonical > derived > candidate > mirror > unknown`).
6. Apply evidence quality modifiers.
7. Resolve by highest effective rank; tie-break by freshness, then machine-parseable source, then runtime ownership; unresolved => `requires_human_review`.
8. Record winning source, losing sources, reason, evidence refs, demotions, and next action.

## Stale Demotion
Stale artifacts are not automatically deleted; they are demoted and blocked from high-confidence reasoning until refreshed or superseded.

## Mirror Policy
Mirror artifacts (including future Obsidian exports) are non-canonical by default and cannot override internal canonical artifacts.

## Chat Non-Canonical Policy
Chat transcript and agent memory are non-canonical by default; they can trigger discovery but cannot resolve conflicts without evidence-backed artifacts.

## Security Rejection Policy
Artifacts containing secrets, credentials, private reasoning, or chain-of-thought are rejected with rank 0 and excluded from reasoning.

## Required Scenarios
- code contradicts spec
- spec contradicts report
- report says PASS but tests fail
- chat says feature exists but repo lacks file
- vault entry contradicts current source
- note is stale after source change
- Obsidian mirror contradicts internal vault
- legacy doc references missing spec
- two reports disagree about test status
- artifact lacks freshness but tries to enter high-confidence context

## Contract Invariants
- Higher effective truth rank wins unless artifact is unsafe.
- Unsafe artifacts are always rejected.
- Unknown freshness blocks high-confidence usage.
- Reports and chat cannot override code/tests/specs.
- Mirror artifacts are non-canonical unless future policy explicitly promotes them.

## Relationship to P6 PolyglotArchitectureRegistry
P6 must map runtime ownership by language/layer so conflict resolution can use runtime-owned tie-breakers consistently.

## Relationship to P8 SpecCoverageGate
P8 should enforce that spec claims used in conflicts are linked to current files and validation status.

## Relationship to P13 ContextQuantRuntime
P13 should consume truth rank, freshness, canonicality, and conflict outcomes as scoring inputs.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/108_truth_hierarchy_canonicality_policy.md
python3 - <<'PY'
import json
from pathlib import Path
for p in [
    '.aiwg/schemas/truth_hierarchy.schema.json',
    'doc/specs/108_truth_hierarchy_canonicality_policy.rules.json'
]:
    json.loads(Path(p).read_text(encoding='utf-8'))
print('spec 108 evidence parse PASS')
PY
```

## Traceability
- Phase: `P5` Truth Hierarchy & Canonicality Policy
- Depends on: `P4` Cognitive Artifact Protocol
- Input evidence: `.aiwg/reports/artifact_lifecycle_matrix.json`
- Next phase: `P6` PolyglotArchitectureRegistry
