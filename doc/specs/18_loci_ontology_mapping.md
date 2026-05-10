---
spec_id: "DE-V2-L4-18"
title: "Palacio de Loci y RBAC Topográfico"
status: "DRAFT"
layer: "L4"
last_verified_on: "2026-04-24"
---
# Palacio de Loci y RBAC Topográfico

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/18_loci_ontology_mapping.md`
- `doc/specs/18_loci_ontology_mapping.feature`
- `doc/specs/18_loci_ontology_mapping.rules.json`
- `layers/l4_edge`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/18_loci_ontology_mapping.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/18_loci_ontology_mapping.md` |
| Artefactos hermanos presentes | `doc/specs/18_loci_ontology_mapping.feature` y `doc/specs/18_loci_ontology_mapping.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/18_loci_ontology_mapping.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/18_loci_ontology_mapping.md` |
