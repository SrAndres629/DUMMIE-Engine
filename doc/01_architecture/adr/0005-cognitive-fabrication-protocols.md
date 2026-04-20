---
spec_id: "DE-V2-[ADR-005](0005-cognitive-fabrication-protocols.md)"
title: "Estándares de Fabricación Cognitiva y Protocolos de Interacción"
status: "ACTIVE"
version: "1.0.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-[ADR-002](0002-ambiguity-resolutions.md)"
    relationship: "EXTENDS"
  - id: "DE-V2-[ADR-003](0003-agentic-communication-fabrication.md)"
    relationship: "REINFORCES"
tags: ["architectural_decision", "cognitive_standards", "industrial_sdd"]
---

# [ADR-005](0005-cognitive-fabrication-protocols.md): Estándares de Fabricación Cognitiva

## Abstract
La transición de una herramienta de desarrollo a una **Software Fabrication Engine (SFE)** industrial requiere la imposición de estándares de ingeniería de software (SDD, DDD, TDD, BDD) no solo sobre el código, sino sobre la documentación misma. Ninguna actualización puede carecer de arquitectura previa, y toda ambigüedad debe resolverse proactivamente consultando al usuario para eliminar cualquier indeterminación.

## 1. Cognitive Context Model (JSON)
```json
{
  "documentation_standards": {
    "SDD": "Spec-Driven Development (Specs are Code)",
    "DDD": "Domain-Driven Design (Bounded Contexts)",
    "TDD": "Test-Driven Development (Sentinel Verification)",
    "BDD": "Behavior-Driven Development (Gherkin Flows)"
  },
  "interaction_protocol": {
    "ambiguity_handling": "Stop and Ask User (PAH)",
    "indeterminacy_elimination": "Proactive questioning",
    "system_goal": "Absolute Determinism"
  },
  "agent_roles": {
    "researchers_architects": "Design, Specification, Ambiguity Discovery",
    "fullstack_engineers": "Implementation, Validation, Execution"
  },
  "personality_ref": "DE-V2-L0-33",
  "ledger_link": "DE-V2-L2-34"
}
```

---

## 2. Estándares de Documentación Industrial
Para operar como una base cognitiva soberana, toda documentación debe ser estructurada profesionalmente para el consumo de agentes de IA:

### 2.1 Métrica SDD-DDD-TDD-BDD
- **SDD (Specs as Code):** La documentación es el código fuente real. Una falla en la spec es una falla en el sistema.
- **DDD (Domain-First):** La arquitectura debe respetar los contextos delimitados. No se permiten "fugas semánticas" entre capas.
- **TDD/BDD:** Cada especificación debe incluir criterios de aceptación verificables (Jidoka) y ejemplos de comportamiento claro.

### 2.2 Prohibición de Caos Estructural
Se prohíbe terminantemente la creación o actualización de documentación que no responda a una arquitectura o arquitectura clave predefinida. No existe "prosa libre" en DUMMIE Engine; solo contratos.

---

## 3. Protocolo de Ambigüedad Cero
El sistema busca el **Determinismo Absoluto**. Ante cualquier indeterminación lógica:
1. **Detección:** El agente identifica el `Ambiguity_Ticket`.
2. **Amplificación Intelectual:** En lugar de asumir una solución, el agente debe investigar cuál es la mejor forma de hacerlo y plantear preguntas al usuario (PAH).
3. **Refinamiento Mental:** Las preguntas deben estar diseñadas para ayudar al usuario a pensar mejor y eliminar ambigüedades en la idea del sistema.
4. **Validación:** No se procede al desarrollo hasta que la indeterminación sea eliminada por la respuesta del usuario.

---

## 4. Diferenciación de Roles Cognitivos
El Swarm se organiza en dos grupos operativos:

### 4.1 Investigadores y Arquitectos (Cognitive Core)
- **Función:** Analizar problemas complejos, diseñar arquitectura y formalizar especificaciones.
- **Protocolo:** Su output es siempre una `Spec` validada o un `ADR`. Son los guardianes de la intención.

### 4.2 Ingenieros Fullstack (Execution Core)
- **Función:** Implementar código basado estrictamente en la documentación aprobada.
- **Protocolo:** Tienen prohibido modificar la lógica de negocio sin una actualización previa de la Spec por parte de un Arquitecto.

---

## 5. Consecuencias
- **Determinismo:** Eliminación de alucinaciones arquitectónicas.
- **Colaboración:** El usuario y los agentes co-architectorizan el sistema mediante un diálogo socrático de alta precisión.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** `0005-cognitive-fabrication-protocols.feature`
- **Machine Rules:** `0005-cognitive-fabrication-protocols.rules.json`
