---
spec_id: "DE-V2-[ADR-009](0009-l2-brain-bounded-contexts.md)"
title: "Agrupación de Micro-Dominios L2 en Bounded Contexts"
status: "ACTIVE"
version: "1.1.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
tags: ["architectural_decision", "bounded_contexts", "l2_brain"]
---

# [ADR-009](0009-l2-brain-bounded-contexts.md): Agrupación de Micro-Dominios L2 en Bounded Contexts

## Abstract
Durante la implementación Greenfield de `L2_Brain` (NODE_4), se identificó el riesgo de micro-fragmentación arquitectónica debido a la alta densidad de especificaciones. Esta decisión consolida las 13 especificaciones de lógica pura en 4 **Bounded Contexts** macro (Context, Memory, Fabrication, Governance) para garantizar la cohesión semántica y reducir el acoplamiento en la capa de Aplicación.

## 1. Cognitive Context Model (Ref)
Para el mapeo de especificaciones por contexto y los invariantes de aislamiento estricto, consulte el archivo hermano [0009-l2-brain-bounded-contexts.rules.json](./0009-l2-brain-bounded-contexts.rules.json).

---

## 2. Contexto
Implementar las 13 especificaciones de L2 (Specs 12, 02, 09, 36, 38, 21, 28, 29, 37, 27, 31, 34, 39) como módulos independientes corría el riesgo de generar "Domain Bloat", dificultando la orquestación cognitiva.

---

## 3. Decisión: Consolidación de Dominios
Se decide consolidar las 13 especificaciones en 4 **Bounded Contexts** macro dentro de la capa Domain de la Arquitectura Hexagonal:

1. **Context** (Spec 12): Manejo de vectores espaciotemporales y relevancia (6D-Context).
2. **Memory** (Specs 02, 09, 36, 38): Manejo de almacenamiento, nodos cristalizados, y el ledger de sesión.
3. **Fabrication** (Specs 21, 28, 29, 37): Intenciones agénticas, YAML de habilidades y el descubrimiento A2A.
4. **Governance** (Specs 27, 31, 34, 39): El bucle Kaizen, auditoría de impacto y consistencia semántica.

---

## 4. Consecuencias
- **Positivas:** Cohesión semántica alta. Los adaptadores interactúan con solo 4 facadas lógicas.
- **Negativas:** Algunas entidades (como `AgentIntent`) pueden necesitar mapeos cruzados resueltos en el `CognitiveOrchestrator`.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [0009-l2-brain-bounded-contexts.feature](./0009-l2-brain-bounded-contexts.feature)
- **Machine Rules:** [0009-l2-brain-bounded-contexts.rules.json](./0009-l2-brain-bounded-contexts.rules.json)
