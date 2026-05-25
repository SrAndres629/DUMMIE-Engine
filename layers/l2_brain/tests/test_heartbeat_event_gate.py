from heartbeat.heartbeat_event_gate import should_run_heartbeat


def test_tick_allowed_on_high_priority_event():
    assert should_run_heartbeat(
        event_type="user_command", now_ts=1000, last_hb_ts=980, interval_s=300
    )


def test_tick_skipped_without_event_and_within_interval():
    assert not should_run_heartbeat(
        event_type=None, now_ts=1000, last_hb_ts=980, interval_s=300
    )
