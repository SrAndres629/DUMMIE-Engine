---
spec_id: "DE-V2-L1-44"
title: "Local Reasoning Gateway"
status: "DRAFT"
layer: "L1"
last_verified_on: "2026-04-29"
---
# Local Reasoning Gateway

## Purpose
Definir el contrato para usar un modelo local tipo Gemma como segunda etapa medible sobre embeddings, bus MCP y memoria 4D-TES. El objetivo primario es mejorar precision de retrieval y seleccion de herramientas antes de entregar contexto a agentes de nube.

## Current State
La capacidad se implementa en modo sombra. El modelo local puede reescribir, rankear, seleccionar y compactar contexto, pero la ejecucion sigue gobernada por daemon, SDD guards, L3 policy y contratos MCP existentes.

## Physical Evidence
- `doc/specs/44_local_reasoning_gateway.md`
- `doc/specs/44_local_reasoning_gateway.feature`
- `doc/specs/44_local_reasoning_gateway.rules.json`
- `layers/l2_brain/local_reasoning.py`
- `layers/l1_nervous/tools_impl/local_reasoning.py`
- `scripts/benchmark_local_reasoning.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- La superficie publica debe exponerse por `dummie-brain` y ser consumible mediante `dummie_discover_capabilities`, `dummie_analyze_capability` y `dummie_execute_capability`.
- Los embeddings hacen recall amplio; el modelo local solo puede hacer rerank, seleccion, compactacion y feedback estructurado en v1.
- La ejecucion de herramientas sigue pasando por daemon, SDD guards, runtime guards y L3 policy.
- La persistencia en 4D-TES debe guardar feedback estructurado de alto valor, no volcados completos de contexto.
- La integracion debe funcionar sin modelo local configurado mediante fallback determinista auditable.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/44_local_reasoning_gateway.md
layers/l2_brain/.venv/bin/python -m pytest layers/l2_brain/tests/test_local_reasoning.py layers/l1_nervous/tests/test_local_reasoning_tools.py layers/l2_brain/tests/test_daemon_cognitive_preflight.py -q
python3 scripts/benchmark_local_reasoning.py --mode offline
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Gateway MCP | `layers/l1_nervous/tools_impl/local_reasoning.py` | `dummie_discover_capabilities` + tool tests |
| Reasoning local | `layers/l2_brain/local_reasoning.py` | `test_local_reasoning.py` |
| Daemon preflight | `layers/l2_brain/daemon.py` | `test_daemon_cognitive_preflight.py` |
| Medicion | `scripts/benchmark_local_reasoning.py` | benchmark offline |
