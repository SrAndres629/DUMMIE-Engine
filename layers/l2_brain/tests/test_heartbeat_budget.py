from heartbeat.heartbeat_budget import HeartbeatBudget


def test_budget_exhaustion_marks_cycle_warn():
    budget = HeartbeatBudget(max_ms=200, max_io_ops=20)
    budget.consume_ms(220)
    assert budget.decision() == "WARN"
