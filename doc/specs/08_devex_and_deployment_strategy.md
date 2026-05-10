---
spec_id: "DE-V2-L0-08"
title: "DevEx y Estrategia de Despliegue Hermético"
status: "DRAFT"
layer: "L0"
last_verified_on: "2026-04-24"
---
# DevEx y Estrategia de Despliegue Hermético

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/08_devex_and_deployment_strategy.md`
- `doc/specs/08_devex_and_deployment_strategy.feature`
- `doc/specs/08_devex_and_deployment_strategy.rules.json`
- `layers/l0_overseer`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/08_devex_and_deployment_strategy.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/08_devex_and_deployment_strategy.md` |
| Artefactos hermanos presentes | `doc/specs/08_devex_and_deployment_strategy.feature` y `doc/specs/08_devex_and_deployment_strategy.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/08_devex_and_deployment_strategy.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/08_devex_and_deployment_strategy.md` |
