# Mapa Físico y Ontológico de DUMMIE Engine

## 1. Estratigrafía de Archivos (Physical Layout)
El monorepo sigue una política de **Sustrato Dividido** (Spec 48) para mantener la agilidad del código fuente.

### 1.1. Unidad Principal (Código e Intención)
```text
/home/jorand/Escritorio/DUMMIE Engine
├── layers/
│   ├── l0_overseer/   # Elixir (Arbiter) - Supervisión OTP
│   ├── l1_nervous/    # Go (Nervous) - Reloj de Lamport y NATS Bridge
│   ├── l2_brain/      # Python (Brain) - Razonamiento PydanticAI
│   │   └── .venv -> /media/datasets/dummie/venvs/l2_brain_venv
│   ├── l3_shield/     # Rust (Shield) - Validación PyO3
│   │   └── target -> /media/datasets/dummie/build_artifacts/l3_shield_target
│   └── l4_edge/       # Zig (Edge) - Escáner LST
│       ├── zig-out -> /media/datasets/dummie/build_artifacts/l4_edge_zig/zig-out
│       └── zig-cache -> /media/datasets/dummie/build_artifacts/l4_edge_zig/zig-cache
├── proto/             # Contratos SSoT (Protobuf v2)
│   └── dummie/v2/     # New namespace path
└── .aiwg/memory/      # Cristalización de Memoria (ACIP)
```

### 1.2. Unidad D (Bloatware y Persistencia)
Ubicación: `/media/datasets/dummie/`
- `venvs/`: Entornos virtuales de Python.
- `build_artifacts/`: Binarios de Rust y Zig, cachés de compilación.
- `uv_cache/`, `go_cache/`, `mix_cache/`: Repositorios de dependencias externas.
- `telemetry/`: Bus de datos **Apache Arrow** (Zero-Copy).

---

## 2. Conectividad Lógica (Bus de Datos)

### 2.1. Plano de Control (NATS)
| Tópico | Origen | Destino | Función |
| :--- | :--- | :--- | :--- |
| `core.v2.life.heartbeat` | L1 (Go) | L0 (Elixir) | Monitoreo de supervivencia y latidos causales. |
| `core.v2.orchestration.tasks` | L1 (Go) | L2 (Python) | Despacho de objetivos para razonamiento. |
| `agent.veto.lifecycle` | L0/L3 | L1 (Go) | Señal de apoptosis para procesos comprometidos. |
| `core.v2.mcp.request` | L1 (Sidecar) | L2 (Brain) | Bridge para Model Context Protocol. |

### 2.2. Plano de Datos (Apache Arrow)
- **Shared Memory**: `/media/datasets/dummie/telemetry`
- **Esquema**: `shared/arrow-schemas/reasoning_events.json`
- **Flujo**: L1 (Productor de Telemetría) ↔ L2/L3 (Consumidores de Análisis de Impacto).

---

## 3. Ontología y Semántica (Loci Mapping)
- **LST (Loci Symbol Tree)**: Generado por **L4 (Zig)** al escanear el monorepo.
- **Veto de Seguridad**: Ejecutado por **L3 (Rust)** sobre el JSON de intención de **L2 (Python)** mediante bindings de PyO3 (`shield.so`).
- **Resolución de Ambigüedad**: Registrada en `.aiwg/memory/ambiguities.jsonl` bajo el protocolo ACIP.
