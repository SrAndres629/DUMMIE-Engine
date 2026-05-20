---
spec_id: "DE-V2-L2-120"
title: "LocalContextCompressor"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
version: "1.0.0"
namespace: "dummie.engine.plan_v1"
---
# Spec 120 - LocalContextCompressor

## Purpose
Provide deterministic local context compression before prompt usage, preserving required context and reducing token load.

## Scope
Covers compression inputs, item-level decisions, secret/private rejection, and compression metrics output.

## Runtime Behavior
Compresses latest context package and prompt frame sections with rules for preserve/compress/drop decisions.

## Inputs
- `.aiwg/reports/context_package_latest.json`
- `.aiwg/reports/prompt_frame_latest.json`

## Outputs
- `.aiwg/reports/local_context_compression_latest.json`

## Safety Rules
- Required items are never dropped.
- Secret/private reasoning patterns are rejected.
- `never_prompt` token role is dropped.

## Missing Artifact Behavior
Missing source artifacts produce warnings or empty-safe behavior; no hard crash for optional inputs.

## Relationship to P10-P17
Builds on context package and prompt frame outputs from prior bundles.

## Current State
Implemented in `layers/l2_brain/flat_brain/local_context_compressor.py` and invoked by CLI command `compress-context`.

## Physical Evidence
- `layers/l2_brain/flat_brain/local_context_compressor.py`
- `.aiwg/reports/local_context_compression_latest.json`
- `layers/l2_brain/tests/test_local_context_compressor.py`

## Contract Invariants
- Reduction ratio in [0,1].
- Required items preserved.
- Output JSON includes preserve/compress/drop counts.

## Tests Expected
`test_local_context_compressor.py` and control-surface integration tests pass.

## Verification
```bash
git diff --check
pytest -q layers/l2_brain/tests/test_local_context_compressor.py
```

## Traceability
Upstream: context package + prompt frame. Downstream: P22 embedding adapter pathways and future prompt runtime tuning.
