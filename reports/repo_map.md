# Repository Map - DUMMIE Engine

## Overview
Este documento mapea la estructura física y lógica del repositorio DUMMIE Engine.

## Layer Topology

### L0 Overseer
- **Ruta**: `layers/l0_overseer`
- **Rol**: Supervisión de bajo nivel.

### L1 Nervous
- **Ruta**: `layers/l1_nervous`
- **Rol**: Transporte, IPC y herramientas MCP.
- **Componentes Críticos**:
  - `tools_impl/`: Implementación de herramientas locales.
  - `sdd_remote_guard.py`: Guardián de herramientas remotas.
- **Contradicciones**:
  - Manipulación de `sys.path` para importar `L2_brain`.

### L2 Brain
- **Ruta**: `layers/l2_brain`
- **Rol**: Lógica de negocio pura, modelos y adaptadores.
- **Componentes Críticos**:
  - `models.py`: Modelos de dominio (`AuthorityLevel`, `MemoryNode4D`).
  - `adapters.py`: `KuzuRepository`.
  - `sdd_governance.py`: Reglas de admisión.

### L3 Shield
- **Ruta**: `layers/l3_shield`
- **Rol**: Seguridad y auditoría topológica.
- **Contradicciones**:
  - `TopologicalAuditor` usa validación simbólica ("cycle" in string) como fallback.

## Contracts
- `AuthorityLevel` (defined in `layers/l2_brain/models.py`).
- `IntentType`.
- `MemoryNode4D`.

## Identified Contradictions
1. **Identity**: Declaraciones de autopoiesis vs ejecución real.
2. **Topology**: Fugas en fronteras de capas (`sys.path`).
3. **Contracts**: Drift en `read_spec`.
