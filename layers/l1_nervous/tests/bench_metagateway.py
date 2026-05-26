"""
Benchmark suite for DUMMIE Engine MetaGateway.
Measures 7 key metrics for LLM agent experience.

Usage:
    uv run python -m tests.bench_metagateway          # baseline
    uv run python -m tests.bench_metagateway --tag post-phase-b  # after changes
"""

import asyncio
import argparse
import json
import time
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, asdict, field
from typing import Any

L1_ROOT = Path(__file__).resolve().parents[1]
DUMMIE_ROOT = Path(os.environ.get("DUMMIE_ROOT", str(L1_ROOT.parent.parent)))
sys.path.insert(0, str(L1_ROOT))
sys.path.insert(0, str(DUMMIE_ROOT))

REPORT_DIR = DUMMIE_ROOT / ".aiwg" / "benchmarks"


@dataclass
class BenchmarkResult:
    timestamp: str
    metric: str
    value: Any
    unit: str
    samples: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


SAMPLE_QUERIES = [
    ("find a file named config.json", "workspace_io"),
    ("create a git branch called feature/foo", "vcs"),
    ("deploy docker container for nginx", "infrastructure"),
    ("search knowledge about user authentication", "knowledge"),
    ("generate an image of a cat", "media_generation"),
    ("run shell command ls -la", "shell"),
    ("what is the current system status", "system"),
    ("optimize the latency of the duck engine", "metacognition"),
    ("create a new MCP server for monitoring", "auto_evolver"),
    ("debug why the gateway is crashing on startup", "metacognition"),
]


class BenchmarkSuite:
    def __init__(self, tag: str = "baseline"):
        self.tag = tag
        self.results: list[BenchmarkResult] = []
        self.timestamp = datetime.now(timezone.utc).isoformat()

    async def run_all(self):
        print(f"\n=== Benchmark: {self.tag} ===\n")
        await self.measure_context_tax()
        await self.measure_discovery_latency()
        # Placeholder for server-dependent metrics
        print("  [SKIP] execution_overhead — needs running MCP server")
        print("  [SKIP] cold_start — needs running MCP server")
        print("  [SKIP] cache_hit — needs running MCP server")
        print("  [SKIP] routing_consistency — needs running MCP server")

    async def measure_context_tax(self):
        """Count tools registered in dummie_gateway_config.json and their schema complexity."""
        print("  Measuring context_tax...")
        try:
            import tiktoken

            enc = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            enc = None

        config_path = DUMMIE_ROOT / "dummie_gateway_config.json"
        try:
            config = json.loads(config_path.read_text())
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"  [WARN] Cannot load config: {e}")
            return

        servers = config.get("mcpServers", {})
        tool_schemas = []
        for sname, scfg in servers.items():
            desc = scfg.get("rationale", scfg.get("description", ""))
            cc = scfg.get("capability_class", "")
            schema_str = json.dumps(
                {
                    "server": sname,
                    "command": scfg.get("command", ""),
                    "description": desc,
                    "capability_class": cc,
                },
                ensure_ascii=False,
            )
            tool_schemas.append(schema_str)

        if enc:
            tokens = sum(len(enc.encode(s)) for s in tool_schemas)
        else:
            tokens = sum(len(s.encode("utf-8")) for s in tool_schemas)

        self.results.append(
            BenchmarkResult(
                timestamp=self.timestamp,
                metric="context_tax",
                value=tokens,
                unit="tokens",
                metadata={
                    "server_count": len(servers),
                    "encoding": "tiktoken" if enc else "bytes",
                },
            )
        )
        print(f"  context_tax: ~{tokens} tokens for {len(servers)} MCP servers")

    async def measure_discovery_latency(self):
        """Measure MetaRouter route latency for sample queries.

        Uses the MetaRouter directly (no MCP server needed) to measure
        regex-based routing and embedding fallback latency.
        """
        print("  Measuring discovery_latency...")

        from meta_router import MetaRouter

        router = MetaRouter()

        all_latencies = []

        for query, _expected_domain in SAMPLE_QUERIES:
            t0 = time.monotonic()
            route = await router.route(query)
            elapsed = (time.monotonic() - t0) * 1000
            all_latencies.append(elapsed)

        all_latencies.sort()
        p50 = all_latencies[len(all_latencies) // 2]
        p95 = all_latencies[int(len(all_latencies) * 0.95)]
        p99 = all_latencies[int(len(all_latencies) * 0.99)]

        self.results.append(
            BenchmarkResult(
                timestamp=self.timestamp,
                metric="discovery_latency",
                value={"p50_ms": p50, "p95_ms": p95, "p99_ms": p99},
                unit="ms",
                samples=all_latencies,
                metadata={
                    "queries": len(SAMPLE_QUERIES),
                    "method": "meta_router.route()",
                },
            )
        )
        print(f"  discovery_latency: p50={p50:.1f}ms p95={p95:.1f}ms p99={p99:.1f}ms")

    def save_report(self):
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_path = REPORT_DIR / f"benchmark_{self.tag}_{ts}.json"
        data = {
            "tag": self.tag,
            "timestamp": self.timestamp,
            "results": [asdict(r) for r in self.results],
        }
        report_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"\nReport: {report_path}")
        return report_path


async def main():
    parser = argparse.ArgumentParser(description="Benchmark DUMMIE MetaGateway")
    parser.add_argument(
        "--tag", default="baseline", help="Benchmark tag (baseline, post-phase-b, ...)"
    )
    args = parser.parse_args()

    suite = BenchmarkSuite(tag=args.tag)
    await suite.run_all()
    suite.save_report()


if __name__ == "__main__":
    asyncio.run(main())
