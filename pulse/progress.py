"""Progress tracking — measurable outcomes for each pulse cycle.

Source of Truth: .aiwg/pulse/progress/
Traced: Each pulse creates pulse_YYYYMMDD_HHMMSS.json
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class PhaseResult:
    """Result of a single phase execution — immutably recorded."""

    phase_name: str
    status: str  # success, failed, skipped
    tokens_used: int
    duration_seconds: float
    output_summary: str
    artifacts_created: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class PulseResult:
    """Complete result of a pulse cycle — canonical truth artifact."""

    pulse_id: str
    started_at: str
    completed_at: Optional[str] = None
    phases: List[PhaseResult] = field(default_factory=list)
    overall_status: str = "running"
    measurable_progress: Dict[str, Any] = field(default_factory=dict)


class ProgressTracker:
    """Track and measure pulse progress with immutable JSON records."""

    def __init__(self, progress_dir: str):
        self.progress_dir = Path(progress_dir)
        self.progress_dir.mkdir(parents=True, exist_ok=True)

    def start_pulse(self, pulse_id: str) -> PulseResult:
        return PulseResult(pulse_id=pulse_id, started_at=datetime.now().isoformat())

    def add_phase_result(self, pulse_result: PulseResult, phase_result: PhaseResult):
        pulse_result.phases.append(phase_result)

    def complete_pulse(self, pulse_result: PulseResult, status: str = "completed"):
        pulse_result.completed_at = datetime.now().isoformat()
        pulse_result.overall_status = status
        self._save_pulse(pulse_result)

    def _save_pulse(self, result: PulseResult):
        filename = f"pulse_{result.pulse_id}.json"
        filepath = self.progress_dir / filename
        with open(filepath, "w") as f:
            json.dump(
                {
                    "pulse_id": result.pulse_id,
                    "started_at": result.started_at,
                    "completed_at": result.completed_at,
                    "overall_status": result.overall_status,
                    "phases": [
                        {
                            "phase_name": p.phase_name,
                            "status": p.status,
                            "tokens_used": p.tokens_used,
                            "duration_seconds": p.duration_seconds,
                            "output_summary": p.output_summary,
                            "artifacts_created": p.artifacts_created,
                            "errors": p.errors,
                        }
                        for p in result.phases
                    ],
                    "measurable_progress": result.measurable_progress,
                },
                f,
                indent=2,
            )

    def get_recent_pulses(self, count: int = 5) -> List[Dict[str, Any]]:
        pulses = []
        for filepath in sorted(self.progress_dir.glob("pulse_*.json"), reverse=True):
            with open(filepath) as f:
                pulses.append(json.load(f))
            if len(pulses) >= count:
                break
        return pulses

    def calculate_progress_metrics(self) -> Dict[str, Any]:
        pulses = self.get_recent_pulses(count=100)
        if not pulses:
            return {"total_pulses": 0, "success_rate": 0.0, "avg_tokens": 0}

        completed = [p for p in pulses if p["overall_status"] == "completed"]
        total_tokens = sum(
            sum(phase["tokens_used"] for phase in p["phases"]) for p in pulses
        )

        return {
            "total_pulses": len(pulses),
            "successful_pulses": len(completed),
            "success_rate": (len(completed) / len(pulses) if pulses else 0.0),
            "avg_tokens_per_pulse": (total_tokens / len(pulses) if pulses else 0),
            "total_tokens_consumed": total_tokens,
        }
