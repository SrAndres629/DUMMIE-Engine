# PHYSICAL_MAP

## Propósito
Mapa de verdad física del sistema para evitar deriva entre diseño teórico y estado implementado.

## Estado físico actual (verificado)

### L0 (`layers/l0_overseer`)
- Runtime/base Elixir con `mix.exs` y módulo de aplicación.
- Evidencia: `layers/l0_overseer/mix.exs`, `layers/l0_overseer/lib/overseer/application.ex`.

### L1 (`layers/l1_nervous`)
- Gateway MCP FastMCP (`mcp_server.py`) y bootstrap hacia L2.
- Bridge/proxy de servidores MCP secundarios (`mcp_proxy.py`).
- Binarios y contratos Go presentes (`main.go`, `sidecar.go`, `proto/*.pb.go`).

### L2 (`layers/l2_brain`)
- Dominio/orquestación en estructura plana (`models.py`, `orchestrator.py`, `daemon.py`).
- Adaptadores de ledger/Kuzu en estado bridge (`adapters.py`).
- Daemon con planner jerárquico obligatorio y outcome explícito de saga (`SUCCESS`/`FAILED`).
- Tests alineados al layout físico actual (`layers/l2_brain/tests`).

### L3 (`layers/l3_shield`)
- Auditores Python (`topological_auditor.py`, `budget_auditor.py`, `compliance_auditor.py`).
- Biblioteca Rust `shield` con función `audit_intent`.

### L4 (`layers/l4_edge`)
- Descubrimiento de capacidades MCP (`tool_discovery.py`).
- Observador de archivos en estado placeholder (`file_watcher.py`).

### L5 (`layers/l5_muscle`)
- Driver MCP y manager de sandbox en Python.
- Compactor de memoria con pipeline inicial (`compactor.py`).

### L6 (`layers/l6_skin`)
- Proyecto frontend con Vite/React/TypeScript (`package.json`).

## Brechas físico-teóricas prioritarias
1. Contratos de modelos (`AuthorityLevel`, `IntentType`, `AgentIntent`) no alineados entre L1 y L2.
2. Contratos de resultado/telemetría del daemon no están formalizados para consumidores inter-capa.
3. Parte de specs sigue en plantilla genérica y sin verificación trazable.
4. Existen artefactos históricos fuera del contrato documental vigente que deben mantenerse fuera del contexto operativo.

## Semáforo de estado
- `ACTIVE`: respaldado por evidencia física en el repo.
- `DRAFT`: diseño parcial o en transición.
- `PROPOSED`: hipótesis/roadmap sin implementación actual.
- `DEPRECATED`: referencia histórica fuera de la arquitectura vigente.

## Regla operativa
Cualquier cambio de arquitectura debe actualizar este mapa y el índice maestro (`doc/CORE_SPEC.md`) en el mismo lote de trabajo.
