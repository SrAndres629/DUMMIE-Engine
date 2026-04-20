---
status: "PROPOSED" # Enum: PROPOSED, ACCEPTED, SUPERSEDED
date: "YYYY-MM-DD"
deciders: ["sw.arch.core", "Humano PAH"]
supersedes: "" # ID del ADR que este revoca, si aplica
tags: ["arquitectura", "dominio"]
---

# ADR-XXXX: [Título Breve e Imperativo]

## Contexto y Problema
Describe el problema técnico o de negocio que estamos intentando resolver. ¿Cuál es el "dolor" que justifica esta decisión?

## Decisión Arquitectónica
Describe la solución elegida de forma clara. Qué vamos a hacer.

## Consecuencias
Describe qué pasa ahora que tomamos esta decisión.
- **Positivas:** Qué ganamos.
- **Negativas/Restricciones:** Qué perdemos o a qué nos obliga esta decisión.

---

## [MSA] Sibling Components Requeridos
Todo ADR debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** `XXXX-nombre-adr.feature` (Prueba de integración de la consecuencia)
- **Machine Rules:** `XXXX-nombre-adr.rules.json` (Restricción matemática que el validador forzará)
