---
spec_id: "151_semantic_ontology_mapper"
title: "151 Semantic Ontology Mapper"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_5"
last_verified_on: "2026-05-16"
---

# Spec 151: Semantic Ontology Mapper

## Purpose
Graph-based classification of intent concepts.

## Scope
- Generates nodes and edges representing semantic relations between system classes.

## Current State
- Operational. Reconciled with Pack 5.2.1 closure requirements.

## Physical Evidence
- `layers/l2_brain/model_mesh/semantic_ontology_mapper.py`
- `.aiwg/reports/semantic_ontology_map_latest.json`
- `.aiwg/schemas/semantic_ontology_map.schema.json`

## Contract Invariants
- decision must be PASS or PASS_WITH_WARNINGS
- must generate graph structure

## Verification
```bash
python3 layers/l2_brain/model_mesh/semantic_ontology_mapper.py
pytest layers/l2_brain/tests/test_semantic_ontology_mapper.py
```

## Traceability
- POST_PLAN_V1_OPERATIONALIZATION_PACK_5 Module 2
