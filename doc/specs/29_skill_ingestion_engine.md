---
spec_id: "DE-V2-CROSS-29_SKILL_INGESTION_ENGINE"
title: "Skill Ingestion Engine"
status: "ACTIVE"
layer: "CROSS"
last_verified_on: "2026-04-29"
---
# Skill Ingestion Engine

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Implementado como pipeline de ingesta automatizado que mapea herramientas MCP a Blueprints cognitivos y genera el archivo maestro de capacidades.

## Physical Evidence
- `doc/specs/29_skill_ingestion_engine.md`
- `doc/specs/29_skill_ingestion_engine.feature`
- `doc/specs/29_skill_ingestion_engine.rules.json`
- `layers/l1_nervous/proto/skill.proto`
- `layers/l1_nervous/tools.py`
- `layers/l0_overseer/internal/orchestrator/skills.go`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/29_skill_ingestion_engine.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/29_skill_ingestion_engine.md` |
| Artefactos hermanos presentes | `doc/specs/29_skill_ingestion_engine.feature` y `doc/specs/29_skill_ingestion_engine.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/29_skill_ingestion_engine.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/29_skill_ingestion_engine.md` |
