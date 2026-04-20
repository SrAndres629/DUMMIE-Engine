---
spec_id: "DE-V2-[ADR-003](0003-agentic-communication-fabrication.md)"
title: "Comunicación Agéntica y Fabricación (SFE)"
status: "ACTIVE"
version: "2.1.0"
layer: "L2"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L2-21"
    relationship: "DEFINES"
tags: ["architectural_decision", "agentic_communication", "software_fabrication"]
---

# [ADR-003](0003-agentic-communication-fabrication.md): Comunicación Agéntica y Fabricación (SFE)

## Abstract
La construcción de software mediante agentes de IA suele fracasar debido a la **Entropía Arquitectónica** y al acoplamiento semántico. El sistema se define como una **Software Fabrication Engine (SFE)** que impone el rigor de un Arquitecto de Sistemas experto sobre la generación de código.

## 1. Cognitive Context Model (JSON)
```json
{
  "protocol": "Architecture-First (AF)",
  "consensus_triangle": [
    "Domain Proposal (Pure Logic)",
    "Port Contract (Protobuf)",
    "Sign-off (Shield Validation)"
  ],
  "arbitration_algorithm": {
    "formula": "Score = (ROI * 0.6) - (Complexity_Risk * 0.4)",
    "veto_override": "S-Shield (Integrity)",
    "escalation": "PAH_OVERRIDE (Human)"
  },
  "enforcement": [
    "Apoptosis Preventiva",
    "Trazabilidad Forense"
  ],
  "personality_ref": "DE-V2-L0-33",
  "ledger_link": "DE-V2-L2-34"
}
```

---

## 2. Contexto
La construcción de software mediante agentes de IA suele fracasar debido a la **Entropía Arquitectónica** y al acoplamiento semántico. El sistema se define como una **Software Fabrication Engine (SFE)** que impone el rigor de un Arquitecto de Sistemas experto sobre la generación de código.

---

## 3. Decisión: Protocolo Architecture-First (AF)
Se establece que la comunicación inter-agente es un **Flujo de Ingeniería de Software (SEF)** obligatorio. Ningún agente puede implementar código sin completar el Triángulo de Consenso:
1. **Domain Proposal:** Definición de lógica pura sin dependencias externas.
2. **Port Contract:** Definición estricta de interfaces en Protobuf ([Spec 10](../../specs/L1_Nervous/10_protobuf_contracts.md)).
3. **Sign-off:** El Auditor (L2/L0) valida la propuesta contra los **Shields Arquitectónicos**.

### 3.1 Soberanía de Especificación (SDD)
El desarrollo es 100% dirigido por documentación (**Spec-Driven Development**). El código es un subproducto efímero derivado de la documentación; la documentación es la "Única Fuente de Verdad" (SSOT) y es el único punto de interacción humana permitido.

---

## 4. Algoritmo de Arbitraje Ejecutivo (L0)
Para evitar la parálisis por análisis ante la divergencia entre agentes, el Árbitro (L0 Elixir) aplica el **Protocolo de Decisión Ponderada**:

$$Score = (ROI \cdot 0.6) - (Complexity\_Risk \cdot 0.4)$$

- **Veto de Integridad (S-Shield):** Si el Shield de Rust (L3) detecta una violación de las reglas SDD ([Spec 22](../../specs/L3_Shield/22_sdd_executable_contracts.md)), el `Score` se anula a 0 automáticamente. La integridad prevalece sobre el beneficio económico.
- **Factor de Latencia:** Las propuestas que excedan el budget de latencia de red sufren una penalización de -0.1 en el score final.
- **Tie-Breaker Final:** En caso de incertidumbre crítica, el sistema escala al **PAH_OVERRIDE (Puntero de Autoridad Humana)**.

---

## 5. Consecuencias y Sanciones
- **Apoptosis Preventiva:** Si un agente insiste en una propuesta vetada por el S-Shield tras 3 iteraciones, L0 dispara el protocolo de muerte cerebral.
- **Trazabilidad Forense:** Toda decisión del Árbitro se persiste en el Event Store con el hash de la regla SDD que motivó el veto.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** `0003-agentic-communication-fabrication.feature`
- **Machine Rules:** `0003-agentic-communication-fabrication.rules.json`
