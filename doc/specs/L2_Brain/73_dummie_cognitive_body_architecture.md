---
spec_id: SPEC-73
title: DUMMIE Cognitive Body Architecture
status: ACTIVE
layer: L2
governance: cognitive_organism
last_verified_on: '2026-05-11'
version: 1.0.0
namespace: dummie.engine.l2_brain
claims:
- id: 73_dummie_cognitive_body_architecture-file-valid
  description: Spec file '73_dummie_cognitive_body_architecture.md' exists, parses
    valid YAML frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/L2_Brain/73_dummie_cognitive_body_architecture.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# SPEC-73: DUMMIE Cognitive Body Architecture

## Purpose
Define the systemic organization of DUMMIE as a multi-model organism, establishing the connection between sensory input, cognitive processing, executive action, and learning persistence.

## Current State
Wired but partially operational. The `CognitiveHookPipeline`, `SensorFirstPolicy`, and `LearningEpisode` are implemented. Meta-Gateway runtime metering is integrated. Authority classification is hardened.

## Physical Evidence
- `layers/l2_brain/cognition/cognitive_hooks.py`
- `layers/l2_brain/metagateway_policy.py`
- `layers/l2_brain/learning_episode.py`
- `layers/l2_brain/daemon/daemon.py`
- `layers/l2_brain/metagateway_runtime_meter.py`
- `layers/l2_brain/outcome_evaluator.py`

## Contract Invariants
- All inputs MUST pass through `CognitiveHookPipeline` before routing.
- `Sensor-First Policy` MUST be evaluated before any direct file read.
- Every saga execution MUST generate a `LearningEpisode` or equivalent outcome metrics.
- Token consumption MUST be measured via `MetaGatewayRuntimeMeter`.

## Anatomical Components

### 2.1 Sensors (L4 Edge / L1 Nervous)
*   **Meta-Gateway:** The primary interface for world discovery.
*   **Sensor-First Policy:** A hard-coded reflex to use discovery tools (semantic search, file cards) before performing heavy context reads.

### 2.2 Cortex (L2 Brain)
*   **CognitiveHookPipeline:** Deterministically classifies intent, authority, and risk.
*   **ModelRouter:** Dynamically assigns tasks to neuron tiers.

### 2.3 Hippocampus (Memory / Persistence)
*   **SessionStore (4D-TES):** The temporal-spatial-causal memory.
*   **Vault:** Long-term memory for "Golden Paths".

### 2.4 Executive System (Daemon)
*   **MissionOrchestrator:** Manages the Mission DAG and checkpoints.
*   **MissionWorkbench:** Physical directory for task artifacts.

## Verification
- Unit tests: `layers/l2_brain/tests/test_authority_classification.py`
- Integration tests: `layers/l2_brain/tests/test_cognitive_loop_e2e.py`
- Efficiency verification: `layers/l2_brain/tests/test_metagateway_hardening.py`

## Traceability
- Replaces: Conceptual roadmap in `.aiwg/reports/systemic_refactor_roadmap.md`
- References: SPEC-71 (Sensor-First Policy)
