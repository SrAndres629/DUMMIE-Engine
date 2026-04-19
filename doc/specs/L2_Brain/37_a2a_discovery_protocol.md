---
spec_id: "DE-V2-L2-37"
title: "Protocolo de Descubrimiento Agent-to-Agent (A2A)"
status: "ACTIVE"
version: "1.0.0"
layer: "L2"
namespace: "io.dummie.v2.brain"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L2-02"
    relationship: "REQUIRES"
tags: ["cognitive_core", "brain_logic", "industrial_sdd"]
---

# Protocolo de Descubrimiento Agent-to-Agent (A2A)

## Abstract
Esta especificación define un componente crítico del plano cognitivo (Brain L2). Se centra en la orquestación de la inteligencia agéntica, la gestión de la consistencia semántica y el aprendizaje continuo mediante ciclos Kaizen.

## 1. Alcance Operativo
El componente opera dentro del Bounded Context del Cerebro, interactuando con la Memoria 4D-TES y el Escudo L3 para garantizar que todo razonamiento sea coherente con la topología global del sistema.

---

## [MSA] Sibling Components
- **Executable Contract**: 37_a2a_discovery_protocol.feature
- **Machine Rules**: 37_a2a_discovery_protocol.rules.json
