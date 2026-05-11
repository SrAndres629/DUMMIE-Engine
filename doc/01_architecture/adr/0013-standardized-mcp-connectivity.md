---
spec_id: "DE-V2-[ADR-0013](0013-standardized-mcp-connectivity.md)"
title: "Interoperabilidad Universal de Agentes vía MCP (Estrategia USB-C)"
status: "ACCEPTED"
version: "1.0.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-[ADR-005](0005-cognitive-fabrication-protocols.md)"
    relationship: "EXTENDS"
  - id: "DE-V2-L1-15"
    relationship: "REINFORCES"
tags: ["architectural_decision", "mcp", "interoperability", "industrial_sdd"]
---

# [ADR-0013](0013-standardized-mcp-connectivity.md): Interoperabilidad Universal de Agentes vía MCP

## Abstract
Para que DUMMIE Engine cumpla su promesa de **Soberanía Cognitiva**, no puede depender de las interfaces propietarias de los proveedores de LLM. Esta decisión establece el **Model Context Protocol (MCP)** como el estándar universal de conexión (USB-C) para integrar cualquier agente de IA con la memoria (4D-TES), el contexto (6D) y las herramientas de fabricación del motor.

## 1. Cognitive Context Model (Ref)
Para los esquemas JSON de las herramientas MCP, las definiciones de recursos y los protocolos de seguridad de transporte, consulte el archivo hermano [0013-standardized-mcp-connectivity.rules.json](./0013-standardized-mcp-connectivity.rules.json).

---

## 2. Contexto
La fragmentación de APIs de agentes y la falta de un estándar para el intercambio de contexto generan "amnesia sistémica" y dificultan la portabilidad del cerebro del sistema. DUMMIE Engine requiere una capa de abstracción que permita "enchufar" diferentes cerebros (Gemini, Claude, GPT, Modelos Locales) sin modificar la infraestructura de la factoría.

---

## 3. Decisión: MCP como Interfaz Universal
Se formaliza el uso de **MCP** como el protocolo de comunicación primario en todas las capas del sistema.

### 3.1 El DUMMIE Memory MCP Server
La capa de memoria (.aiwg + KùzuDB) se expone como un servidor MCP soberano que proporciona:
- **Tools:** `crystallize_decision`, `log_lesson`, `resolve_ambiguity`.
- **Resources:** Acceso directo a los esquemas de las Specs, historial de decisiones y el Grafo de Loci.
- **Prompts:** Plantillas de razonamiento predefinidas (Arquitecto, Ingeniero, Auditor).

### 3.2 La Metáfora del USB-C y los Tres Pilares de Pureza
MCP actúa como un puerto físico estandarizado. Para evitar la degradación del motor, se imponen tres restricciones arquitectónicas:

1.  **Aislamiento de Capa (L1/L6 Interface):** El servidor MCP reside exclusivamente en las capas de interfaz (L6) o transporte (L1). No debe contaminar la lógica pura del Cerebro (L2).
2.  **Servidor de Lógica Zero (Dumb Adapter):** El `mcp_server` debe ser un adaptador hexagonal puro. Tiene terminantemente prohibido contener reglas de negocio; su única función es mapear llamadas MCP a Casos de Uso del Dominio (L2).
3.  **Generación Dirigida por Specs (SDD):** La interfaz MCP (herramientas y recursos) debe derivarse de los contratos Protobuf y las Specs de Layer 1, garantizando que el "puerto" sea un reflejo exacto de la capacidad física del sistema.

---

## 4. Realización Física: Agente de Sistema Residente

El motor se implementa como un servicio MCP residente que actúa como el "Sistema Operativo Cognitivo" del repositorio.

### 4.1. Arquitectura de Conexión
- **Servidor:** `layers/l1_nervous/adapters/mcp/server.py`
- **Protocolo:** JSON-RPC sobre Stdio (MCP Standard).
- **Alcance:** Proporciona acceso unificado a las 4 dimensiones de la memoria (4D-TES) y los 6 vectores de contexto (6D).

### 4.2. Configuración Plug & Play
Para activar el Agente de Sistema, cualquier entorno compatible debe importar el archivo [dummie_agent_config.json](../../../dummie_agent_config.json). Esto garantiza que el cerebro esté siempre disponible como una capacidad nativa del entorno de desarrollo.

---

## 5. Invariantes de Seguridad y Soberanía
- **Aislamiento fiduciario:** Las llamadas MCP son auditadas por el Escudo L3 antes de su ejecución física.
- **Soberanía de Datos:** El servidor MCP reside localmente, garantizando que el conocimiento nunca abandone el entorno controlado del monorepo.
- **Determinismo:** Las respuestas del servidor MCP incluyen el `CausalHash` para asegurar la trazabilidad 4D-TES.

---

## 6. Consecuencias
- **Positivas:** Desacoplamiento total del proveedor de IA. Mejora drástica en la precisión de los agentes al proporcionarles herramientas de "Grado Industrial".
- **Negativas:** Requiere que los agentes soporten MCP (actualmente un estándar en expansión).

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [0013-standardized-mcp-connectivity.feature](./0013-standardized-mcp-connectivity.feature)
- **Machine Rules:** [0013-standardized-mcp-connectivity.rules.json](./0013-standardized-mcp-connectivity.rules.json)
