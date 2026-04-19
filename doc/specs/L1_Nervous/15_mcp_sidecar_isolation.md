---
spec_id: "DE-V2-L1-15"
title: "Aislamiento Fiduciario de I/O (Modelo FEI)"
status: "ACTIVE"
version: "2.1.0"
layer: "L1"
namespace: "io.dummie.v2.io"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L1-10"
    relationship: "IMPLEMENTS"
tags: ["cognitive_core", "io_isolation", "industrial_sdd"]
---

# 15. Aislamiento Fiduciario de I/O (Modelo FEI)

## Abstract
Para proteger la integridad del bus de datos y evitar el bloqueo del Cerebro (L2) ante latencias de red, el sistema implementa el **Modelo de Aislamiento Fiduciario (FEI)**. Toda interacción con el mundo exterior (MCP Tools) es gestionada por un Sidecar en Go (L1), que desacopla la ejecución física de la inferencia cognitiva.

## 1. Cognitive Context Model (JSON)
```json
{
  "isolation_model": "FEI (Functional Isolation)",
  "sidecar": {
    "tech": "Go (L1)",
    "sandbox": "Bubblewrap",
    "promise_logic": "Topological Promise (Np)"
  },
  "mechanisms": {
    "shadowing": "Shadow Queue (L1) -> Atomic Collapse",
    "resilience": ["Lease Extension", "Time Dilation Signal"],
    "discovery": "Hot-Reload via NATS Broadcast"
  },
  "personality_ref": "DE-V2-L0-33",
  "ledger_link": "DE-V2-L2-34"
}
```

---

## 2. Topología del Sidecar MCP (Go/L1)
- **Desacoplamiento Temporal:** El agente en Python no realiza peticiones de red. Emite una **Intención MCP** a L1.
- **Topological Promise ($Np$):** L1 devuelve una promesa inmediata al flujo temporal. El Cerebro continúa razonando en el multiverso mientras L1 gestiona la I/O física.
- **Sandbox de Ejecución:** Los procesos locales se lanzan mediante **Bubblewrap** (aislamiento de FS y red).

---

## 3. Invariante de Shadowing (Escritura Segura)
Las acciones con efectos secundarios (escrituras en Git, Webhook, DB) operan bajo Shadowing:
1. **Shadow Queue:** L1 retiene la ejecución física de la escritura.
2. **Commit Candidate:** El Cerebro simula el éxito de la operación.
3. **Atomic Collapse:** Go libera la ejecución real solo tras el evento de `CONSENSUS_COMMIT` firmado por el Auditor. Si hay rebobinado, la cola se purga (Safe Revert).

---

## 4. Resiliencia y Backpressure
- **Lease Extension:** Para evitar que Elixir (L0) ejecute apoptosis durante esperas largas de red (ej. HTTP 429), Go emite extensiones de vida cognitivas.
- **Time Dilation Signal:** Si la carga de I/O satura el kernel (file descriptors > 80%), L1 emite una señal que dilata los tiempos de respuesta de los agentes para reducir la presión.

---

## 5. Discovery Epistemológico
- **Hot-Reload de Herramientas:** La adición de plugins MCP en L1 dispara un broadcast de NATS.
- **Update Cognitivo:** L2 actualiza su registro de herramientas en caliente, permitiendo al agente usar nuevas capacidades sin reinicio de la saga.
