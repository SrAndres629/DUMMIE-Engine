---
spec_id: "DE-V2-L0-46"
title: "Demonio Soberano (dummied)"
status: "PROPOSED"
layer: "L0"
last_verified_on: "2026-04-28"
---
# Demonio Soberano (dummied)

## Purpose
Definir el comportamiento contractual del daemon soberano que orquesta ramas, persistencia y recuperación sin depender de una sesión interactiva continua.

## Current State
Existe implementación física en L0 para `dummied`, almacenamiento de estado y orquestación, pero esta spec todavía describe un objetivo parcialmente estabilizado. Debe tratarse como `PROPOSED` hasta que el contrato completo de control y recuperación quede cubierto por verificación trazable.

## Physical Evidence
- `layers/l0_overseer/cmd/dummied/main.go`
- `layers/l0_overseer/internal/orchestrator/store.go`
- `layers/l0_overseer/internal/orchestrator/daemon.go`
- `.aiwg/memory/state.db`

## Contract Invariants
- **Sovereignty:** El daemon es dueño del ciclo de vida de los agentes locales.
- **Persistence:** Todo cambio de estado persistente debe sobrevivir a reinicios del proceso.
- **Async-First:** La espera de input humano no debe bloquear ramas no relacionadas.
- **Resilience:** El daemon debe reconstruir el último estado válido después de un crash.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/46_sovereign_daemon_dummied.md
cd layers/l0_overseer && go test -v ./internal/orchestrator/...
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Persistencia de estado | `layers/l0_overseer/internal/orchestrator/store.go` | `go test -v ./internal/orchestrator/...` |
| Aislamiento de ramas | `layers/l0_overseer/internal/orchestrator/daemon.go` | `go test -v ./internal/orchestrator/...` |
| Bootstrap del daemon | `layers/l0_overseer/cmd/dummied/main.go` | Inspección y pruebas de build |
