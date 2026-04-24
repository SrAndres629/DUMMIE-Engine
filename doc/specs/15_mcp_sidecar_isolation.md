---
spec_id: "DE-V2-L1-15"
title: "Aislamiento de I/O y Adaptador MCP (Modelo FEI)"
status: "ACTIVE"
version: "2.3.0"
layer: "L1"
namespace: "io.dummie.v2.io"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L1-10"
    relationship: "IMPLEMENTS"
tags: ["cognitive_core", "io_isolation", "industrial_sdd", "mcp"]
---

# 15. Aislamiento de I/O y Adaptador MCP (Modelo FEI)

## Abstract
Para proteger la integridad del bus de datos y estandarizar la conectividad agéntica, el sistema implementa el **Modelo de Adaptación de I/O (FEI)**. Toda interacción se gestiona mediante un **Servidor MCP (Model Context Protocol)**. Este componente actúa como el "Puerto USB-C" del sistema, operando bajo la **Política de Lógica Cero**: no contiene reglas de dominio, delegando toda decisión cognitiva al Cerebro (L2) a través de casos de uso estandarizados.

## 1. Arquitectura Híbrida (Go/Python)
El sistema L1 opera en dos capas para maximizar la resiliencia y la facilidad de integración:
- **Sidecar de Transporte (Go):** Gestiona el puente de mensajería (NATS) y la monitorización de bajo nivel.
- **Adaptador de Herramientas (Python/FastMCP):** Expone la lógica de negocio de L2 hacia el exterior mediante el estándar MCP. Permite una integración nativa con orquestadores como Claude Desktop o Antigravity.

---

## 2. Topología del Adaptador MCP
- **Desacoplamiento Temporal:** El agente emite una **Intención MCP**. El adaptador la traduce a un `AgentIntent` para el Cerebro.
- **Topological Promise ($Np$):** L2 devuelve un estado `INTENT_QUEUED_L2_VALIDATED`. El adaptador informa éxito inmediato al agente externo mientras la persistencia física ocurre de forma asíncrona en el 4D-TES.
- **Aislamiento de Recursos:** El acceso a la memoria soberana (`loci.db`) está protegido por un sistema de arbitraje de bloqueos.

---

## 3. Invariante de Shadowing (Escritura Segura)
Las acciones con efectos secundarios operan bajo Shadowing:
1. **Shadow Queue:** El adaptador recibe la petición y la valida contra el Shield (L3).
2. **Commit Candidate:** El Cerebro simula el éxito y genera un hash causal previo.
3. **Atomic Collapse:** El cambio se consolida en el Merkle-DAG solo tras la validación de integridad estructural.

---

## 4. Resiliencia y Backpressure
- **Degraded Mode:** Si el sistema detecta que otra instancia (MASTER) tiene el control exclusivo de la base de datos, el adaptador entra automáticamente en modo **READER (Read-Only)**.
- **Signals:** El adaptador emite un estado `Degraded` en el recurso `brain://health`.

---

## 5. El Servidor MCP como HUB de Integración
- **Exposición de Memoria:** Permite que agentes externos lean y escriban en la memoria soberana sin acceso directo al sistema de archivos.
- **Hot-Reload:** Soporte para la adición dinámica de herramientas (Skills) sin reinicio del motor.

---

## 6. Arbitraje de Persistencia (Multi-Tenancy)
Para escenarios donde múltiples clientes agénticos requieren acceso simultáneo:

### 6.1 Estados de Instancia
1. **MASTER (Write-Enabled):** La primera instancia en adquirir el lock exclusivo.
2. **READER (Read-Only):** Instancias subsiguientes. Operan con `read_only=True` en KuzuDB.

### 6.2 Manejo de Colisiones
Si se solicita una escritura a un **READER**, responde con `ERR_MEMORY_LOCKED`.

---

## [MSA] Sibling Components Requeridos
- **Executable Contract:** [15_mcp_sidecar_isolation.feature](./15_mcp_sidecar_isolation.feature)
- **Machine Rules:** [15_mcp_sidecar_isolation.rules.json](./15_mcp_sidecar_isolation.rules.json)
