---
status: "ACCEPTED"
date: "2026-04-18"
deciders: ["sw.arch.core", "Humano PAH"]
supersedes: ""
tags: ["arquitectura", "dominio", "l2_brain", "bounded_contexts"]
---

# ADR-0009: Agrupación de Micro-Dominios L2 en Bounded Contexts

## Estado
Aceptado

## Contexto
Durante la implementación Greenfield de `L2_Brain` (NODE_4), se observó que existen 13 especificaciones formales que gobiernan la lógica de negocio pura (Specs 12, 02, 09, 36, 38, 21, 28, 29, 37, 27, 31, 34, 39). Implementar estas 13 especificaciones como módulos o paquetes paralelos independientes corría el riesgo de generar una micro-fragmentación arquitectónica ("Domain Bloat"), dificultando la orquestación cognitiva en la capa de Aplicación.

## Decisión
Se decidió consolidar las 13 especificaciones en 4 **Bounded Contexts** macro dentro de la capa Domain de la Arquitectura Hexagonal:

1. **Context** (Spec 12): Manejo de vectores espaciotemporales y relevancia (6D-Context).
2. **Memory** (Specs 02, 09, 36, 38): Manejo de almacenamiento, nodos cristalizados, y el ledger de sesión.
3. **Fabrication** (Specs 21, 28, 29, 37): Intenciones agénticas, YAML de habilidades y el descubrimiento A2A.
4. **Governance** (Specs 27, 31, 34, 39): El bucle Kaizen, auditoría de impacto y consistencia semántica.

## Consecuencias
- **Positivas:** Cohesión semántica alta. Los adaptadores y casos de uso de la Application Layer interactúan con solo 4 facadas lógicas, reduciendo el acoplamiento.
- **Negativas:** Algunas entidades (como `AgentIntent`) pueden necesitar mapeos cruzados para relacionarse con `MemoryNode`, lo cual deberá resolverse en el `CognitiveOrchestrator` de la capa de Aplicación.
