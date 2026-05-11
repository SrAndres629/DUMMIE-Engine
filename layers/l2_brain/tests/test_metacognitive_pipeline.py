import pytest
import asyncio
from metacognition.pipeline import MetacognitivePipeline
from metacognition.input_hooks import IntentClarifierHook, AuthorityClassifierHook
from metacognition.deliberation_hooks import MissionDecomposerHook, PlanCriticHook
from metacognition.output_hooks import AnswerVerifierHook, MemoryUpdateHook
from metacognition.contracts import AuthorityLevel

@pytest.mark.asyncio
async def test_metacognitive_pipeline_full_flow():
    pipeline = MetacognitivePipeline(
        input_hooks=[IntentClarifierHook(), AuthorityClassifierHook()],
        deliberation_hooks=[MissionDecomposerHook(), PlanCriticHook()],
        output_hooks=[AnswerVerifierHook(), MemoryUpdateHook()]
    )
    
    # Test case 1: Automation request (High authority)
    frame = await pipeline.preprocess("test_session_1", "Quiero automatizar mi contenido de TikTok")
    assert frame.refined_intent == "OBJECTIVE_AUTOMATION"
    assert frame.authority_level == AuthorityLevel.A4_EXTERNAL_ACTOR
    
    frame = await pipeline.deliberate(frame)
    assert len(frame.mission_plan) > 0
    assert "ResearchAgent" in frame.mission_plan[0]["agent"]
    
    frame = await pipeline.postprocess(frame, "Listo, plan de automatización creado.")
    assert "Output length verified" in frame.verification_findings[0]
    assert frame.telemetry["memory_synced"] is True

@pytest.mark.asyncio
async def test_authority_classification_critical():
    hook = AuthorityClassifierHook()
    pipeline = MetacognitivePipeline(input_hooks=[hook])
    
    frame = await pipeline.preprocess("test_session_2", "Borra todo el sistema root")
    assert frame.authority_level == AuthorityLevel.A5_CRITICAL_OP

@pytest.mark.asyncio
async def test_authority_classification_workspace():
    hook = AuthorityClassifierHook()
    pipeline = MetacognitivePipeline(input_hooks=[hook])
    
    frame = await pipeline.preprocess("test_session_3", "Crea un archivo de notas")
    assert frame.authority_level == AuthorityLevel.A1_WORKSPACE_OP
