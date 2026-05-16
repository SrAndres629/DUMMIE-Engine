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
        scores: list[ReadinessScore] = []

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

        # 4. Memory Coherence — consume Pack 3 data
        session_store = self.repo_root / "layers/l2_brain/session_store.py"
        kuzu_db = self.repo_root / ".aiwg/memory/loci.db"
        memory_spine_report = self._load_json("memory_spine_entrypoint_latest.json")
        memory_sync = self._load_json("memory_spine_sync_latest.json")

        # Priority: check sync report status first (runtime truth > file existence)
        if memory_sync.get("db_status") == "DEGRADED":
            scores.append(ReadinessScore("MEMORY_COHERENCE", 0.3, "PARTIAL",
                                         "Session store exists but Kuzu DEGRADED — file-backed memory only"))
        elif session_store.exists() and kuzu_db.exists():
            scores.append(ReadinessScore("MEMORY_COHERENCE", 1.0, "READY", "Operational memory linked to 4D-TES spine"))
        elif session_store.exists():
            scores.append(ReadinessScore("MEMORY_COHERENCE", 0.5, "PARTIAL", "Session store exists but Kuzu spine (loci.db) is missing"))
        else:
            scores.append(ReadinessScore("MEMORY_COHERENCE", 0.0, "NOT_READY", "Missing memory persistence layer"))

        # 5. Readiness Calibration — consume Pack 3 calibrator
        calibration = self._load_json("readiness_score_calibration_latest.json")
        if calibration:
            cal_scores = calibration.get("calibrated_scores", {})
            avg_cal = sum(cal_scores.values()) / max(1, len(cal_scores))
            norm = min(1.0, avg_cal / 10.0)
            if calibration.get("findings"):
                scores.append(ReadinessScore("CALIBRATED_READINESS", norm, "PARTIAL",
                                             f"Calibrated avg={avg_cal:.1f}/10, {len(calibration['findings'])} findings"))
            else:
                scores.append(ReadinessScore("CALIBRATED_READINESS", norm, "READY", "Calibrated readiness fully passing"))
        else:
            scores.append(ReadinessScore("CALIBRATED_READINESS", 0.0, "NOT_READY", "No readiness calibration report"))

        # 6. Token Economy — consume Pack 3 benchmark
        benchmark = self._load_json("token_economy_benchmark_latest.json")
        if benchmark:
            efficiency = benchmark.get("token_efficiency_score", 0)
            mtype = benchmark.get("measurement_type", "unknown")
            if mtype == "deterministic_estimate":
                scores.append(ReadinessScore("TOKEN_ECONOMY", min(1.0, efficiency / 100.0), "PARTIAL",
                                             f"Efficiency {efficiency}/100 (deterministic estimate, no live LLM measurement)"))
            else:
                scores.append(ReadinessScore("TOKEN_ECONOMY", min(1.0, efficiency / 100.0), "READY",
                                             f"Efficiency {efficiency}/100"))
        else:
            scores.append(ReadinessScore("TOKEN_ECONOMY", 0.0, "NOT_READY", "No token economy benchmark"))

        # 7. Entrypoint Enforcement — consume Pack 3 audit
        audit = self._load_json("entrypoint_enforcement_audit_latest.json")
        if audit:
            audits = audit.get("audits", [])
            using_spine = sum(1 for a in audits if a.get("uses_memory_spine"))
            total = len(audits) or 1
            ratio = using_spine / total
            if ratio >= 0.8:
                scores.append(ReadinessScore("ENTRYPOINT_ENFORCEMENT", ratio, "READY",
                                             f"{using_spine}/{total} entrypoints use memory spine"))
            else:
                scores.append(ReadinessScore("ENTRYPOINT_ENFORCEMENT", ratio, "PARTIAL",
                                             f"Only {using_spine}/{total} entrypoints use memory spine"))
        else:
            scores.append(ReadinessScore("ENTRYPOINT_ENFORCEMENT", 0.0, "NOT_READY", "No entrypoint enforcement audit"))

        total_score = sum(s.score for s in scores) / len(scores) if scores else 0.0

        report = {
            "decision": "PASS" if total_score >= 0.8 else "WARN",
            "readiness_score": round(total_score, 4),
            "components": [s.to_dict() for s in scores],
            "generated_at": self._utc_now()
        }

        # Write to both expected paths
        self.reports_root.mkdir(parents=True, exist_ok=True)
        report_json = json.dumps(report, indent=2) + "\n"
        (self.reports_root / "sovereign_readiness_latest.json").write_text(report_json, encoding="utf-8")
        (self.reports_root / "sovereign_runtime_readiness.json").write_text(report_json, encoding="utf-8")

        # MD version
        md = "# Sovereign Runtime Readiness Assessment\n\n"
        md += f"**Decision:** {report['decision']}\n"
        md += f"**Score:** {report['readiness_score']:.2%}\n"
        md += f"**Generated At:** {report['generated_at']}\n\n"
        md += "## Components\n\n"
        md += "| Component | Score | Status | Reason |\n"
        md += "| :--- | :--- | :--- | :--- |\n"
        for s in scores:
            md += f"| {s.component} | {s.score:.2f} | {s.status} | {s.reason} |\n"
        (self.reports_root / "sovereign_runtime_readiness.md").write_text(md, encoding="utf-8")

        return report

    def _load_json(self, filename: str) -> dict[str, Any]:
        path = self.reports_root / filename
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_readiness_assessment(repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    assessor = SovereignRuntimeReadiness(repo_root=repo_root, aiwg_root=aiwg_root)
    return assessor.run_assessment()


if __name__ == "__main__":
    report = run_readiness_assessment()
    print(json.dumps(report, indent=2))
