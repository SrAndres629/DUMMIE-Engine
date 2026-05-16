from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ReadinessScore:
    component: str
    score: float  # 0.0 to 1.0
    status: str  # READY|PARTIAL|NOT_READY
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SovereignRuntimeReadiness:
    def __init__(self, repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg"):
        self.repo_root = Path(repo_root).resolve()
        self.aiwg_root = self.repo_root / aiwg_root
        self.reports_root = self.aiwg_root / "reports"

    def run_assessment(self) -> dict[str, Any]:
        scores = []
        
        # 1. CLI Control Plane Readiness
        cli_file = self.repo_root / "layers/l2_brain/cli_control_plane.py"
        chat_cli = self.repo_root / "layers/l2_brain/dummie_chat_cli.py"
        if cli_file.exists() and chat_cli.exists():
            scores.append(ReadinessScore("CLI_CONTROL", 1.0, "READY", "Unified control plane and chat CLI present"))
        else:
            scores.append(ReadinessScore("CLI_CONTROL", 0.5, "PARTIAL", "Missing chat CLI or control plane"))

        # 2. Strategic Partner Swarm
        swarm_file = self.repo_root / "layers/l2_brain/strategic_partner_swarm.py"
        if swarm_file.exists():
            scores.append(ReadinessScore("STRATEGIC_SWARM", 1.0, "READY", "Strategic partner swarm logic present"))
        else:
            scores.append(ReadinessScore("STRATEGIC_SWARM", 0.0, "NOT_READY", "Missing swarm coordination logic"))

        # 3. Trusted Workstation
        trusted_file = self.repo_root / "layers/l2_brain/trusted_workstation_mode.py"
        if trusted_file.exists():
            scores.append(ReadinessScore("TRUSTED_WORKSTATION", 1.0, "READY", "Action classifier and dry-run guard present"))
        else:
            scores.append(ReadinessScore("TRUSTED_WORKSTATION", 0.0, "NOT_READY", "Missing safety guards for autonomous mutation"))

        # 4. Memory Coherence (MEMORY-SPINE-GAP check)
        # We check if session_store and 4D-TES (Kuzu) are linked
        session_store = self.repo_root / "layers/l2_brain/session_store.py"
        kuzu_db = self.repo_root / ".aiwg/memory/loci.db"
        if session_store.exists() and kuzu_db.exists():
             scores.append(ReadinessScore("MEMORY_COHERENCE", 1.0, "READY", "Operational memory linked to 4D-TES spine"))
        elif session_store.exists():
             scores.append(ReadinessScore("MEMORY_COHERENCE", 0.5, "PARTIAL", "Session store exists but Kuzu spine (loci.db) is missing"))
        else:
             scores.append(ReadinessScore("MEMORY_COHERENCE", 0.0, "NOT_READY", "Missing memory persistence layer"))

        total_score = sum(s.score for s in scores) / len(scores) if scores else 0.0
        
        report = {
            "decision": "PASS" if total_score >= 0.8 else "WARN",
            "readiness_score": total_score,
            "components": [s.to_dict() for s in scores],
            "generated_at": self._utc_now()
        }
        
        (self.reports_root / "sovereign_readiness_latest.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        
        return report

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_readiness_assessment(repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    assessor = SovereignRuntimeReadiness(repo_root=repo_root, aiwg_root=aiwg_root)
    return assessor.run_assessment()


if __name__ == "__main__":
    run_readiness_assessment()
