---
spec_id: "DE-V2-L4-49"
title: "Protocolo de Hidratación Semántica LSP (Semantic Bridge)"
status: "ACTIVE"
version: "2.2.0"
layer: "L4"
namespace: "io.dummie.v2.edge.lsp"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L4-18"
    relationship: "REFINES_ONTOLOGY"
  - id: "DE-V2-L1-41"
    relationship: "CONSUMES_VIA_ACP"
tags: ["edge_layer", "lsp", "semantic_hydration", "lst_analysis"]
---

# 49. Protocolo de Hidratación Semántica LSP (Semantic Bridge)

## Abstract
Para trascender la limitación de la "visión ciega", el sistema implementa un **Puente Semántico** con los Language Servers del IDE. En lugar de procesar texto plano, el sistema consume estructuras ricas (LST, Símbolos, Referencias), permitiendo al Cerebro L2 operar con profundidad arquitectónica y reduciendo drásticamente el uso de tokens mediante la hidratación selectiva de contexto.

## 1. Cognitive Context Model (Ref)
Para la profundidad máxima de contexto (LST Depth), la política de extracción de esqueletos (Skeletal Extraction) y los requisitos de versión del servidor LSP, consulte el archivo hermano [49_lsp_context_hydration_protocol.rules.json](./49_lsp_context_hydration_protocol.rules.json).

---

## 2. El Hidratador Semántico (L4 Bridge)
El Hidratador actúa como un traductor entre el protocolo ACP y el LST del sistema:
- **Symbol Ingestion:** Obtención de la jerarquía completa de objetos en el archivo activo.
- **Reference Tracking:** Navegación por el grafo de dependencias sin necesidad de lectura física de archivos.
- **Diagnostic Consumption:** Inyección de errores de linter y compilación directamente en el bucle de autosanación ([Spec 40](40_self_healing_remediation_loop.md)).

---

## 3. Optimización del Contexto (Zonificación)
En lugar de saturar la ventana de contexto del LLM:
1.  **Cursor Zoning:** Identificación del foco de trabajo y extracción del contexto inmediato.
2.  **Skeletal Representation:** Generación de versiones resumidas (solo firmas de métodos e interfaces) del monorepo.
3.  **Visual-Semantic Sync:** En caso de conflicto entre la telemetría visual (L6) y los datos LSP (L4), prevalece la Verdad Física del LSP.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [49_lsp_context_hydration_protocol.feature](./49_lsp_context_hydration_protocol.feature)
- **Machine Rules:** [49_lsp_context_hydration_protocol.rules.json](./49_lsp_context_hydration_protocol.rules.json)
