#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT / "layers" / "l2_brain"
if str(L2) not in sys.path:
    sys.path.insert(0, str(L2))

from local_reasoning import DeterministicReasoningProvider, LocalReasoningService, estimate_tokens


DEFAULT_CASES = [
    {
        "goal": "retrieve project context before sending work to a cloud agent",
        "expected": ["local.knowledge_search_context"],
        "candidates": [
            {
                "id": "local.delete_everything",
                "text": "delete files permanently",
                "score": 0.91,
                "side_effect_level": "destructive",
            },
            {
                "id": "local.knowledge_search_context",
                "text": "search context and retrieve relevant knowledge",
                "score": 0.52,
                "side_effect_level": "read",
            },
        ],
    },
    {
        "goal": "persist a validated lesson in 4D-TES after a task succeeds",
        "expected": ["local.selection_feedback", "local.crystallize"],
        "candidates": [
            {
                "id": "local.knowledge_search_context",
                "text": "search context and retrieve knowledge",
                "score": 0.6,
                "side_effect_level": "read",
            },
            {
                "id": "local.selection_feedback",
                "text": "persist structured selection feedback in 4D-TES",
                "score": 0.5,
                "side_effect_level": "write",
            },
            {
                "id": "local.crystallize",
                "text": "persist validated knowledge in the 4D-TES memory engine",
                "score": 0.48,
                "side_effect_level": "write",
            },
        ],
    },
]


def load_cases(path: str | None) -> list[dict]:
    if not path:
        return DEFAULT_CASES
    target = ROOT / path
    return json.loads(target.read_text(encoding="utf-8"))


def precision_at_k(selected: list[str], expected: list[str], k: int) -> float:
    if not expected:
        return 1.0
    selected_set = set(selected[:k])
    expected_set = set(expected)
    return len(selected_set & expected_set) / min(k, len(expected_set))


def baseline_rank(candidates: list[dict], k: int) -> list[str]:
    ranked = sorted(candidates, key=lambda item: item.get("score", 0.0), reverse=True)
    return [item["id"] for item in ranked[:k]]


def run_benchmark(cases: list[dict], mode: str, k: int) -> dict:
    service = LocalReasoningService(
        provider=DeterministicReasoningProvider() if mode == "offline" else None
    )
    rows = []
    for case in cases:
        started = time.perf_counter()
        baseline_selected = baseline_rank(case["candidates"], k)
        rerank = service.reasoned_rerank(case["goal"], case["candidates"], max_selected=k, mode="shadow")
        shaped = service.context_shaper(case["goal"], rerank["ranked"], token_budget=4000, cloud_agent="benchmark")
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        selected = [item["id"] for item in rerank["ranked"][:k]]
        raw_tokens = estimate_tokens(json.dumps(case["candidates"], ensure_ascii=False))
        shaped_tokens = int(shaped.get("estimated_tokens", raw_tokens))
        rows.append(
            {
                "goal": case["goal"],
                "baseline_selected": baseline_selected,
                "local_selected": selected,
                "expected": case["expected"],
                "baseline_precision_at_k": precision_at_k(baseline_selected, case["expected"], k),
                "local_precision_at_k": precision_at_k(selected, case["expected"], k),
                "latency_ms": round(elapsed_ms, 3),
                "raw_candidate_tokens": raw_tokens,
                "shaped_tokens": shaped_tokens,
                "estimated_token_reduction": round(max(0.0, 1.0 - (shaped_tokens / max(1, raw_tokens))), 4),
                "provider_status": rerank.get("provider_status", "unknown"),
            }
        )
    count = max(1, len(rows))
    return {
        "mode": mode,
        "k": k,
        "cases": rows,
        "summary": {
            "baseline_precision_at_k": round(sum(row["baseline_precision_at_k"] for row in rows) / count, 4),
            "local_precision_at_k": round(sum(row["local_precision_at_k"] for row in rows) / count, 4),
            "avg_latency_ms": round(sum(row["latency_ms"] for row in rows) / count, 3),
            "avg_estimated_token_reduction": round(
                sum(row["estimated_token_reduction"] for row in rows) / count, 4
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark local reasoning over embedding recall candidates.")
    parser.add_argument("--fixture", help="Repo-relative JSON fixture path.")
    parser.add_argument("--mode", choices=["offline", "online"], default="offline")
    parser.add_argument("--k", type=int, default=1)
    args = parser.parse_args()

    report = run_benchmark(load_cases(args.fixture), mode=args.mode, k=args.k)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    summary = report["summary"]
    if summary["local_precision_at_k"] < summary["baseline_precision_at_k"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
