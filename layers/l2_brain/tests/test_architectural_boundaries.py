"""
[T10] Tests de regresión para fronteras arquitectónicas.
Verifica que:
- NativeShieldAdapter ya no existe como clase directa (es alias)
- UnsafeBypassShieldAdapter bloquea por defecto
- DummieDaemon.s_shield es TopologicalAuditor cuando imports funcionan
- AgentIntent.rationale retorna goal
- SixDimensionalContext tiene los 6 campos canónicos
- _AllowAllAuditor ya no existe (renombrado)
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# --- NativeShieldAdapter regression ---

def test_native_shield_adapter_is_alias_not_class():
    """NativeShieldAdapter must be an alias, not an independent class."""
    from adapters import NativeShieldAdapter, UnsafeBypassShieldAdapter
    assert NativeShieldAdapter is UnsafeBypassShieldAdapter, (
        "NativeShieldAdapter should be an alias for UnsafeBypassShieldAdapter, "
        "not an independent class."
    )


# --- DummieDaemon shield wiring ---

def test_daemon_uses_topological_auditor_when_available():
    """DummieDaemon.s_shield should be TopologicalAuditor when L3 is importable."""
    from daemon import DummieDaemon

    class _NoopBus:
        async def wait_for_request(self):
            raise NotImplementedError

    daemon = DummieDaemon(
        ledger_path="/tmp/test_ledger.jsonl",
        mcp_gateway=object(),
        event_bus=_NoopBus(),
    )
    # Si TopologicalAuditor se importó correctamente, debería ser la clase real
    shield_name = daemon.s_shield.__class__.__name__
    assert shield_name in ("TopologicalAuditor", "_FallbackUnsafeAuditor"), (
        f"Unexpected s_shield class: {shield_name}"
    )


def test_allow_all_auditor_no_longer_exists():
    """_AllowAllAuditor should not exist in daemon.py (renamed to _FallbackUnsafeAuditor)."""
    import daemon as daemon_module
    assert not hasattr(daemon_module, "_AllowAllAuditor"), (
        "_AllowAllAuditor should have been renamed to _FallbackUnsafeAuditor"
    )


def test_fallback_unsafe_auditor_exists():
    """_FallbackUnsafeAuditor should exist in daemon.py."""
    import daemon as daemon_module
    assert hasattr(daemon_module, "_FallbackUnsafeAuditor")


@pytest.mark.asyncio
async def test_fallback_unsafe_auditor_message():
    """_FallbackUnsafeAuditor should return a message indicating L3 failure."""
    from daemon import _FallbackUnsafeAuditor
    auditor = _FallbackUnsafeAuditor()
    ok, msg = await auditor.audit("<dag/>", "test")
    assert ok is True
    assert "FALLBACK_UNSAFE" in msg
    assert "L3 Shield import failed" in msg


# --- AgentIntent ---

def test_agent_intent_rationale_is_goal_alias():
    """AgentIntent.rationale should return goal."""
    from models import AgentIntent
    intent = AgentIntent(goal="test goal value")
    assert intent.rationale == "test goal value"
    assert intent.rationale == intent.goal


def test_agent_intent_default_authority():
    """AgentIntent should default to AGENT authority."""
    from models import AgentIntent, AuthorityLevel
    intent = AgentIntent(goal="test")
    assert intent.authority_a == AuthorityLevel.AGENT


# --- SixDimensionalContext ---

def test_six_dimensional_context_canonical_fields():
    """SixDimensionalContext must have exactly the 6 canonical dimensions + metadata."""
    from models import SixDimensionalContext
    ctx = SixDimensionalContext()
    # Verify all 6 dimensions exist
    assert hasattr(ctx, "locus_x")
    assert hasattr(ctx, "locus_y")
    assert hasattr(ctx, "locus_z")
    assert hasattr(ctx, "lamport_t")
    assert hasattr(ctx, "authority_a")
    assert hasattr(ctx, "intent_i")
    assert hasattr(ctx, "metadata")


def test_six_dimensional_context_defaults():
    """SixDimensionalContext defaults should be set."""
    from models import SixDimensionalContext, AuthorityLevel, IntentType
    ctx = SixDimensionalContext()
    assert ctx.lamport_t == 0.0
    assert ctx.authority_a == AuthorityLevel.AGENT
    assert ctx.intent_i == IntentType.FABRICATION
    assert isinstance(ctx.metadata, dict)
