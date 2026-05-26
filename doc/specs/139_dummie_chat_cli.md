---
spec_id: 139_dummie_chat_cli
title: 139 Dummie Chat Cli
status: ACTIVE
canonicality: canonical
artifact_type: spec
plan: DUMMIE PLAN V1
layer: l2_brain
created_by: operationalization_pack_1
last_verified_on: '2026-05-16'
claims:
- id: 139_dummie_chat_cli-file-valid
  description: Spec file '139_dummie_chat_cli.md' exists, parses valid YAML frontmatter,
    and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/139_dummie_chat_cli.md').read().split('---')[1]); assert d, 'empty
    frontmatter'"
  severity: critical
---
# Spec 139: DUMMIE Chat CLI

## Purpose
Provide a native, local chat interface for system monitoring and strategic decision-making.

## Scope
- Responds to status, technical debt, and planning queries.
- Interfaces with `RepoIntelligenceQuery` and `ContextEnforcementGate`.
- Operates locally without external LLM dependencies.

## Runtime Behavior
1. Receive user query via CLI.
2. Determine intent (status, debt, query, etc.).
3. Enforce context gate.
4. Execute relevant intelligence query or report load.
5. Return structured `DummieChatResponse`.

## Safety Rules
- Must not execute workspace mutations without authorization.
- Must not call cloud LLMs.


## Current State
- TBD

## Physical Evidence
- TBD

## Contract Invariants
- TBD

## Verification
- TBD

## Traceability
- TBD
