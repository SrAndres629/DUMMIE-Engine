---
spec_id: DE-V2-L2-111
title: SpecCoverageGate
status: ACTIVE
layer: L2
last_verified_on: '2026-05-16'
version: 1.0.0
namespace: dummie.engine.plan_v1
claims:
- id: 111_spec_coverage_gate-file-valid
  description: Spec file '111_spec_coverage_gate.md' exists, parses valid YAML frontmatter,
    and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/111_spec_coverage_gate.md').read().split('---')[1]); assert d,
    'empty frontmatter'"
  severity: critical
---
# Spec 111 - SpecCoverageGate

## Purpose
Define the first measurable coverage gate that checks whether specs, features, rules, layers, languages, tests, capabilities, and debt isolation are sufficiently connected for controlled phase progression.

## Scope
Applies to governance phases that need evidence before implementation-heavy work. P8 provides gate definitions and matrix artifacts, not runtime enforcement.

## Why P8 Exists
P7 created a compact world model. P8 converts that model into measurable coverage gates so missing links are visible before future phases create new notes, plans, or runtime behavior.

## Current State
Implemented in P8 as governance artifacts (coverage matrix, schema, report, and spec triplet) without runtime enforcement changes.

## Physical Evidence
- `.aiwg/reports/spec_coverage_matrix.json`
- `.aiwg/schemas/spec_coverage_gate.schema.json`
- `.aiwg/reports/plan_v1_phase_8_spec_coverage_gate.md`
- `.aiwg/reports/plan_v1_phase_8_spec_coverage_gate.json`
- `doc/specs/111_spec_coverage_gate.md`
- `doc/specs/111_spec_coverage_gate.feature`
- `doc/specs/111_spec_coverage_gate.rules.json`

## Relationship to P7 ProjectWorldModel
P8 consumes world model, corrected polyglot registry, truth hierarchy schema, cognitive artifact schema, and canonical phase state to compute coverage.

## Spec Triplet Integrity
A complete family must include `.md`, `.feature`, and `.rules.json`. Missing members or invalid rules JSON downgrade integrity and influence gate decisions.

## Layer Coverage
L0-L6 coverage is evaluated through linked spec refs, test refs, and language refs. Weak coverage is allowed with documented reasons; missing layers are gate failures.

## Language Coverage
First-party languages must have coverage references. Dependency-only languages do not define architecture identity and can remain warning-level when unlinked.

## Capability Coverage
Native capabilities must be path-backed and linked to tests/spec/report evidence. Weak linkages are warnings; absent linkages are failures.

## Test Linkage
Core L2 capabilities require test linkage. Cross-layer unevenness is warning-level unless linkage collapses entirely.

## Known Debt Isolation
Legacy guide references to missing specs (2, 7, 15, 35, 41, 42, 44) are inherited debt, not P8 regressions.

## Coverage Thresholds
- Triplet integrity pass: >=90%, warning: >=70%, fail: <70%.
- Layer coverage pass requires all layers represented with at least partial coverage or documented low-confidence reason.
- Language coverage fails only if first-party language is omitted from coverage.
- Capability coverage fails when world-model capability has missing path/linkage.
- Test linkage fails only when no core linkage exists.

## Gate Decisions
Gate emits `PASS`, `PASS_WITH_WARNINGS`, or `FAIL` with explicit blockers and warning lists.

## Relationship to P9 FolderNotes + NotePlans
P9 must consume coverage constraints so notes do not become stale narrative debt disconnected from specs/tests.

## Relationship to P13 ContextQuantRuntime
P13 must consume coverage matrix as a quality signal before optimizing context selection.

## Validation Expectations
Coverage matrix JSON, gate schema JSON, P8 report JSON, and Spec 111 rules JSON must parse. Known inherited spec debt remains tracked.

## Contract Invariants
- Coverage gate computes triplet integrity, layer coverage, language coverage, capability coverage, and test linkage.
- Legacy guide debt is isolated as inherited and not attributed to P8.
- Gate decision includes explicit blockers and warnings.
- P9 consumes coverage constraints before creating notes/noteplans.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/111_spec_coverage_gate.md
python3 - <<'PY'
import json
from pathlib import Path
for p in [
    '.aiwg/reports/spec_coverage_matrix.json',
    '.aiwg/schemas/spec_coverage_gate.schema.json',
    'doc/specs/111_spec_coverage_gate.rules.json'
]:
    json.loads(Path(p).read_text(encoding='utf-8'))
print('spec 111 JSON evidence parse PASS')
PY
```

## Traceability
- Phase: `P8` SpecCoverageGate
- Depends on: `P7` ProjectWorldModel and corrected polyglot/truth/artifact schemas
- Next phase: `P9` FolderNotes + NotePlans
