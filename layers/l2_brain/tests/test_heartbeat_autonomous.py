from heartbeat.heartbeat_autonomous import resolve_runtime_mode


def test_mode_active_when_recent_user_activity():
    mode = resolve_runtime_mode(last_user_event_s=5, cpu=0.2, queue_depth=0)
    assert mode == "active"


def test_mode_idle_when_no_recent_activity():
    mode = resolve_runtime_mode(last_user_event_s=900, cpu=0.2, queue_depth=0)
    assert mode == "idle"


def test_mode_degraded_under_high_load():
    mode = resolve_runtime_mode(last_user_event_s=20, cpu=0.95, queue_depth=20)
    assert mode == "degraded"
