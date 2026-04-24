---
spec_id: "DE-V2-L1-30"
title: "Protocolo de Orquestación de Sesiones Flotantes (Floating Context)"
status: "DRAFT"
version: "1.0.0"
layer: "L1"
namespace: "io.dummie.v2.nervous.orchestration"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L1-15"
    relationship: "EXTENDS"
tags: ["orchestration", "floating_sessions", "multi_tenancy", "context_isolation"]
---

# 30. Protocolo de Orquestación de Sesiones Flotantes

## 1. Abstract
Para industrializar el desarrollo agéntico y reducir el sesgo probabilístico, DUMMIE Engine implementa el **Modelo de Sesiones Flotantes**. Cada tarea de desarrollo se ejecuta en un "Nodo Contextual" efímero. Estos nodos son independientes entre sí, compartiendo únicamente la persistencia causal del Cerebro (L2).

## 2. Ciclo de Vida de la Sesión (Apoptosis Controlada)

1.  **Spawn:** El Orquestador crea una instancia de MCP Sidecar con un `SessionID` único.
2.  **Context Injection:** Se carga un sub-conjunto del grafo 4D-TES relevante para la tarea en la memoria de trabajo del nodo.
3.  **Isolated Execution:** El agente opera sobre un `Workspace Shadow` (L0) aislado para evitar colisiones de archivos.
4.  **Crystallization:** Al completar la tarea, los hallazgos se validan y se consolidan en el grafo principal.
5.  **Apoptosis:** La sesión se destruye, liberando recursos y eliminando el sesgo acumulado en la memoria de corto plazo (KV-Cache).

## 3. Direccionamiento via NATS
El ruteo de mensajes se realiza mediante sujetos jerárquicos:
- `core.v2.mcp.session.{SessionID}.request`: Peticiones entrantes.
- `core.v2.mcp.session.{SessionID}.response`: Respuestas del nodo.
- `core.v2.mcp.broadcast.status`: Latidos de salud de todas las sesiones activas.

## 4. Invariantes de Seguridad
- **Namespace Locking:** Una sesión no puede modificar archivos fuera de su namespace asignado sin una `Cross-Locus Permission` validada por el Shield (L3).
- **Causal Sovereignty:** Solo una sesión puede ser `MASTER` de escritura para un `locus_x` específico en un tiempo $t$.

## 5. Integración con Antigravity
El IDE actuará como el orquestador principal de UI, visualizando cada sesión flotante como un hilo de trabajo independiente en el panel de herramientas.
