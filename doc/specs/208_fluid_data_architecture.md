---
spec_id: 208_fluid_data_architecture
title: Fluid Data Architecture — Dummie Engine Pipeline Optimization
status: ACTIVE
layer: cross-layer
last_verified_on: '2026-05-25'
claims:
- id: 208_fluid_data_architecture-file-valid
  description: Spec file '208_fluid_data_architecture.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/208_fluid_data_architecture.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
## Purpose
Define and implement the Fluid Data Architecture for the DUMMIE Engine: a set of optimizations that route computational data through the fastest available paths — GPU for LLM inference and embeddings, tmpfs for ephemeral I/O, kernel-level scheduling for process prioritization — while maintaining the existing spec-driven contract system.

This is the master design document. Each optimization has its own executable spec.

## Current State
The DUMMIE Engine runs exclusively on CPU despite having a NVIDIA RTX 3060 GPU (6GB VRAM, Ampere) permanently idle in P8 state. All LLM inference (Ollama disabled), embeddings (fastembed CPU-only), and ephemeral I/O (.aiwg/reports, .aiwg/runtime on NTFS) are suboptimal. The kernel (OEM 6.17.0) supports sched_ext, PSI, intel_pstate, and KSM — all configured but sched_ext unused.

## Physical Evidence
- GPU idle P8, 0% utilization, 15 MiB VRAM used out of 6 GiB
- Ollama service inactive (disabled, port 11434 not listening)
- .aiwg/runtime on NTFS (fuseblk) via /media/datasets/
- .aiwg/reports 98 MB on disk, JSON I/O going through FUSE layer
- Embeddings via fastembed (CPU ONNX), sentence-transformers venv exists but inactive
- Kernel CONFIG_SCHED_CLASS_EXT=y — no scheduler loaded

## Contract Invariants
- **GPU-first inference**: Enable Ollama on GPU; local LLM inference must use CUDA when available
- **GPU-first embeddings**: Embedding service must use GPU (CUDA) when available, CPU fallback only when GPU absent
- **Ephemeral I/O in RAM**: .aiwg/runtime, .aiwg/reports, .aiwg/sockets must be in tmpfs, not persistent storage
- **Scheduler isolation**: Each layer (L0-L6) should be schedulable under different sched_ext policies if loaded
- **No code duplication**: Changes must reference source files, not duplicate them
- **Spec wiring**: Each subspec must be registered in spec_graph.json

## Verification
```bash
nvidia-smi -q -d COMPUTE | grep "Compute Mode"
ollama list 2>/dev/null && echo "Ollama GPU active" || echo "Ollama not running"
mount | grep tmpfs-dummie
cat /sys/kernel/sched_ext/ops 2>/dev/null || echo "No sched_ext scheduler"
```

## Traceability
- Maps to: Fluid Data Architecture program
- Contract Schema: `.aiwg/schemas/208_fluid_data_architecture.rules.json`
- Subspecs: 209 (Ollama GPU), 210 (tmpfs), 211 (GPU Embeddings), 212 (Shared Memory), 213 (sched_ext)
