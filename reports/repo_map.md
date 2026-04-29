# Mapa del Repositorio: DUMMIE Engine

## Capas Arquitectónicas (L0 a L6)

### [L0 Overseer](file:///home/jorand/Escritorio/DUMMIE%20Engine/layers/l0_overseer) (Go / Elixir)
- **Rol:** Supervisión de procesos, tolerancia a fallos y ciclo de vida.
- **Componentes Clave:** Daemon principal, scripts de control.

### [L1 Nervous](file:///home/jorand/Escritorio/DUMMIE%20Engine/layers/l1_nervous) (Go / Python)
- **Rol:** Transporte de datos e IPC (Zero-Copy vía Apache Arrow).
- **Componentes Clave:** `memory_ipc.py`, `mcp_proxy.py`.

### [L2 Brain](file:///home/jorand/Escritorio/DUMMIE%20Engine/layers/l2_brain) (Python)
- **Rol:** Modelado cognitivo y almacenamiento en grafo.
- **Componentes Clave:** `models.py`, `adapters.py`, `embedding_provider.py`.

### [L3 Shield](file:///home/jorand/Escritorio/DUMMIE%20Engine/layers/l3_shield) (Rust / Python)
- **Rol:** Validación de seguridad topológica y cumplimiento.
- **Componentes Clave:** `topological_auditor.py`, `Cargo.toml` (Rust Core).

### [L4 Edge](file:///home/jorand/Escritorio/DUMMIE%20Engine/layers/l4_edge) (Zig / Python)
- **Rol:** Escaneo de bajo nivel y descubrimiento de herramientas.
- **Componentes Clave:** `lst_scanner.zig`, `tool_discovery.py`.

### [L5 Muscle](file:///home/jorand/Escritorio/DUMMIE%20Engine/layers/l5_muscle) (Mojo / Python)
- **Rol:** Operaciones matemáticas rápidas y compactación de memoria.
- **Componentes Clave:** `math_ops.mojo`, `compactor.py`.

### [L6 Skin](file:///home/jorand/Escritorio/DUMMIE%20Engine/layers/l6_skin) (Web)
- **Rol:** Interfaz gráfica y observabilidad básica.
- **Componentes Clave:** `index.html`.

## Dependencias Críticas e Imports Cruzados
- **Advertencia:** Fugas de abstracción detectadas en `L1_nervous` mediante manipulaciones de `sys.path` para importar desde `L2_brain`.
