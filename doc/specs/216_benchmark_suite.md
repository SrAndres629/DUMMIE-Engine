---
status: Approved
claims:
- id: benchmark_runs
  description: Benchmark ejecuta sin errores y produce JSON valido
  severity: critical
  verify_cmd: uv run python -m tests.bench_metagateway
- id: context_tax_measured
  description: Metrica context_tax presente con valor positivo
  severity: high
implementations:
  - file: layers/l1_nervous/tests/bench_metagateway.py
    class: BenchmarkSuite
    type: primary
---

# Benchmark Suite for SMART MetaGateway

**Date:** 2026-05-26  
**Phase:** A  
**Requires reboot:** No  
**Depends on:** Nothing  
**Files created:** `layers/l1_nervous/tests/bench_metagateway.py`

## 1. Purpose

Establish performance baseline for the current system before making architectural changes. Measure the seven key metrics that determine LLM agent experience. Run as a standalone script that produces a JSON report.

## 2. Metrics

### 2.1 Context tax (tokens)

How many tokens do tool schemas consume from the agent's context window?

**Method:** Call `dummie_discover_capabilities("*")` and count token usage of all tool schemas.

```
context_tax = sum(len(encode(t.schema)) for t in all_tools)
```

**Expected:** ~5000 tokens (45 tools × ~110 avg schema tokens)

### 2.2 Discovery latency (ms)

How long does it take to find the right tool for a query?

**Method:** 
- Time `dummie_discover_capabilities(query)` for 10 sample queries
- Measure P50, P95, P99
- Sample queries: "find a file", "create a git branch", "deploy docker", "search knowledge", "generate image"

### 2.3 Execution latency (ms)

How long does infrastructure overhead add per tool call?

**Method:**
- Call `dummie_execute_capability(filesystem.ping, {})` or any no-op target
- Measure total time vs actual tool execution time
- `overhead = total_time - tool_execution_time`

**Expected:** ~200ms (SDD guard + MCPProxyManager + STDIO JSON-RPC)

### 2.4 Cold start rate

How often does a tool call trigger a subprocess spawn?

**Method:**
- Call 10 different tools sequentially
- Record which calls triggered `_ensure_ready()` (subprocess spawn) vs used cached process
- `cold_start_rate = cold_starts / total_calls`

### 2.5 Cold start latency (ms)

How long does the first call to each server take?

**Method:**
- First call to each server: total latency
- Subsequent calls: average latency
- `cold_start_penalty = first_call - avg_subsequent`

### 2.6 Cache hit rate

Test the current cache (should be 0 — no cache exists yet).

**Method:**
- Call `dummie_discover_capabilities("find file")` with same query 5 times
- Record whether each call reused a previous result
- Baseline: 0% (reference for Phase B improvement)

### 2.7 Routing consistency

Does the same query return the same route?

**Method:**
- Same query to `dummie_discover_capabilities` 3 times
- Check if result domain/tool is the same
- `consistency = identical_results / 3`

## 3. Implementation

### 3.1 File: `layers/l1_nervous/tests/bench_metagateway.py`

Single-file benchmark script. Design:

