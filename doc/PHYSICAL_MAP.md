---
status: ACTIVE
layer: meta
domain: [physical-map, layer-map, architecture]
---
# PHYSICAL_MAP

## Propósito
Mapa de verdad física del sistema para evitar deriva entre diseño teórico y estado implementado.

## Estado físico actual (verificado)

### L0 (`layers/l0_overseer`)
- **Control Plane**: Monitor de salud y orquestación de ciclo de vida.
- **Go Orchestrator**: Motor de enjambre basado en StateGraph (`internal/orchestrator/graph.go`) y gestión de habilidades (`internal/orchestrator/skills.go`).
- Binarios Go (`cmd/monitor/main.go`, `cmd/overseer/main.go`, `cmd/swarm/main.go`, `cmd/dummied/main.go`).
- Runtime base Elixir mantenido para orquestación reactiva.
- Socket de control canónico en `.aiwg/sockets/dummied.sock`.

### L1 (`layers/l1_nervous`)
- **Data Plane (Memory Plane)**: Servidor Arrow Flight tipado (`cmd/memory/main.go`).
- **Nervous Infrastructure**: Gateway MCP FastMCP (`mcp_server.py`) con bootstrap estricto.
- **SMART MetaGateway (canonical)**: Dispatcher central con cache semántico 2-capas (`semantic_cache.py`), router con modelo pequeño (`smart_router.py`), disclosure progresivo de tools en 3 tiers (`context_budget_tools.py`), ejecución DAG de skills (`skill_executor.py`), entry point canónico `dummie_process`. Ver `doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md`.
- **Skill Ingestion Pipeline**: Contratos Protobuf (`proto/skill.proto`) e integración de herramientas (`tools.py`). Skills incorporados: TDD, code_review, systematic_debugging, explore_codebase.
- **Typed SDK**: Generador dinámico (`sdk_generator.py`) y clientes generados (`generated/`).
- **Zero-Copy IPC**: Bridge tipado en `memory_ipc.py` con excepciones estructuradas.
- **Atomicidad**: `utils.py` con `AtomicLedgerWriter` (flock).
- **Local Reasoning Gateway**: Tools MCP en modo sombra para recall, rerank, context shaping y feedback medible.
- **Pruebas**: `tests/test_smart_components.py` (38 tests). `tests/bench_metagateway.py` (benchmark suite).
- **Sub-gateways HTTP (legacy)**: `gateway/*.py` en puertos 8081-8085 — deprecados, servicios systemd enmascarados. Reemplazados por MCPProxyManager STDIO directo.

### L2 (`layers/l2_brain`)
- Dominio/orquestación en estructura plana (`models.py`, `orchestrator.py`, `daemon.py`).
- Adaptadores de ledger/Kuzu en estado bridge (`adapters.py`).
- Daemon con planner jerárquico obligatorio y outcome explícito de saga (`SUCCESS`/`FAILED`).
- Contratos de razonamiento local para proveedores Gemma/Ollama, OpenAI-compatible y fallback determinista.
- Tests alineados al layout físico actual (`layers/l2_brain/tests`).

### L3 (`layers/l3_shield`)
- Auditores Python (`topological_auditor.py`, `budget_auditor.py`, `compliance_auditor.py`).
- Biblioteca Rust `shield` con función `audit_intent`.

### L4 (`layers/l4_edge`)
- Descubrimiento de capacidades MCP (`tool_discovery.py`).
- Observador de archivos explícitamente deshabilitado hasta tener backend real (`file_watcher.py`).

### L5 (`layers/l5_muscle`)
- Driver MCP y manager de sandbox en Python.
- Compactor de memoria con pipeline inicial (`compactor.py`).

### L6 (`layers/l6_skin`)
- Proyecto frontend con Vite/React/TypeScript (`package.json`).

## Brechas físico-teóricas prioritarias
1. Contratos de modelos (`AuthorityLevel`, `IntentType`, `AgentIntent`) alineados en la ruta oficial L1/L2: `layers/l1_nervous/domain/models.py` reexporta la SSoT de `layers/l2_brain/models.py`. Riesgo remanente: existen definiciones Protobuf generadas y modelos legacy bajo `layers/l2_brain/src/brain/domain/` que no deben tratarse como SSoT Python.
2. Contratos de resultado/telemetría del daemon no están formalizados para consumidores inter-capa.
3. Parte de specs sigue en plantilla genérica y sin verificación trazable (Specs 26 y 29 actualizadas a ACTIVE).
4. Existen artefactos históricos fuera del contrato documental vigente que deben mantenerse fuera del contexto operativo.

## Semáforo de estado
- `ACTIVE`: respaldado por evidencia física en el repo.
- `DRAFT`: diseño parcial o en transición.
- `PROPOSED`: hipótesis/roadmap sin implementación actual.
- `DEPRECATED`: referencia histórica fuera de la arquitectura vigente.

## Regla operativa
Cualquier cambio de arquitectura debe actualizar este mapa y el índice maestro (`doc/CORE_SPEC.md`) en el mismo lote de trabajo.
