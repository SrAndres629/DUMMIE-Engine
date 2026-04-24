---
spec_id: "DE-V2-L0-11"
title: "Estructura de Monorepo Soberano"
status: "ACTIVE"
version: "2.2.0"
layer: "L0"
namespace: "io.dummie.v2.structure"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L0-00"
    relationship: "IMPLEMENTS"
tags: ["cognitive_core", "monorepo_topology", "industrial_sdd"]
---

# 11. Estructura de Monorepo Soberano

## Abstract
La estructura del repositorio refleja la estratigrafía de 7 capas del Agentic OS. Se implementa un monorepo políglota diseñado para la hermeticidad de dependencias (Nix) y la visibilidad total de la arquitectura por parte de los agentes SFE. El repositorio actúa como el **Palacio de Loci Físico** del sistema.

## 1. Cognitive Context Model (Ref)
Para la topología detallada de directorios, los invariantes de hermeticidad y las reglas de RBAC topológico por capa, consulte el archivo hermano [11_monorepo_structure.rules.json](./11_monorepo_structure.rules.json).

---

## 2. Topología de Directorios
```text
/
├── doc/                 # SSoT: Specs, ADRs, Walkthroughs
│   ├── 00_foundation/   # Manifiestos y Vision
│   ├── 01_architecture/ # ADRs y Diagramas
│   └── specs/           # Especificaciones por Capa (L0-L6)
├── governance/          # Contratos Ejecutables e Invariantes
├── proto/               # Definiciones .proto ([Spec 10](../L1_Nervous/10_protobuf_contracts.md))
├── layers/              # El Stack Inmortal (L0-L6)
├── pkg/                 # Librerías Compartidas
├── .aiwg/               # Hipocampo Agéntico (Memoria y Evolución)
└── flake.nix            # Entorno hermético funcional
```

---

## 3. Invariantes del Monorepo
- **Hermeticidad:** Prohibición de dependencias globales. Todo binario es provisto por Nix.
- **Topological RBAC:** Acceso de escritura restringido por capa de expertise.
- **Spec-Driven Consistency:** Bloqueo de cambios en `/layers` sin correspondencia en `/doc/specs`.

---

## 4. Gestión de Dependencias (Nix)
Se utiliza **Nix Flakes** para garantizar un espacio de nombres unificado de librerías nativas (libarrow, CUDA). Esto asegura que el Data Plane mantenga una latencia mínima al evitar desajustes de versiones entre los 7 lenguajes.

---

## 5. Formalización de Esquemas Arrow
Bajo la **Ley de Schema-First**, todas las definiciones de buffers de memoria compartida residen en `/proto/arrow/`. Se prioriza el formato **FlatBuffers** para enlaces binarios de latencia cero con Zig (L4) y Rust (L3).

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [11_monorepo_structure.feature](./11_monorepo_structure.feature)
- **Machine Rules:** [11_monorepo_structure.rules.json](./11_monorepo_structure.rules.json)
