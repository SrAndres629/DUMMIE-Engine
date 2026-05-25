from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def write_heartbeat_perf_report(
    aiwg_root: Path,
    heartbeat_id: str,
    mode: str,
    cycle_ms: int,
    phase_ms: Dict[str, int],
    skipped_phases: list[str],
    budget_decision: str,
) -> Dict[str, Any]:
    report = {
        "heartbeat_id": heartbeat_id,
        "mode": mode,
        "cycle_ms": int(cycle_ms),
        "phase_ms": dict(phase_ms),
        "skipped_phases": list(skipped_phases),
        "budget_decision": budget_decision,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    reports = aiwg_root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "heartbeat_perf_latest.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report
