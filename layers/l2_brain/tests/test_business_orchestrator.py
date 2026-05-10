from business_orchestrator import BusinessSolutionOrchestrator


def test_business_orchestrator_creates_business_session_and_artifacts(tmp_path):
    orchestrator = BusinessSolutionOrchestrator(tmp_path)

    session = orchestrator.start_business_session(
        "biz-1",
        {"prompt": "Launch a runtime MVP for session planning.", "authority_a": "HUMAN"},
    )
    package = orchestrator.create_solution_package(
        "biz-1",
        market="developer tools",
        users=["engineering lead"],
    )
    next_loop = orchestrator.propose_next_loop("biz-1")

    assert session["state"]["session_type"] == "business_solution"
    assert package["mission"]["goal"] == "Launch a runtime MVP for session planning."
    assert next_loop["artifact"] == "next_loop.md"

    loaded = orchestrator.store.load_session("biz-1")
    expected = {
        "business_brief.md",
        "prd.md",
        "architecture.md",
        "backlog.md",
        "validation_plan.md",
        "risk_register.md",
        "next_loop.md",
    }
    assert expected.issubset(set(loaded["artifacts"]))
