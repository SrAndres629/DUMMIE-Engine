---
spec_id: '207'
title: OpenCode Native Integration
status: ACTIVE
version: 1.0.0
layer: L1
tags:
- opencode
- integration
- mcp
- plugin
claims:
- id: 207_opencode_native_integration-file-valid
  description: Spec file '207_opencode_native_integration.md' exists, parses valid
    YAML frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/207_opencode_native_integration.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Spec 172: OpenCode Native Integration with DUMMIE Engine

## Abstract
DUMMIE Engine como kernel cognitivo, OpenCode como shell de interfaz. Esta spec define la integración nativa: SSOT único de DUMMIE, plugin de opencode con hooks, generación automática de configuración, multi-sesión por dominio, y Qwen3-Embedding como modelo primario de routing.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   OpenCode CLI/TUI                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │         dummie-opencode plugin (TS)              │   │
│  │  ┌─────────┐ ┌──────────┐ ┌────────────────┐    │   │
│  │  │dummie_  │ │chat.     │ │tool.execute.   │    │   │
│  │  │discover │ │params    │ │before (SDD)     │    │   │
│  │  │dummie_  │ │hook      │ │shell.env       │    │   │
│  │  │route    │ │          │ │system.transform │    │   │
│  │  └─────────┘ └──────────┘ └────────────────┘    │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │ MCP stdio
┌──────────────────────▼──────────────────────────────────┐
│              DUMMIE Engine (systemd)                     │
│  ┌─────────────┐  ┌─────────────────────────────────┐   │
│  │ dummie-brain │  │      MetaGateway + Router       │   │
│  │ (MCP Server) │  │  ExactMatch → EmbeddingMatch    │   │
│  │              │  │  (Qwen3-Embedding) → CoT → LLM  │   │
│  └─────────────┘  └────────┬────────────────────────┘   │
│                            │                            │
│  ┌──────────┐ ┌────────┐ ┌───────┐ ┌──────────┐ ┌─────┐│
│  │  Media   │ │  Code  │ │ Infra │ │Knowledge │ │Shell ││
│  │  :8081   │ │ :8082  │ │ :8083 │ │  :8084   │ │:8085 ││
│  └──────────┘ └────────┘ └───────┘ └──────────┘ └─────┘│
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Delegation  │  │    Swarm     │  │   Guardian   │   │
│  │  local/cloud │  │  multi-agent │  │ architecture │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└──────────────────────────────────────────────────────────┘
```

## SSOT Chain

```
models_config.json (modelos, providers, lifecycle)
dummie_gateway_config.json (topología MCP, perfiles)
meta_router_assignments.json (routing table, gateways)
         │
         ▼
generate_opencode_config.py
         │
         ▼
opencode.jsonc (generado, nunca editado manualmente)
```

## Components

### 1. Config Generator (`scripts/generate_opencode_config.py`)
- Lee `models_config.json`, `dummie_gateway_config.json`, `meta_router_assignments.json`
- Genera `opencode.jsonc` con MCP servers, plugin config, y metadata de DUMMIE
- Se ejecuta como `ExecStartPre` del servicio systemd

### 2. OpenCode Plugin (`layers/l1_nervous/plugins/opencode-dummie/`)
- TypeScript, compatible con opencode v1.15.5 plugin API
- 3 custom tools: `dummie_discover`, `dummie_route`, `dummie_swarm`
- Hooks: `chat.message` (session→gateway binding), `shell.env` (DUMMIE env vars), `system.transform` (context injection), `tool.execute.before` (SDD guardrails)

### 3. Systemd Service (`scripts/systemd/dummie-opencode.service`)
- After/Requires: dummie-engine.service
- ExecStartPre: generate_opencode_config.py
- ExecStart: opencode serve
- Environment: DUMMIE_ROOT, DUMMIE_DEFAULT_LLM, DUMMIE_DEFAULT_EMBEDDING

### 4. Qwen3-Embedding Integration
- Model: `qwen3-embedding` (0.6B) via Ollama
- Replaces `BAAI/bge-small-en-v1.5` como default embedding
- Dimensions: configurable via models_config.json
- Routing: primary model for EmbeddingMatchStrategy

## Routing Pipeline (per message)

```
1. ExactMatchStrategy (regex, conf=1.0) → match? → route
2. EmbeddingMatchStrategy (Qwen3-Embedding, conf>0.35) → match? → route
3. CrossEncoderRerankStrategy (rerank top-3, conf>0.5) → match? → route
4. CoTReasoningStrategy (Chain of Thought, conf>0.6) → match? → route
5. LLMReasoningStrategy (gemma4:e2b JSON, conf>0.7) → route
6. No match → research → integration plan
```

## Multi-Session Model

```
opencode session A ──→ MetaGateway ──→ media gateway (imagenes)
opencode session B ──→ MetaGateway ──→ code gateway (git)
opencode session C ──→ MetaGateway ──→ knowledge gateway (docs)

Swarm coordination:
  swarm.propose(objective) → distribute across sessions
  swarm.vote(plan) → consensus
  swarm.ack(result) → complete
```

## Verification

### Acceptance Criteria
1. `generate_opencode_config.py` produces valid opencode.jsonc
2. Plugin loads in opencode without errors
3. `dummie_route("genera una imagen")` returns domain=media_generation
4. `dummie_route("git status")` returns domain=vcs
5. Qwen3-Embedding is used by EmbeddingMatchStrategy
6. `dummie-opencode.service` can be installed and started
7. Gateway assignments persist per session

### Test Commands
```bash
uv run python scripts/generate_opencode_config.py
uv run python -m layers.l1_nervous.meta_router --query "genera una imagen"
uv run python -m layers.l1_nervous.meta_router --query "git status"
ollama ps  # verify qwen3-embedding is loaded
```