```python
"""
Benchmark suite for DUMMIE Engine MetaGateway.
Measures 7 key metrics before/after architectural changes.
Run: uv run python -m tests.bench_metagateway
Output: benchmarks/baseline_2026-05-26.json
"""

import asyncio
import json
import time
import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Any

REPORT_DIR = Path(os.environ.get("DUMMIE_ROOT", "/media/datasets/DUMMIE Engine")) / ".aiwg" / "benchmarks"


@dataclass
class BenchmarkResult:
    """Single benchmark run."""
    timestamp: str
    metric: str                      # "context_tax" | "discovery_latency" | ...
    value: Any                       # Main value (float for latencies, int for tokens, etc.)
    unit: str                        # "tokens" | "ms" | "rate"
    samples: list[float] = None      # Raw sample values (for percentiles)
    metadata: dict = None            # Context about the run


class BenchmarkSuite:
    """Benchmark suite for MetaGateway performance metrics."""

    def __init__(self, tag: str = "baseline"):
        self.tag = tag
        self.results: list[BenchmarkResult] = []
        self.timestamp = datetime.utcnow().isoformat()

    async def run_all(self):
        """Run all benchmarks in sequence."""
        await self.measure_context_tax()
        await self.measure_discovery_latency()
        await self.measure_execution_overhead()
        await self.measure_cold_start()
        await self.measure_cache_hit()
        await self.measure_routing_consistency()

    async def measure_context_tax(self):
        """Estimate token cost of all tool schemas visible to agent."""
        # Heavy import only when benchmarking
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")

        # Collect all tool schemas
        schemas = []

        # Local tools (internal_mcp)
        from mcp.server.fastmcp import FastMCP
        internal = FastMCP("Internal-Registry")
        from tools import register_tools

        # Dummy getters for registration
        def dummy_orch():
            return None
        def dummy_proxy():
            return None

        register_tools(internal, lambda: None, lambda: None, "/tmp")

        local_tools = internal._tool_manager.list_tools()
        for t in local_tools:
            schema_str = json.dumps({"name": t.name, "description": t.description, "parameters": t.parameters})
            schemas.append(schema_str)

        tokens = sum(len(enc.encode(s)) for s in schemas)

        self.results.append(BenchmarkResult(
            timestamp=self.timestamp,
            metric="context_tax",
            value=tokens,
            unit="tokens",
            metadata={"tool_count": len(schemas), "type": "local"}
        ))
        print(f"  context_tax: {tokens} tokens for {len(schemas)} tools")

    async def measure_discovery_latency(self):
        """Measure how long dummie_discover_capabilities takes per query."""
        from tools import register_tools

        test_queries = [
            "find a file named config.json",
            "create a git branch called feature/foo",
            "deploy docker container for nginx",
            "search knowledge about user authentication",
            "generate an image of a cat",
            "what's the current system status",
            "run shell command ls -la",
            "install a new MCP server for database",
            "self-program a new tool for API integration",
            "analyze capability git.git_status",
        ]

        latencies = []
        for query in test_queries:
            # We measure via the actual tool call path
            # Use the MCP server's registered tool directly if possible
            t0 = time.monotonic()

            # This is a simplified benchmark — real version calls the actual
            # dummie_discover_capabilities via MCP protocol or direct import
            await asyncio.sleep(0.01)  # placeholder

            elapsed = (time.monotonic() - t0) * 1000
            latencies.append(elapsed)

        latencies.sort()
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]

        self.results.append(BenchmarkResult(
            timestamp=self.timestamp,
            metric="discovery_latency",
            value={"p50_ms": p50, "p95_ms": p95, "p99_ms": p99},
            unit="ms",
            samples=latencies,
        ))

    async def measure_execution_overhead(self):
        """Measure infra overhead per tool call (vs actual exec)."""
        # Call a no-op or fast tool multiple times
        # Record total time — infrastructure cost is total (no actual work)
        pass

    async def measure_cold_start(self):
        """Measure cold start rate and penalty."""
        pass

    async def measure_cache_hit(self):
        """Should be 0% for baseline."""
        pass

    async def measure_routing_consistency(self):
        """Same query 3x → same result?"""
        pass

    def save_report(self):
        """Save benchmark results to JSON file."""
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        report_path = REPORT_DIR / f"benchmark_{self.tag}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        data = {
            "tag": self.tag,
            "timestamp": self.timestamp,
            "results": [asdict(r) for r in self.results],
        }
        report_path.write_text(json.dumps(data, indent=2))
        print(f"\nReport saved: {report_path}")
        return report_path


async def main():
    suite = BenchmarkSuite(tag="baseline")
    print("Running benchmark suite (baseline)...")
    await suite.run_all()
    suite.save_report()


if __name__ == "__main__":
    asyncio.run(main())
```

### 3.2 Key design decisions

1. **Standalone file** — no changes to existing code. Pure measurement.
2. **JSON output** — machine-readable, comparable across runs.
3. **Tag system** — "baseline", "post-phase-b", "post-phase-c" for diffing.
4. **Asyncio** — matches the runtime model.
5. **Heavy imports lazy** — expensive imports (tiktoken) only when benchmark runs.

### 3.3 Sample queries for discovery benchmark

| Query | Expected domain | Complexity |
|-------|----------------|------------|
| "find a file named config.json" | workspace_io | low |
| "create a git branch called feature/foo" | vcs | low |
| "deploy docker container for nginx" | infrastructure | medium |
| "search knowledge about user auth" | knowledge | low |
| "generate an image of a cat" | media_generation | low |
| "what's the current system status" | system | low |
| "run shell command ls -la" | shell | low |
| "how do I optimize the latency of the du engine" | metacognition | high |
| "create a new MCP server that monitors disk usage" | auto_evolver | high |
| "debug why the gateway is crashing on startup" | metacognition | high |

## 4. Success Criteria

| Metric | Target | How measured |
|--------|--------|-------------|
| Script runs without errors | ✅ | Exit code 0 |
| Outputs valid JSON | ✅ | json.loads succeeds |
| All 6 metrics measured | ✅ | Non-null values |
| Complete in <60s | ✅ | Wall clock |

## 5. Files

| File | Action |
|------|--------|
| `layers/l1_nervous/tests/bench_metagateway.py` | **Create** — benchmark suite |
| `.aiwg/benchmarks/baseline_*.json` | **Create** — first report |