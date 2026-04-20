---
status: "ACCEPTED"
date: "2026-04-20"
deciders: ["sw.arch.core", "Humano PAH"]
supersedes: ""
tags: ["arquitectura", "mantenimiento_espacial", "diagramas"]
---

# ADR 0010: Estrategia Híbrida de Mantenimiento Espacial (Diagramación)

## Contexto
El sistema VCA (Virtual Collective Architecture) requiere actualizar dinámicamente sus modelos mentales visuales ("Mantenimiento Espacial") a medida que el enjambre modifica la base de código. Surgió la necesidad de definir un formato estándar: ¿Mermaid, PlantUML (C4) o un enfoque libre?

## Decisión
Se adopta una **Estrategia Híbrida Guiada por el Contexto**. El enjambre tiene la autonomía de elegir el motor de renderizado visual más adecuado para cada problema:

1.  **Mermaid (`.mmd` o embebido en Markdown):** Para diagramas de flujo interactivos, secuencias de eventos y diagramas de estado rápidos. Ideal para visualizar los Contratos Gherkin.
2.  **PlantUML (Modelo C4):** Para representar arquitecturas estáticas de alto nivel (Containers, Components, Code) y mapas topológicos del Bounded Context.
3.  **Memoria Vectorial/Textual LST (Latent Semantic Tree):** Cuando un diagrama visual es insuficiente o demasiado denso, el enjambre construirá representaciones topológicas abstractas en formato JSON/YAML dentro de `.aiwg/` para su propio consumo cognitivo.

## Consecuencias
- El Agente 2 (Architect) debe instalar herramientas o dependencias adicionales si requiere renderizar PlantUML.
- Otorga máxima flexibilidad al enjambre para documentar estructuras físicas complejas sin forzarlas a un formato visual restrictivo.
