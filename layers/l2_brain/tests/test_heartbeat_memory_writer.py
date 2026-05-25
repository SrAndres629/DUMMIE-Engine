from heartbeat.heartbeat_memory_writer import append_heartbeat_node_safe


def test_memory_write_failure_does_not_fail_heartbeat():
    status = append_heartbeat_node_safe(
        hb_id="hb-test",
        mode="advisory",
        result={"decision": "PASS"},
        max_attempts=1,
        timeout_ms=1,
    )
    assert status["success"] is False
    assert status["degraded"] is True
