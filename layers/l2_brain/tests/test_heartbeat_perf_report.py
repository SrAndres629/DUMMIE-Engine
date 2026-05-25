import tempfile
from pathlib import Path

from heartbeat.heartbeat_perf_report import write_heartbeat_perf_report


def test_write_heartbeat_perf_report_schema():
    tmp = Path(tempfile.mkdtemp())
    aiwg = tmp / ".aiwg"
    out = write_heartbeat_perf_report(
        aiwg_root=aiwg,
        heartbeat_id="hb-123",
        mode="active",
        cycle_ms=120,
        phase_ms={"observe": 20},
        skipped_phases=["metacognitive_loop"],
        budget_decision="ALLOW",
    )
    assert out["heartbeat_id"] == "hb-123"
    assert out["mode"] == "active"
    assert out["budget_decision"] == "ALLOW"
    assert (aiwg / "reports" / "heartbeat_perf_latest.json").exists()
