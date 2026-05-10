---
spec_id: "DE-V2-[ADR-010](0010-hybrid-diagram-strategy.md)"
title: "Estrategia Híbrida de Mantenimiento Espacial (Diagramación)"
status: "ACTIVE"
version: "1.1.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
tags: ["architectural_decision", "diagramming", "spatial_maintenance"]
---

# [ADR-010](0010-hybrid-diagram-strategy.md): Estrategia Híbrida de Mantenimiento Espacial (Diagramación)

## Abstract
El sistema VCA (Virtual Collective Architecture) requiere actualizar dinámicamente sus modelos mentales visuales ("Mantenimiento Espacial") a medida que el enjambre modifica la base de código. Esta decisión adopta una **Estrategia Híbrida** que permite elegir entre Mermaid, PlantUML o representaciones LST según el contexto, garantizando la flexibilidad sin sacrificar el rigor arquitectónico.

## 1. Cognitive Context Model (Ref)
Para los formatos autorizados, las reglas de selección de motor y los invariantes de renderizado, consulte el archivo hermano [0010-hybrid-diagram-strategy.rules.json](./0010-hybrid-diagram-strategy.rules.json).

---

## 2. Contexto
Surgió la necesidad de definir un estándar para la visualización de estructuras físicas complejas y flujos de decisión que cambian frecuentemente. Un formato único (solo Mermaid o solo PlantUML) limitaba la expresividad del enjambre ante diferentes niveles de abstracción.

---

## 3. Decisión: Estrategia Híbrida Guiada por el Contexto
El enjambre tiene la autonomía de elegir el motor de renderizado visual más adecuado para cada problema:

1.  **Mermaid (`.mmd` o embebido en Markdown):** Para diagramas de flujo interactivos, secuencias de eventos y diagramas de estado rápidos. Ideal para visualizar los Contratos Gherkin.
2.  **PlantUML (Modelo C4):** Para representar arquitecturas estáticas de alto nivel (Containers, Components, Code) y mapas topológicos del Bounded Context.
3.  **Memoria Vectorial/Textual LST (Latent Semantic Tree):** Cuando un diagrama visual es insuficiente, el enjambre construirá representaciones topológicas abstractas en formato JSON/YAML dentro de `.aiwg/` para su propio consumo cognitivo.

---

## 4. Consecuencias
- **Flexibilidad Máxima:** Permite documentar desde flujos simples hasta topologías de red densas.
- **Sobrecarga de Herramientas:** El agente de arquitectura debe asegurar la disponibilidad de los motores de renderizado.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [0010-hybrid-diagram-strategy.feature](./0010-hybrid-diagram-strategy.feature)
- **Machine Rules:** [0010-hybrid-diagram-strategy.rules.json](./0010-hybrid-diagram-strategy.rules.json)
