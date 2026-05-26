---
status: APPROVED
layer: l1
domain:
- metagateway
- canonical
- routing
- smart
claims:
- id: SMART_METAGATEWAY_ARCHITECTURE-file-valid
  description: Spec file 'SMART_METAGATEWAY_ARCHITECTURE.md' exists, parses valid
    YAML frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Canonical Architecture: SMART MetaGateway

**Date:** 2026-05-26  
**Supersedes:** Legacy MetaGateway (Waves 1-7), standalone sub-gateways, parallel routing paths  

## 1. Architectural Problem

The DUMMIE Engine L1 Nervous system has three parallel paths that do not communicate:

| Path | Purpose | Status |
|------|---------|--------|
| MetaGateway (metagateway.py) | Route queries to sub-gateways via HTTP | **Dead code** — route_request() never called in production |
| MCPProxyManager (mcp_proxy.py) | Execute tools via STDIO subprocess | **Active** — used by dummie_execute_capability |
| Sub-gateways (gateway/*.py) | HTTP servers on ports 8081-8085 | **Legacy** — running but not in hot path |

Additionally, **45 MCP tools** are exposed to the agent, consuming ~5000 tokens of context window before any reasoning occurs.

## 2. Canonical Architecture

### 2.1 Single Entry Point

```
Agent (opencode/Claude)
  │
  │  2-3 tools exposed (was 45)
  │
  ▼
┌──────────────────────────────────────────────┐
│          MetaGateway (dispatcher)             │
│                                              │
│  dummie_process(intent, mode)                 │
│       │                                      │
│  ┌────┴────────────────────────┐              │
│  │ 1. SemanticRouteCache      │  L1+L2       │
│  │ 2. SmartRouter             │  tiny model  │
│  │ 3. ContextBudgetRouter     │  3 tiers     │
│  │ 4. SkillBinder             │  DAG exec    │
│  │ 5. MCPProxyManager         │  STDIO call  │
│  └────────────────────────────┘              │
│                                              │
│  Hooks: SDD guards, circuit breaker          │
│  Daemon: pre-warm, health, restart           │
└──────────────────────────────────────────────┘
```

### 2.2 Tools exposed to agent

| Tool | Purpose | When used |
|------|---------|-----------|
| `dummie_process` | Main entry — intent → cached/ routed/executed | Every query |
| `dummie_admin` | Install, health, config | Maintenance |

Total: **2 tools** in context instead of 45 (~5000 tokens saved).

### 2.3 Internal flow of dummie_process

```
dummie_process(intent, mode="auto")
  │
  ├─► L1 Cache (dict[sha256, result], ~30ns)
  │     hit → return (cache hit recorded)
  │
  ├─► L2 Cache (cosine similarity, ~15µs)
  │     hit → return (cache hit recorded)
  │
  ├─► SmartRouter (Qwen3.5:0.8b, ~50ms)
  │     ├─ classification: domain + confidence
  │     └─ confidence ≥ 0.8 → route
  │
  ├─► ContextBudgetRouter
  │     └─ select tool tier from available budget
  │
  ├─► SkillBinder
  │     └─ match intent → skill DAG → execute internally → compact result
  │
  ├─► MetacognitiveReasoner (gemma4:e2b, fallback only)
  │     └─ low confidence or novel query → LLM reasoning
  │
  ├─► Cache result (async, non-blocking)
  │
  └─► MCPProxyManager.call_tool(server, tool, args)
        └─ STDIO subprocess → JSON-RPC → result
```

### 2.4 What each component owns

| Component | Owns | Does NOT own |
|-----------|------|-------------|
| SemanticRouteCache | Cache storage, TTL, eviction, persistence | Routing logic, LLM calls |
| SmartRouter | Intent classification, tool selection | Cache, execution |
| ContextBudgetRouter | Tool tier selection by token budget | Routing, execution |
| SkillBinder | Multi-step DAG matching + execution | Single tool routing |
| MCPProxyManager | Subprocess lifecycle, STDIO transport | Routing decisions |
| MetacognitiveReasoner | Complex/novel query reasoning (rare) | Routine routing |

### 2.5 Data flow

```
intent ──► MetaGateway
             │
             ▼
         SemanticRouteCache.get(intent)
             │
             ├── hit ──► return cached route + exec
             │
             └── miss
                   │
                   ▼
               SmartRouter.route(intent, context_budget)
                   │
                   ├── confidence ≥ 0.8
                   │     │
                   │     ▼
                   │   SkillBinder.match(intent)
                   │     │
                   │     ├── skill match → execute DAG → compact result
                   │     │
                   │     └── no skill → MCPProxyManager.call_tool(server, tool)
                   │
                   └── confidence < 0.8
                         │
                         ▼
                     MetacognitiveReasoner.analyze(intent)
                         │
                         ▼
                     SmartRouter re-run with enriched intent
                         │
                         ▼
                     route + execute
```

## 3. Context Budget Strategy

### 3.1 Tier system (unchanged from Phase 1b)

| Tier | Token cost | Tools | When loaded |
|------|-----------|-------|-------------|
| 1 | 500 | filesystem (read/search), shell (basic) | Always |
| 2 | 1500 | git, github, sqlite, docker | Medium complexity |
| 3 | 3000 | browser-use, comfyui, n8n, sequential thinking | High complexity |

### 3.2 Progressive disclosure

The agent sends `dummie_process(intent)`. The MetaGateway:
1. Classifies intent via SmartRouter
2. Determines required tier from intent complexity
3. Only loads tools for that tier
4. If mid-execution needs higher tier, escalates internally (not visible to agent)

## 4. Skill DAG Execution

### 4.1 Matching

When SmartRouter returns a domain and confidence, SkillBinder checks:
- Does any skill template match the intent keywords?
- Does the domain overlap with the skill's trigger patterns?

### 4.2 Execution

1. Topological sort of skill's tool DAG
2. Parallel execution where dependencies allow
3. Intermediate results fed downstream
4. Compact summary returned to agent

### 4.3 Example: TDD skill

```yaml
skill_id: tdd
trigger_patterns: ["test", "tdd", "implement.*test"]
steps:
  - id: find_tests
    server: filesystem
    tool: search_files
    args: {pattern: "*_test.py"}
  - id: read_tests
    server: filesystem
    tool: read_text_file
    args: {}
    depends_on: [find_tests]
  - id: run_tests
    server: shell
    tool: execute_command
    args: {command: pytest}
    depends_on: [read_tests]
```

Agent sees: `dummie_process(intent="run tdd on user model")`  
Agent gets: `{status: "pass", coverage: "87%", failures: []}`  
Agent never sees the 3 individual tool calls.

## 5. Daemon Integration (L0)

### 5.1 Pre-warming

The L0 daemon maintains a set of "hot" MCP servers:
- filesystem (always hot)
- shell (always hot)
- git (on demand + keep warm for 5min after use)

### 5.2 Health

Daemon exposes health endpoint:
```
GET /health → {servers: {filesystem: "hot", shell: "hot", git: "idle"}}
```

MetaGateway checks health before routing decisions.

### 5.3 Restart

Daemon auto-restarts failed servers:
- 3 retries with exponential backoff
- After 3 failures, marks as degraded
- Notifies MetaGateway to bypass degraded servers

## 6. Migration Path

### Phase A — Benchmark (Spec 216)
Instrument the current system to measure:
- Context token usage per tool
- Discovery latency (dummie_discover_capabilities)
- Tool execution latency (dummie_execute_capability)
- Cold start frequency
- Cache hit/miss rate

### Phase B — Connect SMART (Spec 217)
- Wire SemanticRouteCache + SmartRouter into dummie_discover_capabilities
- Add cache check before MetacognitiveReasoner.analyze()
- Add cache write after successful route
- Measure improvement

### Phase C — dummie_process (Spec 218)
- New MCP tool: `dummie_process`
- MetaGateway.process() with full pipeline: cache → route → execute
- Retire standalone tool handlers behind dummie_process
- Expose only 2 tools to agent

### Phase D — Skill DAG (Spec 219)
- SkillBinder integration
- DAG execution engine
- Compact result formatting

### Phase E — Daemon (Spec 220)
- Pre-warming logic in L0
- Health API
- Auto-restart with degradation signaling

### Phase F — Sunset (Spec 221)
- Remove HTTP sub-gateways
- Decommission systemd services
- Remove legacy code paths
- All STDIO, all through MCPProxyManager

### Phase G — Post-benchmark
- Re-run benchmarks
- Compare metrics
- Document improvements

## 7. Success Criteria

| Metric | Before (estimate) | After (target) |
|--------|-------------------|----------------|
| Tools exposed to agent | 45 | 2 |
| Context tokens for schemas | ~5000 | ~300 |
| P50 discovery latency | 2-10s | <50ms (cache hit) |
| P99 discovery latency | 10-25s | <1s (LLM fallback) |
| Cache hit rate | 0% | >40% |
| Cold start rate | ~20% | <1% |
| Architecture paths | 3 parallel | 1 canonical |

## 8. Principles

1. **Single source of truth** — MetaGateway is the only routing authority
2. **Cache-first** — never invoke LLM if cache answers
3. **Progressive disclosure** — agent sees minimal tools, gateway handles complexity
4. **Skills as DAGs** — multi-step workflows are server-side, agent gets summary
5. **Measured before changed** — every phase has before/after metrics
6. **Legacy verified dead** — no code path removed until confirmed unused
