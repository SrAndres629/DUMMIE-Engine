from dataclasses import asdict

from agent_office.models import (
    AgentSession,
    ContextPacket,
    DecisionRecord,
    EvidencePacket,
    RepoManifest,
    WorkRoom,
)


def test_repo_manifest_is_json_safe_contract():
    manifest = RepoManifest(
        repo_id="dummie-engine",
        root="/repo/dummie",
        memory_root=".aiwg",
        specs_root="doc/specs",
        trust_level="private",
        allowed_providers=["codex", "gemini"],
        default_orchestrator_model="codex-5.5",
    )

    assert asdict(manifest) == {
        "repo_id": "dummie-engine",
        "root": "/repo/dummie",
        "memory_root": ".aiwg",
        "specs_root": "doc/specs",
        "trust_level": "private",
        "allowed_providers": ["codex", "gemini"],
        "default_orchestrator_model": "codex-5.5",
    }


def test_workroom_defaults_to_open_and_tracks_scope():
    workroom = WorkRoom(
        workroom_id="wr_01",
        repo_id="dummie-engine",
        objective="Harden orchestration runtime",
        affected_paths=["layers/l2_brain/**"],
        related_specs=["doc/specs/41_semantic_fabric_indexer.md"],
    )

    assert workroom.status == "OPEN"
    assert workroom.agents == []
    assert workroom.decisions == []
    assert workroom.evidence == []


def test_agent_session_declares_provider_role_and_permissions():
    session = AgentSession(
        session_id="sess_01",
        repo_id="dummie-engine",
        workroom_id="wr_01",
        role="contradictor",
        provider="gemini",
        model="gemini-flash",
        can_edit=False,
        allowed_paths=["layers/l2_brain/**"],
        context_packet_id="ctx_01",
        expected_output="evidence_review",
    )

    assert session.status == "OPEN"
    assert session.can_edit is False
    assert session.provider == "gemini"


def test_context_packet_carries_scoped_context_not_full_repo():
    packet = ContextPacket(
        context_packet_id="ctx_01",
        repo_id="dummie-engine",
        workroom_id="wr_01",
        role="researcher",
        task="Find the real contract failure",
        constraints=["Do not edit files"],
        files=["layers/l2_brain/daemon.py"],
        specs=["doc/specs/05_orchestration_stack_and_glue.md"],
        memory_refs=["mem_01"],
        output_schema="agent_research_report_v1",
    )

    assert packet.constraints == ["Do not edit files"]
    assert packet.files == ["layers/l2_brain/daemon.py"]
    assert packet.output_schema == "agent_research_report_v1"


def test_evidence_packet_requires_verification_before_truth():
    evidence = EvidencePacket(
        evidence_id="ev_01",
        repo_id="dummie-engine",
        workroom_id="wr_01",
        producer_session_id="sess_01",
        claim="MCPDriver lacks execute",
        evidence=["layers/l5_muscle/mcp_driver.py:14"],
        confidence=0.91,
    )

    assert evidence.verification_status == "PENDING"


def test_decision_record_links_approved_decision_to_evidence():
    decision = DecisionRecord(
        decision_id="dec_01",
        repo_id="dummie-engine",
        workroom_id="wr_01",
        decision="Expose execute as executor contract",
        rationale="L2 should depend on behavior, not L5 transport naming",
        approved_by="orchestrator",
        evidence_ids=["ev_01"],
        status="APPROVED",
    )

    assert decision.evidence_ids == ["ev_01"]
    assert decision.status == "APPROVED"
