from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from total_project_truth_scan import run_total_truth_scan
from lifecycle_integration_mapper import run_lifecycle_mapping
from source_of_truth_conflict_detector import run_conflict_detection
from context_coverage_auditor import run_context_audit
from sovereign_runtime_readiness import run_readiness_assessment
from memory_spine_bridge import run_memory_spine_sync


class OperationalizationPack2Runner:
    def __init__(self, repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg"):
        self.repo_root = Path(repo_root).resolve()
        self.aiwg_root = self.repo_root / aiwg_root
        self.reports_root = self.aiwg_root / "reports"

    def run_all(self) -> dict[str, Any]:
        print("Starting Operationalization Pack 2 Runner...")
        
        # 1. Truth Scan
        print("Running Total Project Truth Scan...")
        truth_scan = run_total_truth_scan(self.repo_root, self.aiwg_root)
        
        # 2. Lifecycle Mapping
        print("Running Lifecycle Integration Mapping...")
        lifecycle = run_lifecycle_mapping(self.repo_root, self.aiwg_root)
        
        # 3. Conflict Detection
        print("Running Source of Truth Conflict Detection...")
        conflicts = run_conflict_detection(self.repo_root, self.aiwg_root)
        
        # 4. Context Audit
        print("Running Context Coverage Audit...")
        context_audit = run_context_audit(self.repo_root, self.aiwg_root)
        
        # 5. Readiness Assessment
        print("Running Sovereign Runtime Readiness Assessment...")
        readiness = run_readiness_assessment(self.repo_root, self.aiwg_root)

        # 6. Memory Spine Sync
        print("Running Memory Spine Synchronization...")
        memory_sync = run_memory_spine_sync(self.repo_root, self.aiwg_root)
        
        summary = {
            "decision": "PASS" if readiness.get("decision") == "PASS" else "WARN",
            "generated_at": self._utc_now(),
            "results": {
                "truth_scan": truth_scan.get("decision"),
                "lifecycle": lifecycle.get("data_flow_integrity"),
                "conflicts": conflicts.get("conflict_count"),
                "context_audit": context_audit.get("decision"),
                "readiness_score": readiness.get("readiness_score"),
                "memory_sync": memory_sync.get("decision")
            }
        }
        
        (self.reports_root / "operationalization_pack_2_summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
        
        print(f"Pack 2 Complete. Readiness Score: {summary['results']['readiness_score']}")
        return summary

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    runner = OperationalizationPack2Runner()
    runner.run_all()
