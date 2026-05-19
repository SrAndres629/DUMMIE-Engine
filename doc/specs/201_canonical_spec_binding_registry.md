---
spec_id: "DE-V2-L2-201"
title: "Canonical Spec Binding Registry"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-19"
---

## Purpose
Define one canonical registry that binds every spec to its physical implementation artifacts, tests, scripts, and operational data paths.

## Current State
Implemented as a sync script that reads `doc/specs/*.md` and writes a single authoritative binding registry in `.aiwg/spec_registry/spec_bindings.yaml`.

## Physical Evidence
- Sync script: `scripts/spec_registry_sync.py`
- Canonical registry: `.aiwg/spec_registry/spec_bindings.yaml`
- Latest sync report: `.aiwg/reports/spec_registry_sync_latest.json`
- CLI entrypoint: `scripts/dummie-ctl`
- Regression test: `tests/test_spec_registry_sync.py`
- Spec contract: `doc/specs/201_canonical_spec_binding_registry.md`
- Spec scenario: `doc/specs/201_canonical_spec_binding_registry.feature`
- Spec rules: `doc/specs/201_canonical_spec_binding_registry.rules.json`

## Contract Invariants
- The registry schema version is fixed at `dummie.spec_binding_registry.v1`.
- Every spec entry contains: `spec_id`, `spec_path`, `feature_path`, `rules_path`, and `physical_evidence`.
- Runtime, test, docs, script, and data paths are classified deterministically from `Physical Evidence`.
- `--strict` mode must fail when evidence paths are missing.

## Verification
```bash
python3 scripts/spec_registry_sync.py --strict
python3 scripts/validate_specs_docs.py --check doc/specs/201_canonical_spec_binding_registry.md
```

## Traceability
- Pack lineage: `PACK_S1` canonicality hardening.
- Depends on: `doc/specs/108_truth_hierarchy_canonicality_policy.md`.
- Enforces: spec-to-file traceability as first-class runtime artifact.
