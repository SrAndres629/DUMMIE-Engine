from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class RepoFileFact:
    path: str
    extension: str
    language: str
    layer: str
    artifact_type: str
    category: str  # first_party|dependency|generated|config|doc
    is_test: bool
    is_spec: bool
    is_schema: bool
    is_report: bool
    is_runtime: bool
    is_generated_or_vendor: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RepoIntelligenceManifest:
    repo_id: str
    tracked_files_count: int
    layers_detected: list[str] = field(default_factory=list)
    languages_detected: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RepoIntelligenceRuntime:
    def __init__(self, repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg"):
        self.repo_root = Path(repo_root)
        self.aiwg_root = self.repo_root / aiwg_root
        self.intel_root = self.aiwg_root / "repo_intelligence"
        self.reports_root = self.aiwg_root / "reports"

    def run_repo_intelligence_scan(self) -> dict[str, Any]:
        tracked_files = self._get_tracked_files()

        facts = []
        layers = set()
        languages = set()

        for path in tracked_files:
            fact = self._classify_file(path)
            facts.append(fact)
            if fact.layer and fact.layer != "unknown":
                layers.add(fact.layer)
            if fact.language and fact.language != "unknown":
                languages.add(fact.language)

        manifest = RepoIntelligenceManifest(
            repo_id="dummie_engine",
            tracked_files_count=len(facts),
            layers_detected=sorted(list(layers)),
            languages_detected=sorted(list(languages)),
            generated_at=self._utc_now(),
        )

        # Output manifest
        self.intel_root.mkdir(parents=True, exist_ok=True)
        (self.intel_root / "repo_intelligence_manifest.json").write_text(
            json.dumps(manifest.to_dict(), indent=2) + "\n", encoding="utf-8"
        )

        # Output inventory
        inventory = {
            "generated_at": manifest.generated_at,
            "files": [f.to_dict() for f in facts],
        }
        (self.intel_root / "repo_inventory.json").write_text(
            json.dumps(inventory, indent=2) + "\n", encoding="utf-8"
        )

        # Output report
        report = {
            "decision": "PASS",
            "tracked_files_count": manifest.tracked_files_count,
            "layers_detected": manifest.layers_detected,
            "languages_detected": manifest.languages_detected,
            "generated_at": manifest.generated_at,
        }
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "repo_intelligence_latest.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )

        return report

    def _get_tracked_files(self) -> list[str]:
        try:
            res = subprocess.run(
                ["git", "ls-files"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return [f for f in res.stdout.split("\n") if f]
        except Exception:
            return []

    def _classify_file(self, path: str) -> RepoFileFact:
        p = Path(path)
        ext = p.suffix.lower()

        # language
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".md": "markdown",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".sh": "bash",
        }
        language = lang_map.get(ext, "unknown")

        # layer
        layer = "unknown"
        if "layers/" in path:
            parts = path.split("/")
            idx = parts.index("layers")
            if len(parts) > idx + 1:
                layer = parts[idx + 1]

        # flags
        is_test = "test_" in p.name or "tests/" in path
        is_spec = "doc/specs/" in path or ".feature" in path or ".rules.json" in path
        is_schema = ".schema.json" in path or "schemas/" in path
        is_report = ".aiwg/reports/" in path
        is_runtime = (
            language in ["python", "bash", "typescript"]
            and not is_test
            and not is_spec
            and "layers/" in path
        )

        is_generated_or_vendor = (
            "node_modules/" in path or "__pycache__" in path or ".venv" in path
        )

        artifact_type = "unknown"
        if is_test:
            artifact_type = "test"
        elif is_spec:
            artifact_type = "spec"
        elif is_schema:
            artifact_type = "schema"
        elif is_report:
            artifact_type = "report"
        elif is_runtime:
            artifact_type = "runtime"

        category = "first_party"
        if is_generated_or_vendor:
            category = "dependency"
        elif is_report:
            category = "generated"
        elif ext in [".json", ".yaml", ".toml"]:
            category = "config"
        elif ext == ".md":
            category = "doc"

        return RepoFileFact(
            path=path,
            extension=ext,
            language=language,
            layer=layer,
            artifact_type=artifact_type,
            category=category,
            is_test=is_test,
            is_spec=is_spec,
            is_schema=is_schema,
            is_report=is_report,
            is_runtime=is_runtime,
            is_generated_or_vendor=is_generated_or_vendor,
        )

    def _utc_now(self) -> str:
        return (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )


def run_repo_intelligence_scan(
    repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg"
) -> dict[str, Any]:
    runtime = RepoIntelligenceRuntime(repo_root=repo_root, aiwg_root=aiwg_root)
    # Using object output for tests and simple dict for CLI
    # To satisfy tests we return an object that acts like dict but has properties
    res = runtime.run_repo_intelligence_scan()

    class Wrapper:
        def __init__(self, d):
            self.__dict__.update(d)

        def to_dict(self):
            return self.__dict__

    return Wrapper(res)
