---
spec_id: "DE-V3-L0-26"
title: "Orquestador de Enjambre Cuántico (Go StateGraph)"
status: "ACTIVE"
layer: "L0_OVERSEER"
last_verified_on: "2026-04-29"
---

# Orquestador de Enjambre Cuántico (Go StateGraph)

## Purpose
Sustituir la orquestación lineal por ejecución paralela basada en StateGraph para habilitar fan-out/fan-in y selección de línea de ejecución más eficiente.

## Current State
Implementado como motor de ejecución principal en L0 mediante Go StateGraph, permitiendo fan-out/fan-in y selección de línea de ejecución eficiente.

## Physical Evidence
- `doc/specs/26_langgraph_quantum_swarm.md`
- `doc/specs/26_langgraph_quantum_swarm.feature`
- `doc/specs/26_langgraph_quantum_swarm.rules.json`
- `layers/l0_overseer/internal/orchestrator/graph.go`
- `layers/l0_overseer/cmd/swarm/main.go`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- El `status` de la spec debe permanecer en estados permitidos por `doc/CORE_SPEC.md`.
- El prototipo StateGraph debe mantener semántica de ejecución paralela (`runParallel`) y merge determinista.
- La evidencia física debe permanecer en rutas Go de L0 y en artefactos hermanos de la spec.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/26_langgraph_quantum_swarm.md
go test ./layers/l0_overseer/internal/orchestrator/... ./layers/l0_overseer/cmd/swarm/...
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | frontmatter + `doc/CORE_SPEC.md` | `python3 scripts/validate_specs_docs.py --check doc/specs/26_langgraph_quantum_swarm.md` |
| Paralelismo y merge | `layers/l0_overseer/internal/orchestrator/graph.go` | `go test ./layers/l0_overseer/internal/orchestrator/...` |
| Integración de prototipo | `layers/l0_overseer/cmd/swarm/main.go` | `go test ./layers/l0_overseer/cmd/swarm/...` |
