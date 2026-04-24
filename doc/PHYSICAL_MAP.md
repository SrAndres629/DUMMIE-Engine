# PHYSICAL_MAP.md: Autoridad Topológica del Sistema

## 1. Estructura de Raíz (L0)
- /doc: Documentación técnica y especificaciones.
- /layers: Código fuente hexagonal desacoplado.
- /scripts: Herramientas de automatización industrial.
- /tests: Suites de validación de comportamiento.

## 2. Capas de Ingeniería (L0-L6)
- L0_Overseer: Elixir/NATS Governance.
- L1_Nervous: Python MCP Brain Gateway (Physical Entry).
- L2_Brain: Lógica pura, 4D-TES Memory, Skill Binder.
- L3_Shield: Validación SDD y Seguridad.
- L4_Edge: Tooling discovery y LSP integration.
- L5_Muscle: Remote Execution (Zero-Trust).
- L6_Skin: Observability y OpenTelemetry.

## 3. Invariantes Físicos
- Profundidad máxima de directorios: 3 niveles.
- Los componentes deben residir en la raíz de su capa respectiva.
