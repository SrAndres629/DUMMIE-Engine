from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class Conflict:
    type: str  # STALE_REPORT|DATA_MISMATCH|MISSING_LINK
    severity: str  # LOW|MEDIUM|HIGH|CRITICAL
    description: str
    affected_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SourceOfTruthConflictDetector:
    def __init__(self, repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg"):
        self.repo_root = Path(repo_root).resolve()
        self.aiwg_root = self.repo_root / aiwg_root
        self.reports_root = self.aiwg_root / "reports"
        self.max_age_hours = 24

    def run_detection(self) -> dict[str, Any]:
        conflicts = []
        
        # 1. Check for stale reports
        reports = list(self.reports_root.glob("*.json"))
        now = datetime.now(timezone.utc)
        
        for report_path in reports:
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Handle both dict and list
                gen_at_str = None
                if isinstance(data, dict):
                    gen_at_str = data.get("generated_at")
                elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                    # Lists usually don't have generated_at at top level, but some might have it in the first element
                    gen_at_str = data[0].get("generated_at")
                
                if gen_at_str:
                    try:
                        gen_at = datetime.fromisoformat(gen_at_str.replace("Z", "+00:00"))
                        age = now - gen_at
                        if age.total_seconds() > self.max_age_hours * 3600:
                            conflicts.append(Conflict(
                                "STALE_REPORT",
                                "MEDIUM",
                                f"Report {report_path.name} is older than {self.max_age_hours} hours",
                                [str(report_path.relative_to(self.repo_root))]
                            ))
                    except ValueError:
                         pass # Skip if date format is invalid
            except Exception as exc:
                conflicts.append(Conflict(
                    "REPORT_PARSE_ERROR",
                    "HIGH",
                    f"Failed to parse report {report_path.name}: {exc}",
                    [str(report_path.relative_to(self.repo_root))]
                ))

        # 2. Roadmap Contradiction Detection
        roadmap_path = self.reports_root / "systemic_refactor_roadmap.json"
        if roadmap_path.exists():
            try:
                with open(roadmap_path, "r", encoding="utf-8") as f:
                    roadmap = json.load(f)
                
                if isinstance(roadmap, list):
                    for item in roadmap:
                        component = item.get("component")
                        status = item.get("current_state")
                        if status == "missing" and component:
                            # Heuristic: check if a file with similar name exists in l2_brain
                            snake_name = component.lower()
                            # Convert CamelCase to snake_case for file names
                            snake_name = "".join(["_" + c.lower() if c.isupper() else c for c in component]).lstrip("_")
                            
                            candidates = [
                                self.repo_root / f"layers/l2_brain/{snake_name}.py",
                                self.repo_root / f"layers/l2_brain/{component.lower()}.py"
                            ]
                            
                            if any(c.exists() for c in candidates):
                                conflicts.append(Conflict(
                                    "ROADMAP_CONTRADICTION",
                                    "HIGH",
                                    f"Roadmap claims {component} is missing, but implementation file exists",
                                    [str(roadmap_path.relative_to(self.repo_root))]
                                ))
            except Exception as exc:
                conflicts.append(Conflict("ROADMAP_AUDIT_FAIL", "MEDIUM", str(exc)))

        # 3. Check for missing critical reports
        critical_reports = [
            "repo_intelligence_latest.json",
            "total_truth_scan_latest.json",
            "lifecycle_integration_latest.json"
        ]
        for cr in critical_reports:
            if not (self.reports_root / cr).exists():
                conflicts.append(Conflict(
                    "MISSING_CRITICAL_REPORT",
                    "HIGH",
                    f"Critical report {cr} is missing from reports folder",
                    []
                ))

        report = {
            "decision": "PASS" if not conflicts else "WARN",
            "conflict_count": len(conflicts),
            "conflicts": [c.to_dict() for c in conflicts],
            "generated_at": self._utc_now()
        }
        
        (self.reports_root / "source_of_truth_conflicts_latest.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        
        return report

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_conflict_detection(repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    detector = SourceOfTruthConflictDetector(repo_root=repo_root, aiwg_root=aiwg_root)
    return detector.run_detection()


if __name__ == "__main__":
    run_conflict_detection()
