import json
from dataclasses import asdict
from unittest.mock import MagicMock

from layers.l2_brain.daemon.daemon import DummieDaemon
from layers.l2_brain.daemon_outcome import (
    DaemonOutcome,
    EfficiencyMetrics,
    MetacognitionStatus,
    ModelRouteMetadata,
    NextAction,
    RecoveryHint,
    SensorFirstStatus,
    TestExecutionSummary,
)
from layers.l2_brain.infrastructure.event_bus import AsyncEventBus
from layers.l2_brain.infrastructure.gateway_contract import SagaTransaction
from layers.l2_brain.models import AuthorityLevel, IntentType


def test_daemon_outcome_serializes_required_contract_fields():
    outcome = DaemonOutcome(
        outcome_id="outcome-1",
        status="SUCCESS",
        session_id="session-1",
        mission_id="mission-1",
        phase_id="phase-1",
        transaction_id="txn-1",
        context_token="ctx-1",
        authority_level="OVERSEER",
        intent_type="MUTATION",
        model_route=ModelRouteMetadata(
            tier="local_fast",
            provider="ollama",
            reason="hook_authority=OVERSEER",
            hook_metadata={"authority_level": "OVERSEER"},
        ),
        metacognition=MetacognitionStatus(
            status="READY",
            enabled_hooks=["AuthorityClassifierHook"],
        ),
        sensor_first=SensorFirstStatus(mode="WARN", decision="ALLOW", reason="all_guards_passed"),
        efficiency=EfficiencyMetrics(
            input_tokens=100,
            cached_tokens=20,
            output_tokens=30,
            estimated_direct_tokens=1000,
            estimated_gateway_tokens=500,
            token_reduction_ratio=0.5,
            measurement_type="estimated",
        ),
        tests=TestExecutionSummary(commands=["pytest"], passed=1, failed=0),
        evidence_refs=["pytest://daemon_outcome"],
        next_action=NextAction(recommended="continue", reason="contract serialized"),
        recovery_hint=RecoveryHint(can_resume=True, resume_from="phase-1"),
        learning_episode_ref="episode-1",
    )

    payload = outcome.to_dict()
    encoded = outcome.to_json()
    decoded = json.loads(encoded)

    assert payload["mission_id"] == "mission-1"
    assert payload["phase_id"] == "phase-1"
    assert payload["model_route"]["tier"] == "local_fast"
    assert payload["metacognition"]["status"] == "READY"
    assert decoded["recovery_hint"]["can_resume"] is True


def test_daemon_outcome_rejects_private_chain_of_thought_evidence():
    outcome = DaemonOutcome(
        outcome_id="outcome-2",
        status="SUCCESS",
        evidence_refs=[
            "public-report",
            "chain_of_thought://private",
            "private reasoning note",
        ],
        next_action=NextAction(recommended="continue", reason="public evidence only"),
    )

    payload = outcome.to_json()

    assert "public-report" in payload
    assert "chain_of_thought" not in payload.lower()
    assert "private reasoning" not in payload.lower()


def test_daemon_outcome_dataclass_defaults_are_serializable():
    outcome = DaemonOutcome(outcome_id="outcome-3", status="DEGRADED")

    payload = asdict(outcome)

    assert payload["status"] == "DEGRADED"
    assert payload["model_route"]["hook_metadata"] == {}
    assert payload["tests"]["commands"] == []


def test_daemon_outcome_rejects_noncanonical_authority_and_intent():
    try:
        DaemonOutcome(outcome_id="outcome-4", status="SUCCESS", authority_level="A1_OPERATOR")
    except ValueError as exc:
        assert "authority_level" in str(exc)
    else:
        raise AssertionError("noncanonical authority_level should fail")

    try:
        DaemonOutcome(outcome_id="outcome-5", status="SUCCESS", intent_type="WRITE")
    except ValueError as exc:
        assert "intent_type" in str(exc)
    else:
        raise AssertionError("noncanonical intent_type should fail")


def test_daemon_exposes_outcome_builder_with_mission_phase():
    daemon = DummieDaemon(
        ledger_path="dummy_ledger.json",
        mcp_gateway=MagicMock(),
        event_bus=MagicMock(spec=AsyncEventBus),
    )
    saga = SagaTransaction(transaction_id="tx-daemon", context_token="ctx", steps=[])

    outcome = daemon._build_outcome(
        status="SUCCESS",
        transaction_id="tx-daemon",
        saga=saga,
        mission_id="mission-1",
        phase_id="phase-1",
        authority_level=AuthorityLevel.AGENT,
        intent_type=IntentType.MUTATION,
    )

    assert daemon.outcome_contract_available is True
    assert outcome["mission_id"] == "mission-1"
    assert outcome["phase_id"] == "phase-1"
    assert outcome["authority_level"] == "AGENT"
    assert outcome["intent_type"] == "MUTATION"
    assert outcome["next_action"]["recommended"] == "continue"
