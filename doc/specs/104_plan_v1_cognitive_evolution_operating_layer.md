---
spec_id: DE-V2-L2-104
title: Plan V1 Cognitive Evolution Operating Layer
status: ACTIVE
layer: L2
last_verified_on: '2026-05-16'
version: 1.0.0
namespace: dummie.engine.plan_v1
claims:
- id: 104_plan_v1_cognitive_evolution_operating_layer-file-valid
  description: Spec file '104_plan_v1_cognitive_evolution_operating_layer.md' exists,
    parses valid YAML frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/104_plan_v1_cognitive_evolution_operating_layer.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Spec 104 - Plan V1 Cognitive Evolution Operating Layer

## Purpose

DUMMIE PLAN V1 must exist as a canonical operating layer that governs phase execution, objectives, dependencies, current position, next phase seed, and evidence reports.

## Current State

Implemented as Phase 1 governance artifacts under `.aiwg/evolution/`, `.aiwg/schemas/`, `.aiwg/reports/`, and `doc/specs/`. Phase 1 is a canonical operating layer, not a new runtime service.

## Physical Evidence

- `.aiwg/evolution/PLAN_V1_COGNITIVE_EVOLUTION_OPERATING_LAYER.md`
- `.aiwg/evolution/phases.yaml`
- `.aiwg/evolution/phase_dependencies.graph.json`
- `.aiwg/evolution/long_term_objectives.yaml`
- `.aiwg/evolution/short_term_objectives.yaml`
- `.aiwg/evolution/current_position.json`
- `.aiwg/evolution/next_phase_seed.json`
- `.aiwg/evolution/phase_acceptance_contract.yaml`
- `.aiwg/evolution/roadmap_update_policy.md`
- `.aiwg/evolution/snowball_metrics.schema.json`

## Requirements

- DUMMIE PLAN V1 exists in `.aiwg/evolution/PLAN_V1_COGNITIVE_EVOLUTION_OPERATING_LAYER.md`.
- Exactly 31 phases exist in `.aiwg/evolution/phases.yaml`.
- Phase dependencies exist in `.aiwg/evolution/phase_dependencies.graph.json`.
- Long-term objectives exist in `.aiwg/evolution/long_term_objectives.yaml`.
- Short-term objectives exist in `.aiwg/evolution/short_term_objectives.yaml`.
- Current position exists in `.aiwg/evolution/current_position.json`.
- Next phase seed exists in `.aiwg/evolution/next_phase_seed.json`.
- Roadmap must not be redefined from chat memory.

## Contract Invariants

- Exactly 31 phases are registered for Plan V1.
- `current_position.json` points to one current phase and one next required phase.
- `next_phase_seed.json` points to P2 after Phase 1.
- Deferred capabilities are registered instead of silently discarded.
- Existing DUMMIE Engine capabilities are mapped before new architecture is introduced.

## Engine-Native Reuse

Phase 1 must map existing native capabilities such as PhaseLedger, ContextBudgetManager, SemanticRetrievalRuntime, MemoryGraphRuntime, MissionWorkbench, OutcomeEvaluator, specs validation, reports, and schemas when present.

## Verification

```bash
python3 scripts/validate_specs_docs.py --check doc/specs/104_plan_v1_cognitive_evolution_operating_layer.md
python3 - <<'PY'
import json
from pathlib import Path
import yaml
assert len(yaml.safe_load(Path('.aiwg/evolution/phases.yaml').read_text())['phases']) == 31
assert json.loads(Path('.aiwg/evolution/current_position.json').read_text())['current_phase'] == 'P1'
assert json.loads(Path('.aiwg/evolution/next_phase_seed.json').read_text())['next_phase'] == 'P2'
PY
```

## Traceability

| Invariant | Evidence | Verification |
| --- | --- | --- |
| 31 phases | `.aiwg/evolution/phases.yaml` | YAML parse and count |
| Current position | `.aiwg/evolution/current_position.json` | JSON parse and cold-read |
| Next phase seed | `.aiwg/evolution/next_phase_seed.json` | JSON parse and cold-read |
| Roadmap dependencies | `.aiwg/evolution/phase_dependencies.graph.json` | JSON parse |
| Acceptance policy | `.aiwg/evolution/phase_acceptance_contract.yaml` | YAML parse |

## Acceptance

The layer is accepted only when critical JSON/YAML files parse and cold-read operability can select P2 without chat memory.
