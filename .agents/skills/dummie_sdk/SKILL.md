---
name: DUMMIE Engine SDK
description: Biblioteca canónica para modelos, routing, delegación y validación arquitectónica. SSOT de configuración, sin strings hardcodeados.
version: 1.0.0
---

# DUMMIE Engine SDK (`dummie_sdk/`)

## Arquitectura

`layers/l1_nervous/dummie_sdk/` es la biblioteca canónica del DUMMIE Engine. Toda interacción con modelos, routing y delegación debe pasar por aquí. El código legacy en `layers/l1_nervous/models/`, `routing/`, `embeddings/` son thin wrappers que delegan al SDK.

```
dummie_sdk/
├── config.py                 # SDKConfig + load_config() — SSOT
├── models/
│   ├── model_registry.py     # Registry config-driven con importlib
│   ├── model_lifecycle.py    # TTL unload, priority queue
│   ├── resource_monitor.py   # VRAM/RAM con nvidia-smi + zram
│   └── adapters/
│       ├── base.py           # BaseModelAdapter abstracto
│       ├── ollama_adapter.py # OllamaAsyncClient
│       ├── fastembed_adapter.py  # TextEmbedding singleton
│       └── cross_encoder_adapter.py  # CrossEncoder rerank
├── routing/
│   ├── types.py              # RoutingResult, RoutingStrategy protocol
│   ├── pipeline.py           # Chain of Responsibility
│   ├── delegation.py         # Local vs Cloud con Strategy pattern
│   └── strategies/
│       ├── base.py           # _ensure_loaded compartido
│       ├── exact_match.py    # 11 regex patterns
│       ├── embedding_match.py # fastembed similarity >0.35
│       ├── cross_encoder_rerank.py  # rerank top-3
│       ├── llm_reasoning.py  # Gemma 4 JSON routing
│       └── cot_reasoning.py  # Chain of Thought
├── validation/
│   ├── guardian.py           # ArchitectureGuardian
│   └── rules.py              # 7 Rule dataclasses
├── hooks/
│   ├── pre_commit.py         # Git pre-commit hook
│   └── install.py            # Hook installer
└── daemon/
    └── guardian_daemon.py    # Background guardian daemon
```

## Configuración (SSOT)

Toda configuración de modelos vive en `configs/models_config.json`:

```json
{
  "models": {
    "llm": { "model_id": "gemma4:2b", "provider": "ollama", "type": "llm" },
    "embedding": { "model_id": "BAAI/bge-small-en-v1.5", "provider": "fastembed", "type": "embedding" },
    "reranker": { "model_id": "cross-encoder/ms-marco-MiniLM-L-2-v2", "provider": "cross_encoder", "type": "reranker" }
  }
}
```

Para cambiar de modelo (ej. gemma4:2b → gemma4:e4b), solo edita este JSON. No toques código.

## Uso

```python
from dummie_sdk.config import load_config
from dummie_sdk.models.model_registry import ModelRegistry

config = load_config()
registry = ModelRegistry(config_path="configs/models_config.json")
adapter = await registry.get_or_create("gemma4:2b")
result = await adapter.generate("prompt aquí")
```

## Guardian

El ArchitectureGuardian valida que no haya violaciones arquitectónicas:

```bash
# Manual
uv run python -m dummie_sdk.validation.guardian

# Como pre-commit hook (instalado vía hooks/install.py)
# Se ejecuta automáticamente en cada git commit
```

Reglas que verifica: hardcoded models, legacy imports, duplicate patterns, forbidden patterns, import circularity, large files, naming conventions.

## Daemon Guardian

El guardian daemon corre en background cada 300s:
```bash
uv run python -m dummie_sdk.daemon.guardian_daemon &
```

## Delegación (Local vs Cloud)

El `DelegationEngine` decide dónde ejecutar basado en:
1. **VRAM**: si < 2048MB libre, prefiere cloud
2. **Tipo de servidor**: cloud-only (muapi, vercel, cloudflare) vs local-only (docker, shell, git)
3. **Estrategia configurable**: LocalPreference, CloudPreference, VRAMAware

```python
from dummie_sdk.routing.delegation import DelegationEngine, DelegationRequest

engine = DelegationEngine()
decision = await engine.decide(DelegationRequest(servers=["muapi", "mcp-comfyui"], vram_free_mb=1024))
# → location=cloud, server=muapi (VRAM bajo)
```

## Routing Pipeline

Chain of Responsibility con 5 estrategias en orden:
1. ExactMatch (regex, conf=1.0)
2. EmbeddingMatch (fastembed >0.35)
3. CrossEncoderRerank (rerank top-3)
4. CoTReasoning (Chain of Thought paso a paso)
5. LLMReasoning (Gemma 4 JSON routing)

Threshold mínimo: 0.5. Si ninguna estrategia alcanza, retorna no-match.
