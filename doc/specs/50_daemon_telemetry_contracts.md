---
spec_id: "DE-V2-L0-50"
title: "Daemon Telemetry & Outcome Contracts"
status: "ACTIVE"
layer: "L0"
last_verified_on: "2026-04-29"
---
# Daemon Telemetry & Outcome Contracts

## Purpose
Definir los contratos formales para la telemetría del daemon y los estados de resultado de las sagas (`SUCCESS`/`FAILED`) para consumidores inter-capa.

## Current State
Implementado parcialmente en `layers/l0_overseer/internal/orchestrator/daemon.go`. Esta spec formaliza el contrato esperado.

## Physical Evidence
- `layers/l0_overseer/internal/orchestrator/daemon.go`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- **Outcome Enum**: El resultado de una saga debe ser estrictamente `SUCCESS` o `FAILED`.
- **Event Schema**: Los eventos de telemetría deben incluir `timestamp`, `component`, `event_type` y `payload`.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/50_daemon_telemetry_contracts.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Outcome Enum | `layers/l0_overseer/internal/orchestrator/daemon.go` | Inspección de código |
| Event Schema | `layers/l0_overseer/internal/orchestrator/daemon.go` | Inspección de código |
