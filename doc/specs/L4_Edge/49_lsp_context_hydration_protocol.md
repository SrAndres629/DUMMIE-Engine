---
spec_id: "DE-V2-L4-49"
title: "Protocolo de Hidratación Semántica LSP (Semantic Bridge)"
status: "ACTIVE"
version: "1.0.0"
layer: "L4"
namespace: "io.dummie.v2.edge.lsp"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L4-18"
    relationship: "REFINES_ONTOLOGY"
  - id: "DE-V2-L1-41"
    relationship: "CONSUMES_VIA_ACP"
tags: ["edge_layer", "lsp", "semantic_hydration", "ast_analysis", "claw_ism"]
---

# 49. Protocolo de Hidratación Semántica LSP (Semantic Bridge)

## Abstract
Para trascender la limitación de la "visión ciega" (dependencia de OCR/Imágenes), esta especificación dota al sistema de un **Puente Semántico** directo con los Language Servers del IDE. En lugar de procesar píxeles de código, el sistema consume estructuras de datos ricas (LST, Símbolos, Referencias y Diagnósticos), permitiendo al Cerebro L2 operar con una profundidad arquitectónica de nivel Principal Engineer y un ahorro del 90% en el uso de tokens.

## 1. El Hidratador Semántico (L4 Bridge)
El Hidratador Semántico actúa como un traductor entre el protocolo ACP del IDE y el LST (Latent Semantic Tree) del sistema:

- **Ingesta de Símbolos**: Obtiene la jerarquía completa de clases, métodos y variables del archivo abierto.
- **Detección de Referencias**: Permite al agente navegar por el grafo de dependencias ("¿Dónde se usa esta función?") sin abrir físicamente cada archivo.
- **Consumo de Diagnósticos**: Inyecta errores de linter y compilación directamente en el contexto del agente para disparar bucles de **Self-Healing** preventivos.

---

## 2. Optimización del Contexto Contextual
En lugar de enviar el archivo completo al LLM:
1.  **Zonificación LSP**: El sistema identifica el cursor del usuario y extrae el "Contexto Inmediato" (la función actual y sus imports relacionados).
2.  **Skeletal Representation**: Genera una versión "esqueleto" del monorepo basada en las firmas de los métodos, permitiendo al agente entender el Blast Radius de un cambio sin saturar la ventana de contexto.

---

## 3. Invariantes de Sincronización
- **Atomicidad Visual-Semántica**: Si la telemetría visual (L6) y los datos LSP (L4) entran en conflicto, prevalecerá la Verdad Física del LSP.
- **Latency Guard**: La hidratación semántica debe ocurrir en paralelo a la telemetría de latidos para evitar el lag perceptual del agente.

---

## [MSA] Sibling Components
- **Executable Contract**: [49_lsp_context_hydration_protocol.feature](49_lsp_context_hydration_protocol.feature)
- **Machine Rules**: [49_lsp_context_hydration_protocol.rules.json](49_lsp_context_hydration_protocol.rules.json)
