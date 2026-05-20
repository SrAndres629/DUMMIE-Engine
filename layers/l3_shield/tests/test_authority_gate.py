import pytest
from layers.l3_shield.authority_gate import AuthorityGate
from layers.l2_brain.metacognition.contracts import MetacognitiveFrame, AuthorityLevel

@pytest.mark.asyncio
async def test_authority_gate_overseer_sovereign():
    gate = AuthorityGate()
    # MANDATO SOBERANO: OVERSEER ahora tiene permiso de escritura
    frame = MetacognitiveFrame(session_id="s1", raw_user_input="refactor L0", authority_level=AuthorityLevel.OVERSEER)
    
    authorized, msg = await gate.validate_intent(frame)
    assert authorized is True
    assert "SVRN_CONFIRM" in msg

@pytest.mark.asyncio
async def test_authority_gate_architect_sovereign():
    gate = AuthorityGate()
    # MANDATO SOBERANO: ARCHITECT ahora tiene permiso de escritura
    frame = MetacognitiveFrame(session_id="s2", raw_user_input="mutación topológica", authority_level=AuthorityLevel.ARCHITECT)
    
    authorized, msg = await gate.validate_intent(frame)
    assert authorized is True
    assert "SVRN_CONFIRM" in msg

@pytest.mark.asyncio
async def test_authority_gate_engineer_sovereign():
    gate = AuthorityGate()
    frame = MetacognitiveFrame(session_id="s3", raw_user_input="crea archivo", authority_level=AuthorityLevel.ENGINEER)
    
    authorized, msg = await gate.validate_intent(frame)
    assert authorized is True
    assert "SVRN_CONFIRM" in msg

@pytest.mark.asyncio
async def test_authority_gate_unspecified_veto():
    gate = AuthorityGate()
    # Niveles desconocidos o no autorizados siguen vetados
    frame = MetacognitiveFrame(session_id="s4", raw_user_input="acción random", authority_level=AuthorityLevel.UNSPECIFIED)
    
    authorized, msg = await gate.validate_intent(frame)
    assert authorized is False
    assert "VETO_L3" in msg
