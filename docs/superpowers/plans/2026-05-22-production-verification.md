# Production Verification Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix registry discrepancies, then verify every component works in real production (not just unit tests).

**Architecture:** 3-phase: (1) fix registry + create missing files, (2) smoke-test each component individually, (3) full integration end-to-end.

**Tech Stack:** Python 3.14, uv, MCP SDK 1.26.0, Ollama (gemma4:e2b), fastembed, systemd

---

### Files to Create/Modify
- Create: `layers/l1_nervous/context/dimensions/__init__.py`
- Create: `layers/l1_nervous/dummie_sdk/routing/delegation.py`
- Create: `configs/models_config.json` (symlink to `layers/l1_nervous/configs/models_config.json`)
- Modify: `.aiwg/registry/mcp_registry.json` (fix 8 broken entries)
- Test: thin wrappers in legacy locations import correctly
- Test: Guardian daemon detects real violations
- Test: sub-gateway starts and serves requests

---

## Chunk 1: Registry Fixes

### Task 1.1: Fix `docker-mcp` entry (absolute path)

**Files:**
- Modify: `.aiwg/registry/mcp_registry.json`

The `docker-mcp` entry (index ~24) has `path: "docker-mcp"` which is a bare relative path. Change to use an absolute path like the other external entries:

```
"path": "/home/jorand/Escritorio/Biblioteca MCP/docker/",
```

The entry already has `canonical_target` pointing to the correct location. Fix the path to match.

### Task 1.2: Fix `scripts/dummie-engine.service` entry (wrong path)

The registry entry (index ~107) has `path: "scripts/dummie-engine.service"` but the actual file is at `scripts/systemd/dummie-engine.service`. Fix the path:

- Change entry's path to `scripts/systemd/dummie-engine.service`
- If duplicate exists at index ~76 with correct path, remove the wrong entry

### Task 1.3: Fix `configs/models_config.json` entry (root vs L1)

The registry entry (index ~151) has `path: "configs/models_config.json"` but the file is at `layers/l1_nervous/configs/models_config.json`. Two options:

- **Option A** (recommended): Create a symlink at root: `ln -s layers/l1_nervous/configs/models_config.json configs/models_config.json`, keep registry entry as-is
- **Option B**: Change registry entry to `layers/l1_nervous/configs/models_config.json`

Pick A for backward compatibility.

### Task 1.4: Create missing `context/dimensions/__init__.py`

**Files:**
- Create: `layers/l1_nervous/context/dimensions/__init__.py`

```python
from .temporal import TemporalDimension
from .spatial import SpatialDimension
from .semantic import SemanticDimension
from .relational import RelationalDimension
from .episodic import EpisodicDimension
from .instrumental import InstrumentalDimension

__all__ = [
    "TemporalDimension", "SpatialDimension", "SemanticDimension",
    "RelationalDimension", "EpisodicDimension", "InstrumentalDimension",
]
```

### Task 1.5: Create `dummie_sdk/routing/delegation.py`

**Files:**
- Create: `layers/l1_nervous/dummie_sdk/routing/delegation.py`

This is a thin re-export wrapper, same pattern as other thin wrappers:

```python
from routing.delegation import (
    DelegationEngine, DelegationRequest, DelegationDecision,
    DelegationStrategy, ExecutionLocation,
    LocalPreferenceStrategy, CloudPreferenceStrategy, VRAMAwareStrategy,
)

__all__ = [
    "DelegationEngine", "DelegationRequest", "DelegationDecision",
    "DelegationStrategy", "ExecutionLocation",
    "LocalPreferenceStrategy", "CloudPreferenceStrategy", "VRAMAwareStrategy",
]
```

### Task 1.6: Mark specs 15/16 as unresolvable

The `doc/specs/15_mcp_sidecar_isolation.md` and `doc/specs/16_mcp_dynamic_gateway.md` files were never written. The registry entries have `status: canonical` but the files don't exist.

Change their status to `planned` (not canonical) and add a note: "Spec file never authored. Status changed from canonical to planned."

### Task 1.7: Handle `.gemini/` entry (expected gap)

The `.gemini/skills/mcp_optimizer/SKILL.md` entry already has `status: duplicate` with a canonical target. No change needed — this is an expected gap for the Gemini-specific fork.

---

## Chunk 2: Thin Wrapper Verification

### Task 2.1: Verify all 11 thin wrappers import correctly

**Files:**
- Test: ALL 11 thin wrappers in legacy locations

Run this script to verify each thin wrapper imports from the SDK without errors:

