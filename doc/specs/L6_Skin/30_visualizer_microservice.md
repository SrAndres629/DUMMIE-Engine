---
spec_id: DE-V2-L6-30
title: Visualizador Topológico 4D (Microservicio)
status: DRAFT
layer: L6
last_verified_on: '2026-04-24'
version: 1.0.0
namespace: dummie.engine.l6
claims:
- id: 30_visualizer_microservice-file-valid
  description: Spec file '30_visualizer_microservice.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/L6_Skin/30_visualizer_microservice.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Visualizador Topológico 4D (Microservicio)

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/L6_Skin/30_visualizer_microservice.md`
- `doc/specs/L6_Skin/30_visualizer_microservice.feature`
- `doc/specs/L6_Skin/30_visualizer_microservice.rules.json`
- `layers/l6_skin/__init__.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/30_visualizer_microservice.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/30_visualizer_microservice.md` |
| Artefactos hermanos presentes | `doc/specs/30_visualizer_microservice.feature` y `doc/specs/30_visualizer_microservice.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/30_visualizer_microservice.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/30_visualizer_microservice.md` |
