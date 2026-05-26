---
spec_id: 211_gpu_embedding_acceleration
title: GPU-Accelerated Embedding Service
status: ACTIVE
layer: L1
last_verified_on: '2026-05-25'
claims:
- id: 211_gpu_embedding_acceleration-file-valid
  description: Spec file '211_gpu_embedding_acceleration.md' exists, parses valid
    YAML frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/211_gpu_embedding_acceleration.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
## Purpose
Accelerate the EmbeddingService by using GPU (CUDA) for model inference. The current implementation uses fastembed (CPU ONNX runtime) exclusively. With NVIDIA CUDA 13.2 available, switching to sentence-transformers with device='cuda' or configuring fastembed with providers=['CUDAExecutionProvider'] can deliver 10-50x embedding throughput improvement.

## Current State
- `EmbeddingService` at `layers/l1_nervous/embeddings/embedding_service.py` (28 lines)
- Uses `fastembed.TextEmbedding` (ONNX CPU runtime, model "BAAI/bge-small-en-v1.5")
- GPU is idle (0% utilization, 15 MiB VRAM)
- `layers/l2_brain/embedding_mesh/` uses sentence-transformers in a separate venv
- `fastembed` supports `providers=["CUDAExecutionProvider"]` for GPU

## Physical Evidence
- Source: `layers/l1_nervous/embeddings/embedding_service.py`
- Config: `layers/l1_nervous/configs/models_config.json` — fastembed section
- GPU: RTX 3060 6GB VRAM, CUDA 13.2
- Model: BAAI/bge-small-en-v1.5 (384-dim, ONNX)

## Contract Invariants
- **GPU-first**: Embedding inference must attempt CUDA before falling back to CPU
- **Fastembed path**: Use fastembed's CUDAExecutionProvider when onnxruntime-gpu is available
- **Fallback**: If CUDA unavailable, silently fall back to CPU (no crash)
- **Dimension guarantee**: Output dimensions must remain 384 (bge-small-en-v1.5)

## Verification
```bash
# GPU active during embedding
python3 -c "from layers.l1_nervous.embeddings.embedding_service import EmbeddingService; e=EmbeddingService(); e.embed(['test']); print('OK')"
nvidia-smi | grep -c python3  # Must show >0
```

## Traceability
- Maps to: FDA-002 (GPU-first compute)
- Source changes: `layers/l1_nervous/embeddings/embedding_service.py`
