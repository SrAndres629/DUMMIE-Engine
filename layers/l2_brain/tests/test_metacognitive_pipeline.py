import pytest
import asyncio
from metacognition.pipeline import MetacognitivePipeline
from metacognition.input_hooks import IntentClarifierHook, AuthorityClassifierHook
from metacognition.deliberation_hooks import MissionDecomposerHook, PlanCriticHook
from metacognition.output_hooks import AnswerVerifierHook, MemoryUpdateHook
from metacognition.contracts import AuthorityLevel

@pytest.mark.asyncio
async def test_metacognitive_pipeline_full_flow():
    from unittest.mock import AsyncMock, MagicMock
    mock_daemon = MagicMock()
    mock_daemon.reason_with_tiers = AsyncMock(return_value='{"steps": []}')
    
    from metacognition.semantic_hooks import SemanticToolSelectorHook
    from metacognition.reasoning_hooks import ReasoningExpansionHook

    pipeline = MetacognitivePipeline(
        input_hooks=[
            IntentClarifierHook(), 
            AuthorityClassifierHook(),
            SemanticToolSelectorHook(None)
        ],
        deliberation_hooks=[
            ReasoningExpansionHook(mock_daemon),
            MissionDecomposerHook(mock_daemon), 
            PlanCriticHook()
        ],
        output_hooks=[AnswerVerifierHook(), MemoryUpdateHook()]
    )
    
    # Test case 1: Automation request (High authority)
    frame = await pipeline.preprocess("test_session_1", "Quiero automatizar mi contenido de TikTok")
    assert frame.refined_intent == "OBJECTIVE_AUTOMATION"
    assert frame.authority_level == AuthorityLevel.A4_EXTERNAL_ACTOR
    
    # Mock LLM response for decomposer
    mock_daemon.reason_with_tiers.side_effect = [
        "Razonamiento profundo sobre TikTok...", # Expansion
        '[{"step": 1, "agent": "ResearchAgent", "action": "Investigate TikTok APIs"}]' # Decomposition
    ]
    
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


@pytest.mark.asyncio
async def test_pipeline_records_hook_failures_in_frame_telemetry():
    class BrokenHook:
        async def run(self, frame):
            raise RuntimeError("boom")

    pipeline = MetacognitivePipeline(input_hooks=[BrokenHook(), IntentClarifierHook()])

    frame = await pipeline.preprocess("test_session_4", "Analiza el sistema")

    assert frame.refined_intent == "OBJECTIVE_INQUIRY"
    assert frame.risk_level == "degraded"
    assert frame.telemetry["hook_failures"][0]["hook"] == "BrokenHook"
    assert "boom" in frame.telemetry["hook_failures"][0]["error"]


def test_metacognitive_authority_level_uses_l2_model_contract():
    from models import AuthorityLevel as ModelAuthorityLevel

    assert AuthorityLevel is ModelAuthorityLevel
