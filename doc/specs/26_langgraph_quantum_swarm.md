---
spec_id: "DE-V3-L0-26"
title: "Orquestador de Enjambre Cuántico (Go StateGraph)"
status: "PROPOSED"
layer: "L0_OVERSEER"
last_verified_on: "2026-04-24"
---

# Orquestador de Enjambre Cuántico (Go StateGraph)

## Purpose
Sustituir la orquestación lineal y frágil por un sistema de ejecución paralelo basado en Grafos de Estado (StateGraph), permitiendo la multiplicidad de agentes y la resolución por consenso o velocidad.

## Architecture
- **State (Floating Session State):** Objeto en Go que viaja por el grafo, clonándose en ramificaciones paralelas.
- **Nodes (Agentes):** Funciones asíncronas en Go que ejecutan tareas específicas.
- **Quantum Merge:** Lógica de fusión que selecciona la mejor línea de tiempo (time-to-success) y consolida el estado.

## Implementation Details (Go)
- **Path:** `layers/l0_overseer/internal/orchestrator/graph.go`
- **Concurrency:** Goroutines + `sync.WaitGroup` para el Fan-out.
- **Sovereignty:** Cada rama puede operar en un `Shadow Worktree` independiente.

## Success Evidence (Audit 2026-04-24)
Ejecución exitosa del comando `swarm` demostrando:
1. Planificación centralizada.
2. Ejecución paralela de estrategias (Aggressive vs Conservative).
3. Fusión atómica del estado final basada en la primera respuesta válida.

## Next Steps
1. Integración con el `SkillIngester`.
2. Implementación de `Juez Node` para evaluación semántica de resultados paralelos.
3. Conexión con el Brain (L2) vía gRPC.
