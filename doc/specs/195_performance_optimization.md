---
spec_id: 195_performance_optimization
title: Performance Optimization - Memory, Process Consolidation, Aggressive Pruning
status: ACTIVE
layer: L2
last_verified_on: '2026-05-21'
version: 1.0.0
claims:
- id: 195_performance_optimization-file-valid
  description: Spec file '195_performance_optimization.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/195_performance_optimization.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
# Spec 195: Performance Optimization

## Purpose
Optimize DUMMIE Engine for laptop deployment (15GB RAM, RTX 3060 6GB) without sacrificing intelligence.

## Targets
| Metric | Before | Target | Method |
|---|---|---|---|
| Daemon RAM | 3.1GB | < 2GB | Lazy loading, aggressive pruning |
| MCP processes | 4 | 2 | Consolidation |
| Swarm daemons | 6 | 1 | Combined role daemon |
| Context tokens | 4096 | 1024-4096 | Dynamic budgeting |
| Embedding cache | None | 500 entries | LRU with TTL |
| RIR drop threshold | 0.15 | 0.20 | More aggressive |
| RIR compress threshold | 0.35 | 0.45 | More aggressive |
| Preserve max chars | 1024 | 512 | Smaller context |
| Compress max chars | 120 | 80 | Smaller summaries |

## Canonical Implementation
- Lazy loader: `layers/l2_brain/metacognition/lazy_loader.py`
- Optimized pruning: `layers/l2_brain/metacognition/context_pruning_optimized.py`
- Embedding cache: `layers/l2_brain/embedding_mesh/vector_cache.py`
- Optimized daemon: `layers/l2_brain/daemon/daemon_service_optimized.py`
- Optimized swarm: `scripts/swarm_daemon_optimized.py`
- Performance monitor: `layers/l2_brain/metacognition/performance_monitor.py`
- Tests: `layers/l2_brain/tests/test_optimized_pruning.py`, `layers/l2_brain/tests/test_embedding_cache.py`

## Dynamic Token Budgeting
- Simple queries (hello, status, help): 1024 tokens
- Normal queries: 2048 tokens
- Complex queries (architect, design, migration): 4096 tokens
- Override via `DUMMIE_MAX_CONTEXT_TOKENS` env var

## Verification Commands
```bash
uv run python -m pytest layers/l2_brain/tests/test_optimized_pruning.py -q --no-header --tb=short
uv run python -m pytest layers/l2_brain/tests/test_embedding_cache.py -q --no-header --tb=short
```
