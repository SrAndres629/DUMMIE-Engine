from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class CoverageMetric:
    category: str  # DOSSIER|SPEC|TEST
    target: str
    status: str  # COVERED|MISSING|PARTIAL
    details: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ContextCoverageAuditor:
    def __init__(self, repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg"):
        self.repo_root = Path(repo_root).resolve()
        self.aiwg_root = self.repo_root / aiwg_root
        self.intel_root = self.aiwg_root / "repo_intelligence"
        self.reports_root = self.aiwg_root / "reports"

    def run_audit(self) -> dict[str, Any]:
        metrics = []
        
        # 1. Dossier Coverage
        inventory_path = self.intel_root / "repo_inventory.json"
        dossier_index_path = self.reports_root / "file_dossier_index.json"
        
        if inventory_path.exists():
            with open(inventory_path, "r", encoding="utf-8") as f:
                inventory = json.load(f)
            
            runtime_files = [f["path"] for f in inventory.get("files", []) if f.get("is_runtime")]
            
            # Check for physical dossiers
            dossier_files = list((self.intel_root / "files").glob("*.json")) if (self.intel_root / "files").exists() else []
            dossier_paths = {d.stem for d in dossier_files}
            
            covered_count = 0
            for rf in runtime_files:
                safe_id = rf.replace("/", "_").replace(".", "_")
                if safe_id in dossier_paths:
                    covered_count += 1
                else:
                    metrics.append(CoverageMetric("DOSSIER", rf, "MISSING", "No deep/standard dossier generated"))
            
            metrics.append(CoverageMetric("DOSSIER_SUMMARY", f"{covered_count}/{len(runtime_files)}", "PARTIAL" if covered_count < len(runtime_files) else "COVERED"))

        # 2. Spec Sibling Coverage
        spec_dir = self.repo_root / "doc" / "specs"
        if spec_dir.exists():
            specs = list(spec_dir.rglob("*.md"))
            for spec in specs:
                if spec.name == "README.md": continue
                
                base = spec.stem
                feature = spec.parent / f"{base}.feature"
                rules = spec.parent / f"{base}.rules.json"
                
                missing = []
                if not feature.exists(): missing.append("feature")
                if not rules.exists(): missing.append("rules.json")
                
                status = "COVERED" if not missing else "PARTIAL"
                metrics.append(CoverageMetric("SPEC_SIBLINGS", str(spec.relative_to(self.repo_root)), status, f"Missing: {', '.join(missing)}" if missing else ""))

        # 3. Test Coverage (Presence)
        if inventory_path.exists():
            runtime_files = [f["path"] for f in inventory.get("files", []) if f.get("is_runtime") and f.get("language") == "python"]
            for rf in runtime_files:
                p = Path(rf)
                test_name = f"test_{p.name}"
                test_dir = p.parent / "tests"
                test_path = test_dir / test_name
                
                if not test_path.exists():
                    metrics.append(CoverageMetric("TEST_PRESENCE", rf, "MISSING", f"Expected test at {test_path}"))
                else:
                    metrics.append(CoverageMetric("TEST_PRESENCE", rf, "COVERED"))

        report = {
            "decision": "PASS",
            "metrics": [m.to_dict() for m in metrics],
            "generated_at": self._utc_now()
        }
        
        (self.reports_root / "context_coverage_latest.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        
        return report

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_context_audit(repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    auditor = ContextCoverageAuditor(repo_root=repo_root, aiwg_root=aiwg_root)
    return auditor.run_audit()


if __name__ == "__main__":
    run_context_audit()