```bash
cd /media/datasets/DUMMIE Engine/layers/l1_nervous
PYTHONPATH="..:$PYTHONPATH"

# Models package
uv run python3 -c "from models import model_registry, model_lifecycle, resource_monitor, session_context; print('models pkg OK')"

# Adapters package
uv run python3 -c "from models.adapters import base, ollama_adapter, fastembed_adapter, cross_encoder_adapter; print('adapters pkg OK')"

# Routing package
uv run python3 -c "from routing import pipeline, delegation; from routing.strategies import exact_match, embedding_match, cross_encoder_rerank, llm_reasoning, cot_reasoning; print('routing pkg OK')"
```

Expected: Each import succeeds. If any fails, the thin wrapper has a bug.

---

## Chunk 3: Guardian Daemon Smoke Test

### Task 3.1: Run Guardian daemon manually

**Files:**
- Test: `layers/l1_nervous/dummie_sdk/daemon/guardian_daemon.py`

Run the Guardian daemon for one scan cycle (not as a service, just to verify it works):

```bash
cd /media/datasets/DUMMIE Engine/layers/l1_nervous
PYTHONPATH="..:$PYTHONPATH" uv run python3 -c "
from dummie_sdk.daemon.guardian_daemon import GuardianDaemon
import asyncio
async def test():
    d = GuardianDaemon(
        scan_dirs=['.', '../layers/l2_brain'],
        exclude_patterns=['__pycache__', '.venv', '.git', 'dummie_sdk', 'generated'],
        interval=300
    )
    result = await d.scan_once()
    print(f'Files scanned: {result[\"files_scanned\"]}')
    print(f'Violations: {result[\"total_violations\"]}')
    for v in result.get('violations', []):
        print(f'  [{v.severity}] {v.rule}: {v.file}:{v.line}')
asyncio.run(test())
"
```

Expected: The daemon scans files and reports any violations. If there are hardcoded model strings in older files (outside dummie_sdk/generated), they should be detected.

### Task 3.2: Verify guardian daemon writes to disk

Check that the `.aiwg/runtime/guardian/` directory has status.json and violations.jsonl:

```bash
ls -la /media/datasets/DUMMIE Engine/.aiwg/runtime/guardian/
cat /media/datasets/DUMMIE Engine/.aiwg/runtime/guardian/status.json 2>/dev/null || echo "No status yet"
```

Expected: `status.json` exists with scan results.

---

## Chunk 4: Sub-Gateway Production Test

### Task 4.1: Start shell_gateway.py on port 8085

**Files:**
- Test: `layers/l1_nervous/gateway/shell_gateway.py`

The shell gateway is the simplest (no cloud dependencies — just shell, mcp-bash, browser-use). Start it:

```bash
cd /media/datasets/DUMMIE Engine/layers/l1_nervous
PYTHONPATH="..:$PYTHONPATH" uv run python gateway/shell_gateway.py &
SHELL_PID=$!
sleep 3
```

Then:
1. Check `.aiwg/runtime/gateways/shell.ready` exists
2. Test that the HTTP server responds on port 8085:

```bash
curl -s http://localhost:8085/health 2>/dev/null || echo "Health endpoint not available"
```

If health endpoint doesn't exist, check the BaseGateway implementation for an HTTP server (it uses MCP StdioServerParameters, so it may not expose an HTTP endpoint directly — it's a subprocess-based gateway).

Actually, looking at the code, `base_gateway.py` uses `StdioServerParameters` from the MCP library. These gateways connect to MCP sub-servers via stdio. They don't have an HTTP endpoint by default — they initiate MCP connections and serve via the MCP transport.

To verify the gateway started successfully:
```bash
cat /media/datasets/DUMMIE Engine/.aiwg/runtime/gateways/shell.ready
```
Expected: prints "ready"

### Task 4.2: Test the gateway via MetaGateway

**Files:**
- Test: `layers/l1_nervous/meta_router.py`, `layers/l1_nervous/metagateway.py`

Use the MetaGateway to route a query to the shell gateway:

```bash
cd /media/datasets/DUMMIE Engine/layers/l1_nervous
uv run python3 -c "
import asyncio
from metagateway import MetaGateway
async def test():
    mg = MetaGateway()
    route = await mg.route_request('listar archivos del directorio actual')
    print(f'Gateway: {route.get(\"gateway\")}')
    print(f'Port: {route.get(\"port\")}')
    print(f'Delegation: {route.get(\"delegation\", {})}')
    print(f'Servers: {route.get(\"servers\")}')
asyncio.run(test())
"
```

Expected: Routes to shell gateway (port 8085), delegation shows local/github or local/shell.

### Task 4.3: Stop the shell gateway

```bash
kill $SHELL_PID 2>/dev/null
```

---

## Chunk 5: Full Integration Test

### Task 5.1: Start ALL 5 sub-gateways via launcher

**Files:**
- Test: `scripts/start_metagateway.sh`

```bash
cd /media/datasets/DUMMIE Engine
bash scripts/start_metagateway.sh
```

Expected: All 5 gateways start. Readiness files appear in `.aiwg/runtime/gateways/`. Exit code 0.

