import pytest
import logging
from unittest.mock import AsyncMock
from layers.l2_brain.metacognition.pipeline import MetacognitivePipeline
from layers.l2_brain.metacognition.input_hooks import IntentClarifierHook, AuthorityClassifierHook
from layers.l2_brain.metacognition.semantic_hooks import SemanticToolSelectorHook
from layers.l2_brain.metacognition.reasoning_hooks import ReasoningExpansionHook
from layers.l2_brain.metacognition.deliberation_hooks import MissionDecomposerHook, PlanCriticHook
from layers.l2_brain.metacognition.output_hooks import AnswerVerifierHook, MemoryUpdateHook
from layers.l2_brain.domain.authority import AuthorityLevel

@pytest.mark.asyncio
async def test_metacognitive_pipeline_e2e_flow():
    mock_daemon = AsyncMock()
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
    assert frame.authority_level == AuthorityLevel.ARCHITECT

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
    assert frame.authority_level == AuthorityLevel.OVERSEER

@pytest.mark.asyncio
async def test_authority_classification_workspace():
    hook = AuthorityClassifierHook()
    pipeline = MetacognitivePipeline(input_hooks=[hook])

    frame = await pipeline.preprocess("test_session_3", "Crea un archivo de notas")
    assert frame.authority_level == AuthorityLevel.ENGINEER

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
