# Meta-Gateway Segmentado — Design Spec

**Date:** 2026-05-22
**Status:** Approved
**Spec #:** 170 (to be registered)

## Context

El gateway monolítico actual (`dummie_gateway_config.json`) tiene 13+ MCP servers en un solo proceso. Un fallo en cualquier server (db_locked, timeout, crash) afecta a todos. Además, no hay aislamiento entre dominios de capacidades (media, code, infra, etc.).

## Architecture

```
MetaGateway Proxy (stdio entry point)
  ├── Media Gateway (port 8081) — muapi, mcp-comfyui, cloudflare AI
  ├── Code Gateway (port 8082) — github, git, filesystem
  ├── Infra Gateway (port 8083) — docker, cloudflare infra, vercel
  ├── Knowledge Gateway (port 8084) — sqlite, sequentialthinking
  └── Shell Gateway (port 8085) — shell, mcp-bash, browser-use
```

### Principles

1. **Single entry point**: MetaGateway proxy recibe todas las requests via stdio
2. **Fail isolation**: Un sub-gateway caído no afecta a los demás
3. **SSOT per gateway**: Cada gateway tiene su propio `gateway_*.json` como fuente canónica
4. **No tool caching**: El MetaGateway nunca cachea tools — siempre delega al sub-gateway
5. **SI cache de índices**: Capability index, embedding vectors, similarity results (TTL controlado)

## Components

### gateway/base_gateway.py
Clase base: `__init__(config_path)`, `start()`, `stop()`, `call_tool(server, tool, args)`.
- Lee config JSON, arranca MCP servers via StdioClient
- Expone API HTTP ligera para el MetaGateway
- Escribe readiness state a `.aiwg/runtime/gateways/<name>.ready`

### metagateway.py
Punto de entrada único. Lee `meta_router_assignments.json` para saber qué gateway maneja qué capability.
- `route(query)` → detecta domain/action → redirige al sub-gateway correcto
- Si el sub-gateway no responde → failover a otro (si hay solapamiento)

### meta_router.py
Router basado en embeddings + exact match:
1. IntentClassifier extrae domain + action
2. Exact match contra capability_index (O(1))
3. Si no hay match: embedding similarity search + [opcional] LLM reasoning
4. Retorna `(gateway_name, server_name, tool_name, confidence)`

### embeddings/
- `embedding_service.py`: Centraliza fastembed BAAI/bge-small-en-v1.5. Wrapper thread-safe con pool de workers.
- `embedding_router.py`: Router embedding fine-tuneable para clasificar cadenas en 16 dominios. Inicialmente usa similarity + heurísticas, preparado para fine-tuning futuro.
- `embedding_cache.py`: LRU cache con TTL configurable (default: index=300s, similarity=60s).

## SSOT Flow

1. Cada sub-gateway publica `router_assignments_<name>.json` con su lista de capabilities
2. `capability_index.py` sincroniza desde todos los assignments → índice global
3. `meta_router_assignments.json` mapea domain+action → gateway
4. MetaGateway consulta el índice, nunca los assignments directamente

## Data Flow

```
Query → MetaGateway
  → meta_router.analyze(query)
    → IntentClassifier → (domain, action)
    → CapabilityIndex.match(domain, action) → (gateway, server, tool, confidence)
    → [confidence < threshold] → EmbeddingSearch + LLM reasoning
  → MetaGateway.call_subgateway(gateway, server, tool, args)
    → HTTP POST http://localhost:{port}/call
  → Response back to caller
```

## Error Handling

- Sub-gateway no responde: timeout 5s → log a quarantine → intentar failover
- Tool error del MCP: propagar con server_name + sugerencia
- MetaGateway crash: exit code 1, quarantine log
- Cada sub-gateway escribe su readiness: `.aiwg/runtime/gateways/<name>.ready`

## Caching Strategy

| Qué | TTL | Dónde |
|-----|-----|-------|
| Capability index (vectores) | 300s | embedding_cache.py |
| Similarity results | 60s | embedding_cache.py |
| Tool metadata | 300s | capability_index.py |
| Tool execution results | 0s (no cache) | — |

## Implementation Order

1. `gateway/` directory + `base_gateway.py`
2. 5 config JSONs
3. 5 sub-gateways (media, code, infra, knowledge, shell)
4. `meta_router_assignments.json` (SSOT global)
5. `embeddings/` (service, router, cache)
6. `meta_router.py` (orchestra embeddings + exact match)
7. `metagateway.py` (punto de entrada único)
8. Update `tools.py` (MetaGateway tools en lugar de directos)
9. Update registry + spec_bindings
10. Verification: 5/5 gateways responden, routing correcto
