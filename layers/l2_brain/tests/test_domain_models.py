import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models import (
    SixDimensionalContext,
    AgentIntent,
    AuthorityLevel,
    IntentType,
    SourceArtifact,
    MemoryTemperatureSignal,
    IntentDraft,
    ConsensusDecision,
    RehydrationManifest,
    MemoryTemperature,
)


def test_six_dimensional_context_defaults():
    ctx = SixDimensionalContext()
    assert ctx.x == 0.0
    assert ctx.a == AuthorityLevel.READ
    assert ctx.i == IntentType.CONTEXT
    assert ctx.metadata == {}


def test_six_dimensional_context_metadata_is_isolated():
    ctx_a = SixDimensionalContext()
    ctx_b = SixDimensionalContext()

    ctx_a.metadata["trace_id"] = "T-001"

    assert ctx_b.metadata == {}
    assert ctx_a.metadata["trace_id"] == "T-001"


def test_agent_intent_defaults():
    intent = AgentIntent(agent_id="A-01", goal="Refactor daemon planner")
    assert intent.intent_type == IntentType.FABRICATION
    assert intent.constraints == []


def test_authority_and_intent_enums_are_stable():
    assert AuthorityLevel.ADMIN.value == "ADMIN"
    assert IntentType.REPAIR.value == "REPAIR"


def test_universal_knowledge_bus_models_are_provider_agnostic():
    artifact = SourceArtifact(
        provider="obsidian",
        source_uri="obsidian://Decisions/OBS-001.md",
        content_type="text/markdown",
        content="body",
        payload_hash="abc123abc123abc123",
        observed_at="2026-04-26T00:00:00Z",
        metadata={"path": "Decisions/OBS-001.md"},
    )
    assert artifact.provider == "obsidian"
    assert artifact.payload_hash.startswith("abc123")

    signal = MemoryTemperatureSignal(
        source_uri=artifact.source_uri,
        provider=artifact.provider,
        signal_type="manual_pin",
        weight=1.0,
        observed_at=artifact.observed_at,
    )
    assert signal.signal_type == "manual_pin"
    assert MemoryTemperature.HOT.value == "HOT"

    draft = IntentDraft(
        draft_id="draft-1",
        goal="Integrate provider",
        risk_level="high",
        proposed_steps=["write spec", "wait for review"],
        requires_human_review=True,
        target_file="Simulations/TASK-001.md",
    )
    assert draft.requires_human_review is True

    decision = ConsensusDecision(
        consensus_id="cons-1",
        topic="Knowledge bus",
        participants=["planner", "reviewer"],
        decision="Use provider-agnostic ports",
    )
    assert decision.dissent == []

    manifest = RehydrationManifest(
        manifest_id="rehydrate-1",
        source_provider="obsidian",
        scan_roots=["DUMMIE/Decisions"],
        artifact_kinds=["decision", "lesson"],
        mode="dry_run",
    )
    assert manifest.mode == "dry_run"
