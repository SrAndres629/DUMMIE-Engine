---
spec_id: "DE-V2-L2-31"
title: "Análisis de Impacto y Radio de Explosión"
status: "ACTIVE"
version: "2.2.0"
layer: "L2"
namespace: "io.dummie.v2.brain"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L2-02"
    relationship: "REQUIRES"
tags: ["cognitive_core", "brain_logic", "industrial_sdd"]
---

# 31. Análisis de Impacto y Radio de Explosión

## Abstract
El componente de Análisis de Impacto cuantifica el **Blast Radius** de cualquier cambio propuesto en el sistema. Utilizando el Palacio de Loci (L4) y el motor de grafos KùzuDB, este componente identifica las dependencias directas e indirectas que podrían verse comprometidas, proporcionando una métrica de riesgo que rige la aprobación automática o el veto de las Sagas.

## 1. Cognitive Context Model (Ref)
Para el motor de grafos utilizado, los tipos de análisis requeridos (Recursive Deps, Side Effects) y los umbrales de puntuación de confianza (Confidence Score), consulte el archivo hermano [31_impact_analytics_blast_radius.rules.json](./31_impact_analytics_blast_radius.rules.json).

---

## 2. Tipología de Impacto
Se definen tres niveles de radio de explosión:
- **LOCAL:** El cambio solo afecta al nodo atómico actual. Riesgo bajo.
- **NEIGHBORHOOD:** El cambio afecta a componentes en la misma capa o dependencias directas. Riesgo moderado.
- **GLOBAL:** El cambio afecta a capas fundamentales (L0, L1) o contratos transversales. Requiere consenso del PAH.

---

## 3. Veto de Riesgo Global
Si el Análisis de Impacto detecta un riesgo global con una confianza inferior al 95%, el sistema ejecuta un **Veto Automático**. La Saga es bloqueada y se genera un informe de riesgos detallado para el Auditor L2, sugiriendo rutas alternativas de menor impacto.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [31_impact_analytics_blast_radius.feature](./31_impact_analytics_blast_radius.feature)
- **Machine Rules:** [31_impact_analytics_blast_radius.rules.json](./31_impact_analytics_blast_radius.rules.json)
