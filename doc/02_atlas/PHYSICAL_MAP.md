---
spec_id: "DE-V2-MAP-01"
title: "Mapa Físico y Ontológico de DUMMIE Engine"
status: "ACTIVE"
version: "2.1.0"
layer: "L0"
namespace: "io.dummie.v2.atlas"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L0-48"
    relationship: "IMPLEMENTS"
tags: ["atlas", "physical_map", "ontology", "industrial_sdd"]
---

# Mapa Físico y Ontológico de DUMMIE Engine

## Abstract
Este documento define la topología física del monorepo y su mapeo ontológico hacia la arquitectura de 7 capas. Establece la política de **Sustrato Dividido** para la segregación de activos (código vs datos masivos) y detalla los canales de conectividad lógica para el plano de control y el plano de datos.

## 1. Cognitive Context Model (Ref)
Para los invariantes de estructura de directorios, los esquemas de telemetría Arrow y las reglas de conectividad NATS, consulte el archivo hermano [PHYSICAL_MAP.rules.json](./PHYSICAL_MAP.rules.json).

---

## 2. Estratigrafía de Archivos (Physical Layout)
El monorepo sigue una política de **Sustrato Dividido** (Spec 48) para mantener la agilidad del código fuente.

### 2.1. Unidad Principal (Código e Intención)
```text
/home/jorand/Escritorio/DUMMIE Engine
├── layers/
│   ├── l0_overseer/   # Elixir (Arbiter) - Supervisión OTP
│   ├── l1_nervous/    # Go (Nervous) - Reloj de Lamport y NATS Bridge
│   ├── l2_brain/      # Python (Brain) - Razonamiento PydanticAI
│   ├── l3_shield/     # Rust (Shield) - Validación PyO3
│   └── l4_edge/       # Zig (Edge) - Escáner LST
├── proto/             # Contratos SSoT (Protobuf v2)
│   └── dummie/v2/     # New namespace path
├── .aiwg/             # Hipocampo Agéntico (Evolución y Autoconciencia)
│   ├── identity.json  # Super-Ego y rasgos de personalidad.
│   ├── evolution.jsonl # Registro del gap Teoría vs Física.
│   └── memory/        # Cristalización de Memoria (ACIP)
└── .git/              # Control de versiones.
```

### 2.2. Unidad D (Bloatware y Persistencia)
Ubicación: `/media/datasets/dummie/`
- `venvs/`: Entornos virtuales de Python.
- `build_artifacts/`: Binarios de Rust y Zig.
- `uv_cache/`, `go_cache/`, `mix_cache/`: Repositorios de dependencias externas.
- `telemetry/`: Bus de datos **Apache Arrow** (Zero-Copy).

---

## 3. Conectividad Lógica (Bus de Datos)

### 3.1. Plano de Control (NATS)
| Tópico | Origen | Destino | Función |
| :--- | :--- | :--- | :--- |
| `core.v2.life.heartbeat` | L1 (Go) | L0 (Elixir) | Monitoreo de supervivencia. |
| `core.v2.orchestration.tasks` | L1 (Go) | L2 (Python) | Despacho de objetivos. |
| `agent.veto.lifecycle` | L0/L3 | L1 (Go) | Señal de apoptosis. |

### 3.2. Plano de Datos (Apache Arrow)
- **Shared Memory**: `/media/datasets/dummie/telemetry`
- **Flujo**: L1 (Productor) ↔ L2/L3 (Consumidores).

---

## 4. Ontología y Semántica (Loci Mapping)
- **LST (Loci Symbol Tree)**: Generado por **L4 (Zig)** al escanear el monorepo.
- **Veto de Seguridad**: Ejecutado por **L3 (Rust)** sobre la intención de **L2 (Python)**.
- **Resolución de Ambigüedad**: Registrada en `.aiwg/memory/ambiguities.jsonl` bajo el protocolo ACIP.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [PHYSICAL_MAP.feature](./PHYSICAL_MAP.feature)
- **Machine Rules:** [PHYSICAL_MAP.rules.json](./PHYSICAL_MAP.rules.json)
