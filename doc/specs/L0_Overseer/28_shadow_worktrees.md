---
spec_id: DE-V2-L0-28B
title: Shadow Worktrees
status: PROPOSED
layer: L0
last_verified_on: '2026-04-24'
version: 1.0.0
namespace: dummie.engine.l0
claims:
- id: 28_shadow_worktrees-file-valid
  description: Spec file '28_shadow_worktrees.md' exists, parses valid YAML frontmatter,
    and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/L0_Overseer/28_shadow_worktrees.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Shadow Worktrees

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Diseño de roadmap; implementación parcial o no integrada al flujo principal.

## Physical Evidence
- `doc/specs/L0_Overseer/28_shadow_worktrees.md`
- `doc/specs/L0_Overseer/28_shadow_worktrees.feature`
- `doc/specs/L0_Overseer/28_shadow_worktrees.rules.json`
- `layers/l0_overseer/__init__.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/28_shadow_worktrees.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/28_shadow_worktrees.md` |
| Artefactos hermanos presentes | `doc/specs/28_shadow_worktrees.feature` y `doc/specs/28_shadow_worktrees.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/28_shadow_worktrees.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/28_shadow_worktrees.md` |
