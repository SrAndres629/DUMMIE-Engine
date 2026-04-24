# DUMMIE Engine

DUMMIE Engine es un sistema experimental de orquestación agéntica multi-capa con foco en trazabilidad, contratos y ejecución asistida por MCP.

## Estado actual (2026-04-24)
- Monorepo activo con capas `layers/l0_overseer` a `layers/l6_skin`.
- Gateway MCP operativo en Python: `layers/l1_nervous/mcp_server.py`.
- Núcleo cognitivo actual en Python plano (bridge): `layers/l2_brain/*.py`.
- Validadores de L3/L4/L5 presentes, mayormente en estado base o stub.
- Suite de pruebas de `L2` alineada al layout físico actual (`13 passed` en `layers/l2_brain/tests`).
- Principal deuda vigente: estandarización operativa de `doc/specs/*.md` (trazabilidad y contenido no genérico).

## Arquitectura física resumida
- `L0`: base Elixir/OTP (`layers/l0_overseer`).
- `L1`: gateway MCP + puente de conectividad (`layers/l1_nervous`).
- `L2`: orquestación cognitiva y modelos (`layers/l2_brain`).
- `L3`: auditores estructural/económico/legal (`layers/l3_shield`).
- `L4`: descubrimiento de herramientas y observación (`layers/l4_edge`).
- `L5`: ejecución y sandbox adapters (`layers/l5_muscle`).
- `L6`: superficie frontend/dev server (`layers/l6_skin`).

## Verificación rápida
```bash
# Estado git
git status --short

# Import smoke (L1/L2/L3/L4/L5)
PYTHONPATH="layers/l2_brain:layers/l1_nervous:layers/l3_shield:layers/l4_edge:layers/l5_muscle" \
  layers/l2_brain/.venv/bin/python -c "import models, orchestrator, bootstrap, tools, resources"

# Tests L2 (alineados al estado actual)
cd layers/l2_brain && uv run pytest -q tests

# Validación de documentación/specs
python3 scripts/validate_specs_docs.py
```

## Navegación documental
- Índice maestro: `doc/CORE_SPEC.md`
- Mapa físico y brechas: `doc/PHYSICAL_MAP.md`
- Contrato documental: `doc/specs/43_documentation_and_artifact_standards.md`
- Base operativa agéntica: `doc/agentic/`
