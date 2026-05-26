---
spec_id: 209_ollama_gpu_acceleration
title: Ollama GPU Acceleration
status: ACTIVE
layer: L1
last_verified_on: '2026-05-25'
claims:
- id: 209_ollama_gpu_acceleration-file-valid
  description: Spec file '209_ollama_gpu_acceleration.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/209_ollama_gpu_acceleration.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
## Purpose
Enable Ollama with GPU acceleration for local LLM inference. The NVIDIA RTX 3060 (6GB VRAM, Ampere) is permanently idle (P8, 0% utilization, 15 MiB VRAM used). Activating Ollama on GPU enables local inference with gemma4:e2b and qwen3-embedding models at 10-100x speedup vs CPU.

## Current State
- Ollama installed but service disabled (`systemctl is-active ollama.service` → inactive)
- NVIDIA GPU idle in P8, 0% utilization
- No models loaded in Ollama (port 11434 not listening)
- All LLM inference hypothetical (no active LLM calls from core engine)

## Physical Evidence
- Service file: `/etc/systemd/system/ollama.service`
- Binary: `/usr/bin/ollama`
- GPU: RTX 3060 6GB VRAM, NVIDIA driver 595.71.05, CUDA 13.2
- Models configured: gemma4:e2b, gemma4:e4b, gemma3:1b, qwen3-embedding

## Contract Invariants
- **GPU exclusive**: Ollama must use CUDA (not CPU) for inference; CPU fallback is acceptable for development
- **VRAM budget**: Must not exceed 5GB VRAM (leave 1GB for system/embeddings)
- **Persistence**: Service must survive reboots (enabled with proper deps)
- **Models**: All models in models_config.json must be pre-pulled

## Verification
```bash
ollama list 2>/dev/null | grep -q "gemma4" && echo "Models ready" || echo "Models missing"
curl -s http://localhost:11434/api/tags | grep -q "gemma4" && echo "Ollama running" || echo "Ollama not serving"
nvidia-smi | grep -v "No running processes" | grep -q "ollama" && echo "GPU active" || echo "No GPU inference"
```

## Traceability
- Maps to: FDA-002 (GPU-first compute)
- Source changes: `ollama.service.d/99-agentic.conf`, `models_config.json` (no changes needed)
