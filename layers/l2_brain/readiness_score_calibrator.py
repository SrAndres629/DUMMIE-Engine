# Spec: 146_readiness_score_calibrator
# Spec: DE-V2-L2-146
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ReadinessCalibrationFinding:
    id: str
    severity: str  # LOW|MEDIUM|HIGH|CRITICAL
    description: str
    impact: str
    score_penalty: float


@dataclass
class ReadinessCalibrationReport:
    decision: str
    calibrated_scores: dict[str, float]
    findings: list[ReadinessCalibrationFinding]
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ReadinessScoreCalibrator:
    def __init__(self, repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg"):
        self.repo_root = Path(repo_root).resolve()
        self.aiwg_root = self.repo_root / aiwg_root
        self.reports_root = self.aiwg_root / "reports"

    def run_calibration(self) -> ReadinessCalibrationReport:
        findings: list[ReadinessCalibrationFinding] = []

        # 1. Detect overconfidence in Memory Readiness
        memory_sync = self._load_json("memory_spine_sync_latest.json")
        if memory_sync.get("db_status") == "DEGRADED":
            findings.append(ReadinessCalibrationFinding(
                "score_1_with_degraded_kuzu",
                "HIGH",
                "Kuzu/4D-TES persistence is DEGRADED. No physical graph writes occur.",
                "Memory Spine is logical-only. Causal retrieval depends on file parsing.",
                3.5
            ))

        # 2. Context Coverage Check
        coverage = self._load_json("context_coverage_latest.json")
        metrics = coverage.get("metrics", [])
        missing_tests = [m for m in metrics if m.get("category") == "TEST_PRESENCE" and m.get("status") == "MISSING"]
        if missing_tests:
            penalty = min(2.0, len(missing_tests) * 0.1)
            findings.append(ReadinessCalibrationFinding(
                "score_1_with_partial_context_coverage",
                "MEDIUM",
                f"Partial context coverage: {len(missing_tests)} missing runtime tests.",
                "Validation integrity is not absolute.",
                penalty
            ))

        # 3. Entrypoint Memory Retrieval Check
        chat_cli = self._load_json("dummie_chat_cli_latest.json")
        if not chat_cli.get("memory_spine") and not chat_cli.get("memory_spine_used", False):
            findings.append(ReadinessCalibrationFinding(
                "score_1_without_entrypoint_memory_retrieval",
                "HIGH",
                "DUMMIE Chat CLI does not retrieve causal memory before response.",
                "Chat remains stateless/amnesic despite memory spine availability.",
                4.0
            ))

        # 4. Token Benchmark Evidence Check
        if not (self.reports_root / "token_economy_benchmark_latest.json").exists():
            findings.append(ReadinessCalibrationFinding(
                "score_1_without_token_benchmark_evidence",
                "MEDIUM",
                "No empirical token economy benchmark exists.",
                "Context strategy ROI is asserted but not measured.",
                1.5
            ))

        # 5. Advisory-Only Capability Check
        scorecard = self._load_json("plan_v1_runtime_capability_scorecard.json")
        capabilities = scorecard.get("capabilities", [])
        advisory_only = [c for c in capabilities
                         if c.get("operational_mode") in ("advisory", "advisory_only", "dry_run")]
        if advisory_only:
            findings.append(ReadinessCalibrationFinding(
                "score_1_with_advisory_only_capability",
                "MEDIUM",
                f"{len(advisory_only)} capabilities operate in advisory-only mode.",
                "System cannot autonomously act; it can only recommend.",
                2.0
            ))

        # 6. Dry-Run-Only Capability Check
        dry_run_only = [c for c in capabilities
                        if c.get("operational_mode") in ("dry_run", "dry_run_only")]
        if dry_run_only:
            findings.append(ReadinessCalibrationFinding(
                "score_1_with_dry_run_only_capability",
                "MEDIUM",
                f"{len(dry_run_only)} capabilities operate in dry-run-only mode.",
                "No real mutations are executed; only simulated.",
                1.5
            ))

        # Calculate Calibrated Scores (0-10)
        base = 10.0

        memory_penalty = sum(f.score_penalty for f in findings if "memory" in f.id or "kuzu" in f.id)
        entrypoint_penalty = sum(f.score_penalty for f in findings if "entrypoint" in f.id)
        token_penalty = sum(f.score_penalty for f in findings if "token" in f.id)
        advisory_penalty = sum(f.score_penalty for f in findings if "advisory" in f.id or "dry_run" in f.id)
        total_penalty = sum(f.score_penalty for f in findings)

        memory_score = max(0.0, base - memory_penalty)
        entrypoint_score = max(0.0, base - entrypoint_penalty)
        token_score = max(0.0, base - token_penalty)
        autonomy_score = max(0.0, base - total_penalty - 2.0)  # Extra penalty for autonomous mutation

        calibrated_scores = {
            "daily_use_readiness": round(min(memory_score, entrypoint_score), 2),
            "memory_spine_readiness": round(memory_score, 2),
            "token_economy_readiness": round(token_score, 2),
            "entrypoint_sovereignty_readiness": round(entrypoint_score, 2),
            "autonomy_readiness": round(max(0.0, autonomy_score - advisory_penalty), 2)
        }

        report = ReadinessCalibrationReport(
            decision="PASS_WITH_WARNINGS" if findings else "PASS",
            calibrated_scores=calibrated_scores,
            findings=findings,
            generated_at=self._utc_now()
        )

        self._save_report(report)
        return report

    def _load_json(self, filename: str) -> dict[str, Any]:
        path = self.reports_root / filename
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_report(self, report: ReadinessCalibrationReport) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "readiness_score_calibration_latest.json").write_text(
            json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8"
        )

        # MD version
        md = "# Readiness Score Calibration Report\n\n"
        md += f"**Decision:** {report.decision}\n"
        md += f"**Generated At:** {report.generated_at}\n\n"
        md += "## Calibrated Scores (0-10)\n\n"
        for k, v in report.calibrated_scores.items():
            md += f"- **{k}:** {v:.2f}\n"

        md += "\n## Findings\n\n"
        for f in report.findings:
            md += f"### [{f.severity}] {f.id}\n"
            md += f"- **Description:** {f.description}\n"
            md += f"- **Impact:** {f.impact}\n"
            md += f"- **Penalty:** -{f.score_penalty}\n\n"

        (self.reports_root / "readiness_score_calibration_latest.md").write_text(md, encoding="utf-8")

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_readiness_score_calibration(repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg") -> ReadinessCalibrationReport:
    calibrator = ReadinessScoreCalibrator(repo_root=repo_root, aiwg_root=aiwg_root)
    return calibrator.run_calibration()


if __name__ == "__main__":
    report = run_readiness_score_calibration()
    print(json.dumps(report.to_dict(), indent=2))
