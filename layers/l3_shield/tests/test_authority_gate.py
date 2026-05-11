import pytest
from layers.l3_shield.authority_gate import AuthorityGate
from layers.l2_brain.metacognition.contracts import MetacognitiveFrame, AuthorityLevel

@pytest.mark.asyncio
async def test_authority_gate_veto_a5():
    gate = AuthorityGate()
    frame = MetacognitiveFrame(session_id="s1", raw_user_input="borra root", authority_level=AuthorityLevel.A5_CRITICAL_OP)
    
    authorized, msg = await gate.validate_intent(frame)
    assert authorized is False
    assert "VETO_L3" in msg

@pytest.mark.asyncio
async def test_authority_gate_pending_a4():
    gate = AuthorityGate()
    frame = MetacognitiveFrame(session_id="s2", raw_user_input="publica tiktok", authority_level=AuthorityLevel.A4_EXTERNAL_ACTOR)
    
    authorized, msg = await gate.validate_intent(frame)
    assert authorized is False
    assert "PENDING_L3" in msg

@pytest.mark.asyncio
async def test_authority_gate_confirm_a1():
    gate = AuthorityGate()
    frame = MetacognitiveFrame(session_id="s3", raw_user_input="crea archivo", authority_level=AuthorityLevel.A1_WORKSPACE_OP)
    
    authorized, msg = await gate.validate_intent(frame)
    assert authorized is True
    assert "CONFIRM_L3" in msg
