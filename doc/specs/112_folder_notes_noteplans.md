---
spec_id: "DE-V2-L2-112"
title: "FolderNotes + NotePlans"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
version: "1.0.0"
namespace: "dummie.engine.plan_v1"
---
# Spec 112 - FolderNotes + NotePlans

## Purpose
Define governed FolderNotes and NotePlans as derived cognitive artifacts for compact folder-level orientation.

## Scope
Covers note contracts, freshness rules, token roles, coverage linkage, and non-override truth constraints for internal notes.

## Why P9 Exists
P7 introduced a compact world model and P8 introduced coverage gating. P9 turns these into governed notes so agents can orient quickly without raw-folder bulk reads.

## Current State
Implemented in P9 as governed artifacts only: folder notes manifest, tier-0 notes/noteplans, schemas, and spec triplet. Runtime freshness enforcement is deferred to P10.

## Physical Evidence
- `.aiwg/notes/folder_notes_manifest.json`
- `.aiwg/notes/folders/README.md`
- `.aiwg/notes/folders/evolution/notes.md`
- `.aiwg/notes/folders/evolution/noteplan.md`
- `.aiwg/schemas/folder_note.schema.json`
- `.aiwg/schemas/noteplan.schema.json`
- `.aiwg/reports/plan_v1_phase_9_folder_notes_noteplans.md`
- `.aiwg/reports/plan_v1_phase_9_folder_notes_noteplans.json`
- `doc/specs/112_folder_notes_noteplans.md`
- `doc/specs/112_folder_notes_noteplans.feature`
- `doc/specs/112_folder_notes_noteplans.rules.json`

## Relationship to P7 ProjectWorldModel
FolderNotes must consume world-model state as canonical orientation input.

## Relationship to P8 SpecCoverageGate
FolderNotes must link to spec coverage matrix and inherit coverage warnings/constraints.

## FolderNote Contract
Each folder note must include folder path, purpose, canonical source refs, source hash, freshness state, linked specs/tests/capabilities, token role, risks, and refresh triggers.

## NotePlan Contract
Each noteplan must capture missing links, required probes, stale risk, and phase-specific guidance for P10/P11/P13.

## Truth Policy
FolderNotes are derived artifacts and cannot override code, tests, specs, schemas, phase ledgers, world model, or current phase files.

## Freshness/Source Hash Policy
Each note tracks deterministic source hash from tracked file list metadata and must refresh when hash or linked canonical evidence changes.

## Token Role Policy
Default token role is `summary_only`; `retrieval_candidate` is allowed only when note freshness is confirmed and task relevance is explicit.

## Coverage Linkage Policy
Every folder note set must reference `.aiwg/reports/spec_coverage_matrix.json` and carry forward inherited coverage debt separately from regressions.

## Anti-Stale Narrative Debt Policy
Notes are compression artifacts. They must remain small, evidence-linked, and invalidated when upstream sources drift.

## Relationship to P10 FreshnessLedger + StaleMemoryDetector
P10 must compute stale status from note hashes and invalidation triggers defined here.

## Relationship to P11 ContextPackage + ContextReceipt
P11 should include notes by reference and enforce token-role/freshness filters.

## Relationship to P13 ContextQuantRuntime
P13 should treat notes as optional compression candidates, never as canonical truth sources.

## Validation Expectations
- Manifest JSON valid.
- Folder note and noteplan schemas valid.
- Tier-0 notes and noteplans present.
- State files advance to P10 only after P9 validation passes.

## Contract Invariants
- Folder notes remain `derived` with truth rank 40.
- Notes never override code/tests/specs/schemas/ledgers/world model/current phase files.
- Default token role remains `summary_only` unless freshness and task relevance justify `retrieval_candidate`.
- Coverage matrix reference is mandatory for governed notes.
- Source hash and refresh triggers are mandatory for each folder entry.

## Verification
```bash
git diff --check
python3 scripts/validate_specs_docs.py || true
python3 - <<'PY'
import json
from pathlib import Path
for p in [
    ".aiwg/notes/folder_notes_manifest.json",
    ".aiwg/schemas/folder_note.schema.json",
    ".aiwg/schemas/noteplan.schema.json",
    "doc/specs/112_folder_notes_noteplans.rules.json",
]:
    json.loads(Path(p).read_text(encoding="utf-8"))
print("Spec 112 verification parse PASS")
PY
```

## Traceability
- Plan: `DUMMIE PLAN V1 — Cognitive Evolution Operating Layer`
- Phase: `P9`
- Upstream inputs:
  - `.aiwg/world_model/project_world_model.json`
  - `.aiwg/reports/spec_coverage_matrix.json`
  - `.aiwg/schemas/cognitive_artifact.schema.json`
  - `.aiwg/schemas/truth_hierarchy.schema.json`
- Downstream consumers:
  - `P10 FreshnessLedger + StaleMemoryDetector`
  - `P11 ContextPackage + ContextReceipt`
  - `P13 ContextQuantRuntime`
