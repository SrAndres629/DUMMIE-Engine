---
spec_id: "DE-V2-[ADR-002](0002-ambiguity-resolutions.md)"
title: "Resolución de Ambigüedades y Gobernanza"
status: "ACTIVE"
version: "2.1.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "EXECUTIVE_ARBITER"
dependencies:
  - id: "DE-V2-L0-14"
    relationship: "IMPLEMENTS"
  - id: "DE-V2-[ADR-005](0005-cognitive-fabrication-protocols.md)"
    relationship: "REQUIRES"
tags: ["architectural_decision", "ambiguity_resolution", "industrial_sdd"]
---

# [ADR-002](0002-ambiguity-resolutions.md): Resolución de Ambigüedades y Gobernanza

## Abstract
La negociación infinita entre agentes expertos requiere un mecanismo de arbitraje vinculante. Esta decisión establece al Árbitro de Elixir (L0) como la autoridad suprema para la resolución de conflictos, limitada por el budget cognitivo y el ROI proyectado.

## 1. Cognitive Context Model (JSON)
```json
{
  "arbitration": {
    "arbiter": "L0 Elixir",
    "iteration_limit": 3,
    "escalation": "PAH (Human Pointer)",
    "protocol": "Ask-User-First ([ADR-005](0005-cognitive-fabrication-protocols.md))"
  },
  "safety_macros": {
    "S_Shield": "Structural/Causal",
    "E_Shield": "Economic/ROI",
    "L_Shield": "Legal/Copyright"
  },
  "bus_segmentation": {
    "control_plane": "NATS (Signal/Veto)",
    "data_plane": "Apache Arrow (Zero-Copy)"
  },
  "persistence": {
    "event_store": "Redb",
    "ontology": "KùzuDB"
  },
  "personality_ref": "DE-V2-L0-33",
  "ledger_link": "DE-V2-L2-34"
}
```

---

## 2. El Árbitro de Elixir (L0) y el Protocolo de Ambigüedad
**Conflicto:** La negociación infinita entre agentes expertos o la toma de decisiones basada en suposiciones.

**Decisión:** Se implementa un protocolo de arbitraje en cascada:
1. **Detección y Escalamiento:** Ante cualquier indeterminación lógica o ambigüedad, el agente debe detener la ejecución y escalar la duda al **Puntero de Autoridad Humana (PAH)** como prioridad absoluta.
2. **Amplificación Intelectual:** Los agentes no solo preguntan; investigan las mejores opciones y presentan preguntas estratégicas (Socratic Ingestion) que ayuden al usuario a refinar su visión y eliminar la indeterminación (Ver [ADR-005](0005-cognitive-fabrication-protocols.md)).
3. **Arbitraje Ejecutivo:** El Árbitro (L0 Elixir) solo interviene en conflictos técnicos de implementación internos. La negociación se limita a **3 iteraciones** antes de una decisión vinculante basada en el ROI.

---

## 3. Los 3 Escudos Activos (Macros)
**Conflicto:** La fragmentación de 38 riesgos individuales satura el contexto de los agentes.
**Decisión:** Consolidación en 3 Macros de Seguridad supervisados por L3/L0:
- **S-Shield (Structural):** Integridad LST y Causalidad de Lamport.
- **E-Shield (Economic):** Financial Circuit Breaker y ROI Optimizer.
- **L-Shield (Legal):** PoI Tracker y Copyright Gavel.

---

## 4. Bus Dual: NATS vs. Arrow
**Decisión:** Segmentación absoluta entre señalización y datos:
- **Control Plane (NATS):** Señalización, latidos de vida y **Vetos de Seguridad**.
- **Data Plane (Apache Arrow):** Intercambio de LSTs y contextos mediante memoria compartida (**Zero-Copy**).

---

## 5. Persistencia Causal
**Decisión:** Uso de **Redb** como Event Store inmutable (indexado por Lamport Ticks) y **KùzuDB** como proyección ontológica para GraphRAG.

---

## 6. Consecuencias
- **Determinismo:** Garantía de progreso ante divergencia cognitiva.
- **Soberanía:** Blindaje contra el agotamiento de recursos (Tokens/RAM).

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** `0002-ambiguity-resolutions.feature`
- **Machine Rules:** `0002-ambiguity-resolutions.rules.json`
