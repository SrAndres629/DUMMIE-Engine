from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class RepoIntelligenceQueryResult:
    query: dict[str, Any]
    results: list[dict[str, Any]]
    count: int
    decision: str = "PASS"
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RepoIntelligenceQueryRuntime:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.intel_root = self.aiwg_root / "repo_intelligence"
        self.reports_root = self.aiwg_root / "reports"

    def query_repo_intelligence(
        self, query: dict[str, Any]
    ) -> RepoIntelligenceQueryResult:
        inventory_path = self.intel_root / "repo_inventory.json"
        if not inventory_path.exists():
            return RepoIntelligenceQueryResult(
                query=query,
                results=[],
                count=0,
                decision="FAIL",
                generated_at=self._utc_now(),
            )

        with open(inventory_path, "r", encoding="utf-8") as f:
            inventory = json.load(f)
        files = inventory.get("files", [])

        results = []

        # Simple filtering logic
        layer = query.get("layer")
        language = query.get("language")
        is_runtime = query.get("is_runtime")
        is_test = query.get("is_test")
        is_spec = query.get("is_spec")
        category = query.get("category")
        path_contains = query.get("path_contains")
        no_tests = query.get("no_tests", False)

        test_paths = [f["path"] for f in files if f.get("is_test")]

        for f in files:
            if layer and f.get("layer") != layer:
                continue
            if language and f.get("language") != language:
                continue
            if is_runtime is not None and f.get("is_runtime") != is_runtime:
                continue
            if is_test is not None and f.get("is_test") != is_test:
                continue
            if is_spec is not None and f.get("is_spec") != is_spec:
                continue
            if category and f.get("category") != category:
                continue
            if path_contains and path_contains not in f["path"]:
                continue

            if no_tests and f.get("is_runtime"):
                name = Path(f["path"]).stem
                if any(f"test_{name}" in tp for tp in test_paths):
                    continue

            results.append(f)

        limit = query.get("limit", 100)
        results = results[:limit]

        return RepoIntelligenceQueryResult(
            query=query,
            results=results,
            count=len(results),
            generated_at=self._utc_now(),
        )

    def _utc_now(self) -> str:
        return (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )


def query_repo_intelligence(
    query: dict[str, Any], aiwg_root: str | Path = ".aiwg"
) -> RepoIntelligenceQueryResult:
    runtime = RepoIntelligenceQueryRuntime(aiwg_root=aiwg_root)
    result = runtime.query_repo_intelligence(query)

    reports_dir = Path(aiwg_root) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "repo_intelligence_query_latest.json").write_text(
        json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8"
    )

    return result
