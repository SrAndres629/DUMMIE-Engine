---
spec_id: "DE-V2-L2-34"
title: "Ledger de Decisiones e Interfaz de Alerta"
status: "DRAFT"
layer: "L2"
last_verified_on: "2026-04-24"
---
# Ledger de Decisiones e Interfaz de Alerta

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/34_decision_ledger_auditor.md`
- `doc/specs/34_decision_ledger_auditor.feature`
- `doc/specs/34_decision_ledger_auditor.rules.json`
- `layers/l2_brain/daemon.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/34_decision_ledger_auditor.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/34_decision_ledger_auditor.md` |
| Artefactos hermanos presentes | `doc/specs/34_decision_ledger_auditor.feature` y `doc/specs/34_decision_ledger_auditor.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/34_decision_ledger_auditor.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/34_decision_ledger_auditor.md` |