### Task 5.2: Route real queries through MetaGateway

Test multiple query types:

```bash
cd /media/datasets/DUMMIE Engine/layers/l1_nervous
uv run python3 -c "
import asyncio
from metagateway import MetaGateway

async def test():
    mg = MetaGateway()
    queries = [
        'generar imagen de un gato',
        'git status',
        'listar contenedores docker', 
        'que hora es',
        'ejecutar comando ls -la',
    ]
    for q in queries:
        r = await mg.route_request(q)
        match = r.get('match', False)
        gw = r.get('gateway', '?')
        dom = r.get('domain', '?')
        del_info = r.get('delegation', {})
        del_str = f'{del_info.get(\"location\",\"?\")}/{del_info.get(\"server\",\"?\")}' if del_info else 'no-del'
        print(f'  {\"OK\" if match else \"--\"} | {q:35s} | gw={gw:10s} | dom={dom:20s} | del={del_str}')
asyncio.run(test())
"
```

### Task 5.3: Test Gemma 4 locally

```bash
uv run python3 -c "
import ollama
response = ollama.chat(model='gemma4:e2b', messages=[{'role':'user','content':'Di solo OK en una palabra'}])
print(response['message']['content'])
"
```

Expected: Prints "OK". If Ollama is not running, start it first.

### Task 5.4: Verify routing pipeline with Gemma 4

```bash
cd /media/datasets/DUMMIE Engine/layers/l1_nervous
PYTHONPATH="..:$PYTHONPATH" uv run python3 -c "
import asyncio
sys.path.insert(0, '.')
from routing.pipeline import RoutingPipeline
from routing.strategies.exact_match import ExactMatchStrategy
from routing.strategies.embedding_match import EmbeddingMatchStrategy
from routing.strategies.cross_encoder_rerank import CrossEncoderRerankStrategy
from routing.strategies.llm_reasoning import LLMReasoningStrategy

async def test():
    pipeline = RoutingPipeline([
        ExactMatchStrategy(),
        EmbeddingMatchStrategy(),
        CrossEncoderRerankStrategy(),
        LLMReasoningStrategy(),
    ])
    result = await pipeline.route('generar imagen 3d de un castillo')
    print(f'Match: {result.match}')
    print(f'Gateway: {result.gateway}')
    print(f'Confidence: {result.confidence:.3f}')
    print(f'Strategy: {result.strategy}')
asyncio.run(test())
"
```

Expected: Pipeline resolves the query (exact match should catch "imagen" → media_generation).

---

## Chunk 6: Guardian Daemon as Service

### Task 6.1: Run Guardian daemon as background process

```bash
cd /media/datasets/DUMMIE Engine/layers/l1_nervous
PYTHONPATH="..:$PYTHONPATH" nohup uv run python3 -m dummie_sdk.daemon.guardian_daemon > /tmp/guardian.log 2>&1 &
echo $! > /tmp/guardian.pid
sleep 5
cat /media/datasets/DUMMIE Engine/.aiwg/runtime/guardian/status.json
```

Expected: status.json shows scan completed, metrics for each scan interval.

### Task 6.2: Stop Guardian daemon

```bash
kill $(cat /tmp/guardian.pid) 2>/dev/null
```

---

## Verificación Final (acceptance criteria)

Run this single script to confirm everything is green:

```bash
cd /media/datasets/DUMMIE Engine

# 1. Registry integrity (all paths exist)
python3 -c "
import json
r = json.load(open('.aiwg/registry/mcp_registry.json'))
missing = [i for i in r['items'] if not (i['path'].startswith('/') or i['path'].startswith('.')) and i['status'] != 'duplicate']
print(f'Registry: {r[\"total_items\"]} items, {len(missing)} possible issues')
"

# 2. Thin wrappers import
cd layers/l1_nervous
PYTHONPATH="..:$PYTHONPATH" uv run python3 -c "
from models import model_registry, model_lifecycle, resource_monitor, session_context
from models.adapters import base, ollama_adapter, fastembed_adapter, cross_encoder_adapter
from routing import pipeline, delegation
from routing.strategies import exact_match, embedding_match, cross_encoder_rerank, llm_reasoning, cot_reasoning
print('All 11 thin wrappers import OK')
"

# 3. MetaGateway routes
uv run python3 -c "
import asyncio
from metagateway import MetaGateway
async def t():
    r = await MetaGateway().route_request('generar imagen')
    assert r.get('match'), 'imagen should match'
    assert 'delegation' in r, 'should have delegation'
    print(f'MetaGateway: OK (domain={r.get(\"domain\")}, del={r.get(\"delegation\",{}).get(\"location\")})')
asyncio.run(t())
"

# 4. Services exist
ls scripts/systemd/*.service | wc -l

# 5. Git clean
git status --short
```
