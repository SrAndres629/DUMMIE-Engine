#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - dependency is present in L2 env
    raise SystemExit("PyYAML is required to run ORBIT-lite") from exc


DEFAULT_CASES = Path("tests/benchmarks/orbit_lite_cases.yaml")
DEFAULT_JSON = Path("reports/benchmarks/orbit_lite_score.json")
DEFAULT_MARKDOWN = Path("reports/benchmarks/orbit_lite_scorecard.md")

METRICS = [
    "evidence_precision",
    "evidence_recall",
    "contradiction_detection",
    "causal_ordering",
    "six_d_context_correctness",
    "corrective_action_quality",
    "hallucination_penalty",
    "persona_alignment",
    "pattern_detection_quality",
]


def infer_status(evidence: list[dict[str, Any]]) -> str:
    if not evidence:
        return "INSUFFICIENT_EVIDENCE"
    if any(item.get("contradicts") for item in evidence):
        return "CONTRADICTED"
    if any(item.get("supports") for item in evidence):
        return "SUPPORTED"
    return "ASSUMPTION"


def score_case(case: dict[str, Any]) -> dict[str, Any]:
    predicted = infer_status(case.get("evidence", []))
    expected = case.get("expected_status")
    status_score = 1.0 if predicted == expected else 0.0
    metric_scores = {name: float(case.get("metrics", {}).get(name, 0.0)) for name in METRICS}

    # hallucination_penalty is better when lower; convert to quality contribution.
    metric_contributions = [
        1.0 - metric_scores["hallucination_penalty"] if name == "hallucination_penalty" else metric_scores[name]
        for name in METRICS
    ]
    quality_score = mean(metric_contributions) if metric_contributions else 0.0
    total_score = round((status_score * 0.4) + (quality_score * 0.6), 4)
    return {
        "id": case["id"],
        "expected_status": expected,
        "predicted_status": predicted,
        "status_score": status_score,
        "metric_scores": metric_scores,
        "score": total_score,
    }


def load_cases(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    cases = data.get("cases", []) if isinstance(data, dict) else []
    if not cases:
        raise SystemExit(f"No ORBIT-lite cases found in {path}")
    return cases


def write_markdown(path: Path, results: dict[str, Any]) -> None:
    lines = [
        "# ORBIT-lite Scorecard",
        "",
        f"- Cases: {results['case_count']}",
        f"- Overall score: {results['overall_score']:.4f}",
        "",
        "| Case | Expected | Predicted | Score |",
        "| --- | --- | --- | --- |",
    ]
    for case in results["cases"]:
        lines.append(
            f"| {case['id']} | {case['expected_status']} | {case['predicted_status']} | {case['score']:.4f} |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run(cases_path: Path, json_path: Path, markdown_path: Path) -> dict[str, Any]:
    case_results = [score_case(case) for case in load_cases(cases_path)]
    results = {
        "case_count": len(case_results),
        "overall_score": round(mean(case["score"] for case in case_results), 4),
        "cases": case_results,
    }
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(markdown_path, results)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic ORBIT-lite reasoning benchmark.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()

    results = run(args.cases, args.json_output, args.markdown_output)
    print(f"ORBIT-lite: {results['case_count']} cases, score={results['overall_score']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
