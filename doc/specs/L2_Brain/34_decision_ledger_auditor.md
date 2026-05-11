---
spec_id: "DE-V2-L2-34"
title: "Ledger de Decisiones e Interfaz de Alerta"
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

# 34. Ledger de Decisiones e Interfaz de Alerta

## Abstract
El Ledger de Decisiones es el registro inmutable de la soberanía cognitiva del sistema. Este componente actúa como el **Testigo Causal**, almacenando cada resolución tomada por el Swarm, desde la aprobación de una arquitectura hasta la mitigación de una vulnerabilidad, garantizando una trazabilidad total y una interfaz de alerta en tiempo real para el PAH.

## 1. Cognitive Context Model (Ref)
Para la ruta del ledger, los campos obligatorios de resolución (Tick, Witness Hash) y los invariantes de inmutabilidad del registro, consulte el archivo hermano [34_decision_ledger_auditor.rules.json](./34_decision_ledger_auditor.rules.json).

---

## 2. El Testigo Causal (Ledger)
Cada entrada en el ledger representa una cristalización de conocimiento:
- **Tick:** Tiempo lógico de Lamport asociado al evento.
- **Resolution:** Declaración formal de la decisión tomada.
- **Witness Hash:** Firma criptográfica o hash de estado que garantiza la integridad de la decisión.

---

## 3. Interfaz de Alerta y Notificación
El Auditor L2 vigila el ledger y emite alertas a través de NATS ante eventos críticos:
- **Architecture Shift:** Cambios en los ADRs o la topología.
- **Constraint Violation:** Decisiones que contradicen los invariantes del Shield L3.
- **Human Oversight Required:** Decisiones con alto radio de explosión que requieren el oráculo del PAH.

## 4. Formal Contract Boundary (Audit Trace)
Para que las decisiones no sean simples promesas en texto, el Ledger implementa el siguiente contrato físico Protobuf (v3) que actúa como *Single Source of Truth* (SSoT):

```protobuf
// ==========================================
// DECISION LEDGER RECORD
// ==========================================
message DecisionRecord {
    string decision_id = 1;
    string rationale = 2;
    string impact_blast_radius = 3;
    
    // Origen de la decisión
    SixDimensionalContext context = 4; 
    // El nodo 4D-TES sobre el que recae el fallo
    string target_causal_hash = 5;     
    
    // Firma criptográfica del auditor (Sentinel/PAH)
    string witness_hash = 6;           
}
```

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [34_decision_ledger_auditor.feature](./34_decision_ledger_auditor.feature)
- **Machine Rules:** [34_decision_ledger_auditor.rules.json](./34_decision_ledger_auditor.rules.json)
