---
spec_id: DE-V2-L2-109
title: PolyglotArchitectureRegistry
status: ACTIVE
layer: L2
last_verified_on: '2026-05-16'
version: 1.0.0
namespace: dummie.engine.plan_v1
claims:
- id: 109_polyglot_architecture_registry-file-valid
  description: Spec file '109_polyglot_architecture_registry.md' exists, parses valid
    YAML frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/109_polyglot_architecture_registry.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Spec 109 - PolyglotArchitectureRegistry

## Purpose
Define the canonical registry that maps DUMMIE layers, languages, runtimes, source directories, specs, tests, ownership, and anti-Python-only bias controls.

## Scope
Applies to global architecture reviews, project world model generation, spec coverage planning, context planning, and future ContextQuant scoring.

## Why P6 Exists
DUMMIE is physically polyglot and layered. P6 prevents agents from reducing the system to L2/Python because that loses runtime ownership, inter-layer contracts, and lower/upper layer evidence.

## Current State
Implemented as compact registry, layer-language map, schema, rules, and report artifacts. Runtime probes are specified but not implemented.

## Physical Evidence
- `.aiwg/architecture/polyglot_architecture_registry.yaml`
- `.aiwg/architecture/layer_language_map.json`
- `.aiwg/schemas/polyglot_architecture_registry.schema.json`
- `.aiwg/reports/plan_v1_phase_6_polyglot_architecture_registry.md`
- `.aiwg/reports/plan_v1_phase_6_polyglot_architecture_registry.json`
- `doc/specs/109_polyglot_architecture_registry.md`
- `doc/specs/109_polyglot_architecture_registry.feature`
- `doc/specs/109_polyglot_architecture_registry.rules.json`

## Relationship to P5 Truth Hierarchy
P5 defines source precedence. P6 registers polyglot architecture as canonical machine-readable evidence with truth rank 85.

## Layer-language Mapping
All L0-L6 layers must appear in `.aiwg/architecture/layer_language_map.json` with physical paths, primary languages, runtime role, and confidence.

## First-party vs Dependency/Vendored Distinction
Architecture identity must be derived from first-party source and canonical contracts, not from tracked dependencies, build outputs, generated caches, or vendored code.

## Anti-Python-only Bias Guard
Global architecture tasks must load the registry and layer map before summarizing DUMMIE. A Python-only global summary is invalid unless the task is explicitly scoped to Python/L2.

## Required Usage by Future Global Architecture Tasks
Future global tasks must report language coverage and identify layers considered. Missing layer coverage must be explicit.

## Required Usage by P7 ProjectWorldModel
P7 must consume the registry and layer map as canonical inputs instead of reconstructing architecture from chat memory.

## Required Usage by P8 SpecCoverageGate
P8 must use the registry to require layer/language coverage in global spec checks.

## Required Usage by P13 ContextQuantRuntime
P13 should prefer compact registry artifacts over raw repo scans for architecture context.

## Risk Model
Risks include dependency-count inflation, generated artifact noise, layer naming drift, sparse layer implementation, and Python-only reasoning bias.

## Validation Expectations
Registry YAML, layer map JSON, schema JSON, and rules JSON must parse. Spec validation may retain known inherited legacy-doc debt.

## Contract Invariants
- All L0-L6 layers are represented or explicitly marked low confidence.
- Dependency/generated files do not define first-party architecture identity.
- Global architecture tasks must load registry and layer map.
- Python-only global summaries are rejected outside explicitly Python-scoped tasks.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/109_polyglot_architecture_registry.md
python3 - <<'PY'
import json
from pathlib import Path
for p in [
    '.aiwg/architecture/layer_language_map.json',
    '.aiwg/schemas/polyglot_architecture_registry.schema.json',
    'doc/specs/109_polyglot_architecture_registry.rules.json'
]:
    json.loads(Path(p).read_text(encoding='utf-8'))
print('spec 109 JSON evidence parse PASS')
PY
```

## Traceability
- Phase: `P6` PolyglotArchitectureRegistry
- Depends on: `P5` Truth Hierarchy & Canonicality Policy
- Next phase: `P7` ProjectWorldModel
