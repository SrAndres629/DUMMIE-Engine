# Model Adapters + Routing Pipeline — Design Spec

**Date:** 2026-05-22
**Status:** Approved  
**Spec #:** 171

## Architecture

### Model Layer (`models/`)
```
ModelRegistry (SSOT de modelos disponibles)
  ├── Adapter Pattern: BaseModelAdapter → OllamaAdapter, FastEmbedAdapter, CrossEncoderAdapter
  ├── Lifecycle: load/unload with TTL idle timeout
  └── ResourceMonitor: RAM/VRAM-aware loading decisions
```

### Routing Layer (`routing/`)
```
RoutingPipeline (Chain of Responsibility)
  ├── Strategy 1: ExactMatch (regex, conf=1.0)
  ├── Strategy 2: EmbeddingMatch (fastembed, conf=0.35-1.0)
  ├── Strategy 3: CrossEncoderRerank (cross-encoder, rerank top-5)
  └── Strategy 4: LLMReasoning (Gemma 3/4, fallback)
```

### Patterns Used

| Pattern | Dónde | Propósito |
|---|---|---|
| **Adapter** | `models/adapters/base.py` | Interfaz unificada para todos los modelos (embedding, LLM, reranker) |
| **Factory** | `model_registry.py:create_adapter()` | Creación lazy de adapters por model_id |
| **Singleton** | `FastEmbedAdapter.get_instance()` | Una instancia por modelo embedding (compartida) |
| **Chain of Resp.** | `routing/pipeline.py` | Estrategias encadenadas con threshold |
| **Strategy** | `routing/strategies/*.py` | Cada algoritmo de routing encapsulado |
| **Registry** | `model_registry.py` | SSOT de modelos disponibles |
| **Facade** | `models/__init__.py` | Punto de acceso único al model layer |

### Resource Optimization

1. **VRAM**: `ResourceMonitor.snapshot()` antes de cargar modelos LLM. Solo carga si hay VRAM suficiente.
2. **RAM**: Embedding models (~200MB) siempre cargados. LLM loading condicional.
3. **TTL Unload**: `ModelLifecycle` descarga modelos idle después de 300s (LLM) o 600s (embedding/reranker).
4. **Session Context**: `SessionContext` mantiene historial de queries para enriquecer prompts.
5. **Shared Instance**: `FastEmbedAdapter.get_instance()` asegura una sola copia en RAM del modelo embedding.

### Ontology Integration

Cada modelo tiene una `OntologyClass`:
- `SEMANTIC`: Embedding models (bge-small-en-v1.5)
- `REASONING`: LLM models (Gemma)
- `SEARCH`: Reranker models (cross-encoder)
- `ROUTING`: Router models (futuro fine-tune)
- `CODE`: Code models (futuro DeepSeek Coder)

El `RoutingPipeline` reporta la estrategia usada + dominio ontológico en cada resultado.
