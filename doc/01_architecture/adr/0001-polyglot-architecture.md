---
spec_id: "DE-V2-[ADR-001](0001-polyglot-architecture.md)"
title: "Arquitectura Políglota de 7 Capas"
status: "ACTIVE"
version: "2.1.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L0-03"
    relationship: "DEFINES"
tags: ["architectural_decision", "polyglot_architecture", "industrial_sdd"]
---

# [ADR-001](0001-polyglot-architecture.md): Arquitectura Políglota de 7 Capas

## Abstract
DUMMIE Engine requiere una infraestructura que elimine las "grietas cerebrales" (estocasticidad, amnesia, entropía) inherentes a los modelos LLM convencionales. La velocidad de ejecución es irrelevante si no existe integridad estructural y viabilidad de negocio (ROI).

## 1. Cognitive Context Model (JSON)
```json
{
  "decision": "Implementation of 7-Layer Hybrid Architecture",
  "layers": {
    "L0_Overseer": "Elixir/OTP (Arbitraje/Vida)",
    "L1_Nervous": "Go/NATS (Causalidad/Comunicación)",
    "L2_Brain": "Python (Cognición/Validación)",
    "L3_Shield": "Rust (Seguridad/WASM)",
    "L4_Edge": "Zig/Kùzu (Análisis LST/Ontología)",
    "L5_Muscle": "Mojo (SIMD/Compactación)",
    "L6_Skin": "Tauri/TS (Visualización/PAH)"
  },
  "mechanisms": [
    "Zero-Copy via Apache Arrow",
    "Financial Circuit Breaker",
    "Self-Healing ([Spec 21](../../specs/L2_Brain/21_software_fabrication_engine.md))"
  ],
  "personality_ref": "DE-V2-L0-33",
  "ledger_link": "DE-V2-L2-34"
}
```

---

## 2. Contexto
DUMMIE Engine requiere una infraestructura que elimine las "grietas cerebrales" (estocasticidad, amnesia, entropía) inherentes a los modelos LLM convencionales. La velocidad de ejecución es irrelevante si no existe integridad estructural y viabilidad de negocio (ROI).

---

## 3. Decisión
Se implementa una arquitectura híbrida de 7 capas basada en la **Especialización Radical de Lenguajes** y la comunicación **Zero-Copy via Apache Arrow**.

### 3.1 Estratigrafía de Capas (L0-L6)
- **L0 - Overseer (Elixir/OTP):** El **Árbitro Ejecutivo**. Gestión de vida y resolución de conflictos.
- **L1 - Nervous (Go/NATS):** El **Relojero de Lamport**. Malla de agentes y persistencia distribuida.
- **L2 - Brain (Python/LG):** Cognición estricta validada por **PydanticAI**.
- **L3 - Shield (Rust/WASM):** **Enforcement de los 3 Escudos**. Garantiza la validación de invariantes físicas.
- **L4 - Edge (Zig/Kùzu):** Análisis LST y **Copyright Gavel**. Ingesta ontológica para el Palacio de Loci.
- **L5 - Muscle (Mojo):** **Consolidación de Memoria Jerárquica** y compactación RCU asíncrona.
- **L6 - Skin (Tauri/TS):** Visualización 4D y **Puntero de Autoridad Humana (PAH)**.

---

## 4. Soberanía y Veto Humano (Decision Sovereignty)
Conforme a la directriz del PAH, se establece una frontera física de intervención:
- **Capa de Intencionalidad (Humano):** El usuario opera exclusivamente sobre archivos de especificación (**Markdown, YAML, JSON**).
- **Capa de Ejecución (Agentes):** Los agentes son los únicos autorizados para modificar archivos de infraestructura y lógica imperativa (**Makefile, flake.nix, .go, .rs, .zig, .mojo**).
- **Veto Absoluto:** Ningún humano intervendrá en el código fuente para corregir fallos; toda corrección se realizará mediante el refinamiento de las Specs (SDD).

## 4. Consecuencias
- **Positivas:** Reducción del 95% en deuda técnica, soberanía de hardware local y trazabilidad legal total (PoI).
- **Negativas:** Incremento en la complejidad inicial de despliegue (mitigado por Nix Flakes en [Spec 08](../../specs/L0_Overseer/08_devex_and_deployment_strategy.md)).
