---
spec_id: "DE-V2-L0-11"
title: "Estructura de Monorepo Soberano"
status: "ACTIVE"
version: "2.1.0"
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

## 1. Cognitive Context Model (JSON)
```json
{
  "topology": {
    "doc/": "SSoT (Specs, ADRs)",
    "governance/": "Executable Contracts",
    "proto/": "Schema Definitions",
    "layers/": "7-Layer Stack (L0-L6)",
    "pkg/": "Shared Libraries",
    "flake.nix": "Environment Hermeticity"
  },
  "invariants": {
    "hermeticity": "Nix-Enforced",
    "Security Masks": ".aiwg/secrets (Git-encrypted)",
    "Governance": "ADRs in /doc/adr/"
  },
  "personality_ref": "DE-V2-L0-33",
  "ledger_link": "DE-V2-L2-34"
}
```

---

## 2. Topología de Directorios
```text
/
├── doc/                 # SSoT: Specs, ADRs, Walkthroughs
├── governance/          # Contratos Ejecutables e Invariantes
│   ├── rules/           # JSON Schemas de Restricción
│   └── policies/        # Reglas de Arbitraje y Veto
├── proto/               # Definiciones .proto ([Spec 10](../L1_Nervous/10_protobuf_contracts.md))
│   └── arrow/           # Esquemas Apache Arrow (Zero-Copy)
├── layers/              # El Stack Inmortal
│   ├── l0_overseer/     # Elixir/OTP (Arbitraje y Vida)
│   ├── l1_nervous/      # Go (Bus NATS, Redb, Lamport)
│   ├── l2_brain/        # Python (LangGraph, PydanticAI)
│   ├── l3_shield/       # Rust (WASM Sandbox, RCU)
│   ├── l4_edge/         # Zig (LST Scanner, KùzuDB)
│   ├── l5_muscle/       # Mojo (SIMD, Compactación)
│   └── l6_skin/         # Tauri/TS (Visualización 4D)
├── pkg/                 # Librerías Compartidas (Arrow C++ Bindings)
├── scripts/             # Automatización Nix y CI/CD
└── flake.nix            # Definición funcional del entorno hermético
```

---

## 3. Invariantes del Monorepo
- **Hermeticidad:** No se permiten dependencias globales del sistema. Todo binario debe ser provisto por el Flake de Nix.
- **Topological RBAC:** Los agentes solo tienen acceso de escritura a los directorios vinculados a su Capa de expertise.
- **Spec-Driven Consistency:** Cualquier cambio en `/layers` que no tenga una correspondencia en `/doc/specs` o `/governance` será bloqueado por el Auditor.

---

## 4. Gestión de Dependencias (Nix)
Se utiliza **Nix Flakes** para garantizar que los 7 lenguajes compartan el mismo espacio de nombres de librerías nativas (libarrow, libcuda, open-telemetry). Esto garantiza que el "Impuesto Políglota" se mantenga en el 0% al evitar desajustes de versiones en el Data Plane.
- **TaskRunner Regional:** La orquestación se gestiona mediante un `TaskRunner` integrado; el comando `./scripts/start.sh` levanta todo el ecosistema.
- **Nix como Wrapper:** `flake.nix` raíz asegura reproducibilidad total. Cada capa puede tener su propio `flake.nix` derivado.

---

## 5. Formalización de Esquemas Arrow
Bajo la **Ley de Schema-First**, todas las definiciones de buffers de memoria compartida residen en `/proto/arrow/`. Se utilizará prioritariamente el formato **FlatBuffers (.fbs)** para garantizar un enlace binario de latencia cero con Zig (L4) y Rust (L3).

---

## 6. Estado de Implementación
- [x] Convenciones de nombrado de carpetas por capas (L0-L6)
- [x] Ubicación de esquemas Apache Arrow (Zero-Copy)
- [x] Integración de NixOS Flakes para reproducibilidad políglota
- [x] Formalización de la estructura de gobernanza ejecutiva (/governance)
