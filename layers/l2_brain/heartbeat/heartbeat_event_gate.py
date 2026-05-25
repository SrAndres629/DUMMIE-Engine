from __future__ import annotations

FORCED_EVENTS = {"user_command", "repair_result", "critical_alert"}
MIN_SPACING_S = 15


def should_run_heartbeat(
    event_type: str | None,
    now_ts: float,
    last_hb_ts: float,
    interval_s: int = 300,
) -> bool:
    if event_type in FORCED_EVENTS:
        return (now_ts - last_hb_ts) >= MIN_SPACING_S
    return (now_ts - last_hb_ts) >= interval_s
