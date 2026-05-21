---
spec_id: DE-V2-CROSS-50
title: Daemon Telemetry & Outcome Contracts
status: ACTIVE
layer: L0
last_verified_on: '2026-05-20'
version: 2.0.0
namespace: dummie.engine.cross
---
# Daemon Telemetry & Outcome Contracts

## Purpose
Define the canonical daemon outcome contract so long-running work can report measurable status, evidence, recovery context, and next action without inventing parallel telemetry formats. Includes CognitiveBridge telemetry for L0→L2 delegation.

## Current State
The canonical outcome DTO is implemented in `layers/l2_brain/daemon_outcome.py` and built by `layers/l2_brain/outcome_evaluator.py`. The L2 daemon exposes `_build_outcome()` and `build_daemon_outcome()` through the same evaluator while retaining a degraded fallback if the outcome contract cannot load. `layers/l2_brain/mission_runtime_contract.py` defines the minimal resume-safe mission/phase contract for the next PhaseLedger work.

**v2.0.0 Addition:** CognitiveBridge telemetry for Go→Python delegation via MCP STDIO (Spec 100).

## Physical Evidence
- `layers/l2_brain/daemon_outcome.py`
- `layers/l2_brain/outcome_evaluator.py`
- `layers/l2_brain/daemon/daemon.py`
- `layers/l2_brain/mission_runtime_contract.py`
- `layers/l0_overseer/internal/orchestrator/cognitive_bridge.go`
- `layers/l0_overseer/internal/orchestrator/daemon.go`
- `layers/l2_brain/tests/test_daemon_outcome.py`
- `layers/l2_brain/tests/test_outcome_evaluator.py`
- `layers/l2_brain/tests/test_mission_runtime_contract.py`
- `.aiwg/schemas/mission_runtime_contract.schema.json`
- `.aiwg/state/cognitive_bridge.json`

## Contract Invariants
- **Outcome Status**: Daemon outcomes must use `SUCCESS`, `PARTIAL`, `FAILED`, `BLOCKED`, or `DEGRADED`.
- **Mission Addressability**: Outcomes must carry `session_id`, `mission_id`, `phase_id`, `transaction_id`, and `context_token` fields, even when optional values are empty.
- **Canonical Semantics**: `authority_level` and `intent_type` must be represented as serialized values from the L1/L2 model contract SSoT.
- **Routing Metadata**: Outcomes must include model route metadata with tier, provider, reason, and hook metadata fields.
- **CognitiveBridge Telemetry**: When Go daemon delegates cognition to Python via MCP STDIO, outcomes must include `cognitive_bridge` metadata with `latency_ms`, `target`, `protocol` (JSON-RPC 2.0), and `success` fields.
- **Metacognition State**: Outcomes must report metacognition as `READY`, `DEGRADED`, or `MISSING` and must not persist private chain-of-thought.
- **Sensor-First State**: Outcomes must report policy mode, decision, and reason for sensor-first gating.
- **Efficiency State**: Outcomes must include token/efficiency fields and mark measurements as `estimated` or `runtime`.
- **Evidence and Tests**: Outcomes must carry command/test summaries and public evidence references separate from assumptions.
- **Recovery State**: Outcomes must include `next_action` and `recovery_hint` so a later runtime can resume or inspect blocked work.
- **Mission Runtime Stub**: Mission runtime contracts must reject path traversal in `mission_id` and `phase_id`, generate deterministic resume tokens, and serialize without private reasoning.

## CognitiveBridge Telemetry Contract

When Go daemon (L0) delegates cognition to Python (L2) via MCP STDIO:

```json
{
  "cognitive_bridge": {
    "latency_ms": 660.5,
    "target": "local.brain_ping",
    "protocol": "json-rpc-2.0",
    "success": true,
    "mcp_server": "DUMMIE-Brain-Gateway",
    "transport": "stdio_subprocess"
  }
}
```

**Invariants:**
- Latency must be measured from command send to response receive
- Target must be the full capability name (e.g., `local.brain_ping`, `dummie_discover_capabilities`)
- Protocol is always `json-rpc-2.0` (MCP standard)
- Success reflects whether the MCP tool call returned without error

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/50_daemon_telemetry_contracts.md
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_daemon_outcome.py layers/l2_brain/tests/test_outcome_evaluator.py layers/l2_brain/tests/test_mission_runtime_contract.py
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Outcome Status | `layers/l2_brain/daemon_outcome.py` | `layers/l2_brain/tests/test_daemon_outcome.py` |
| Mission Addressability | `layers/l2_brain/outcome_evaluator.py` | `layers/l2_brain/tests/test_outcome_evaluator.py` |
| Canonical Semantics | `layers/l2_brain/outcome_evaluator.py` | `layers/l1_nervous/tests/test_model_contract_alignment.py` |
| Routing Metadata | `layers/l2_brain/daemon_outcome.py` | `layers/l2_brain/tests/test_daemon_outcome.py` |
| CognitiveBridge Telemetry | `layers/l0_overseer/internal/orchestrator/cognitive_bridge.go` | `.aiwg/state/cognitive_bridge.json` |
| Metacognition State | `layers/l2_brain/outcome_evaluator.py` | `layers/l2_brain/tests/test_outcome_evaluator.py` |
| Sensor-First State | `layers/l2_brain/outcome_evaluator.py` | `layers/l2_brain/tests/test_outcome_evaluator.py` |
| Efficiency State | `layers/l2_brain/outcome_evaluator.py` | `layers/l2_brain/tests/test_outcome_evaluator.py` |
| Evidence and Tests | `layers/l2_brain/daemon_outcome.py` | `layers/l2_brain/tests/test_daemon_outcome.py` |
| Recovery State | `layers/l2_brain/outcome_evaluator.py` | `layers/l2_brain/tests/test_outcome_evaluator.py` |
| Mission Runtime Stub | `layers/l2_brain/mission_runtime_contract.py` | `layers/l2_brain/tests/test_mission_runtime_contract.py` |
