import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models import SixDimensionalContext, AgentIntent, AuthorityLevel, IntentType


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
