---
spec_id: "DE-V2-L1-15"
title: "Aislamiento Fiduciario de I/O (Modelo FEI)"
status: "ACTIVE"
version: "2.2.0"
layer: "L1"
namespace: "io.dummie.v2.io"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L1-10"
    relationship: "IMPLEMENTS"
tags: ["cognitive_core", "io_isolation", "industrial_sdd"]
---

# 15. Aislamiento Fiduciario de I/O y Servidor MCP (Modelo FEI)

## Abstract
Para proteger la integridad del bus de datos y estandarizar la conectividad agéntica, el sistema implementa el **Modelo de Aislamiento Fiduciario (FEI)**. Toda interacción se gestiona mediante un **Servidor MCP Universal**. Este Sidecar actúa como el "Puerto USB-C" del sistema, operando bajo la **Política de Lógica Cero**: no contiene reglas de dominio, delegando toda decisión cognitiva al Cerebro (L2).

## 1. Cognitive Context Model (Ref)
Para el modelo de aislamiento (Bubblewrap), la lógica de promesas topológicas (Np) y los mecanismos de resiliencia ante backpressure de I/O, consulte el archivo hermano [15_mcp_sidecar_isolation.rules.json](./15_mcp_sidecar_isolation.rules.json).

---

## 2. Topología del Sidecar MCP (Go/L1)
- **Desacoplamiento Temporal:** El agente en Python no realiza peticiones de red. Emite una **Intención MCP** a L1.
- **Topological Promise ($Np$):** L1 devuelve una promesa inmediata al flujo temporal. El Cerebro continúa razonando mientras L1 gestiona la I/O física.
- **Sandbox de Ejecución:** Los procesos locales se lanzan mediante **Bubblewrap** (aislamiento de FS y red).

---

## 3. Invariante de Shadowing (Escritura Segura)
Las acciones con efectos secundarios (Git, Webhook, DB) operan bajo Shadowing:
1. **Shadow Queue:** L1 retiene la ejecución física de la escritura.
2. **Commit Candidate:** El Cerebro simula el éxito de la operación.
3. **Atomic Collapse:** Go libera la ejecución real solo tras el evento de `CONSENSUS_COMMIT`.

---

## 4. Resiliencia y Backpressure
- **Lease Extension:** Para evitar apoptosis durante esperas de red, Go emite extensiones de vida cognitivas hacia Elixir (L0).
- **Time Dilation Signal:** Si la carga de I/O satura el kernel, L1 emite una señal que dilata los tiempos de respuesta de los agentes.

---

## 5. El Servidor MCP como HUB de Integración
- **Exposición de Memoria:** L1 actúa como el puente MCP hacia el 4D-TES (L2), permitiendo que agentes externos lean y escriban en la memoria soberana sin acceso directo al sistema de archivos.
- **Hot-Reload de Herramientas:** La adición de plugins MCP en L1 dispara un broadcast de NATS.
- **Update Cognitivo:** L2 actualiza su registro de herramientas en caliente.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [15_mcp_sidecar_isolation.feature](./15_mcp_sidecar_isolation.feature)
- **Machine Rules:** [15_mcp_sidecar_isolation.rules.json](./15_mcp_sidecar_isolation.rules.json)
