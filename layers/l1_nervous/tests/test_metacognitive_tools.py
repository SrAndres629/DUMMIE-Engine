import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT.parents[0] / "l2_brain"
for path in (ROOT, L2):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from tools_impl.metacognition import MetacognitionToolService
from metacognition.pipeline import MetacognitivePipeline
from metacognition.input_hooks import (
    AuthorityClassifierHook,
    IntentClarifierHook,
    PromptRefinerHook,
    ToolNeedDetectorHook,
)
from metacognition.deliberation_hooks import MissionDecomposerHook, PlanCriticHook
from metacognition.output_hooks import AnswerVerifierHook


class FakeDaemon:
    async def reason_with_tiers(self, *args, **kwargs):
        return '[{"step": 1, "agent": "ResearchAgent", "action": "Map platform APIs"}]'


def _service():
    daemon = FakeDaemon()
    daemon.metacognition = MetacognitivePipeline(
        input_hooks=[
            IntentClarifierHook(),
            PromptRefinerHook(),
            AuthorityClassifierHook(),
            ToolNeedDetectorHook(),
        ],
        deliberation_hooks=[MissionDecomposerHook(daemon), PlanCriticHook()],
        output_hooks=[AnswerVerifierHook()],
    )
    return MetacognitionToolService(daemon)


@pytest.mark.asyncio
async def test_refine_prompt_tool_returns_structured_json():
    result = json.loads(await _service().refine_prompt("Quiero automatizar TikTok"))

    assert result["refined_intent"] == "OBJECTIVE_AUTOMATION"
    assert result["refined_prompt"]


@pytest.mark.asyncio
async def test_plan_mission_tool_returns_mission_plan():
    result = json.loads(await _service().plan_mission("Quiero automatizar TikTok"))

    assert result["mission_plan"][0]["agent"] == "ResearchAgent"


@pytest.mark.asyncio
async def test_criticize_plan_tool_flags_empty_plan():
    result = json.loads(await _service().criticize_plan([]))

    assert "empty" in result["deliberation_summary"].lower()


@pytest.mark.asyncio
async def test_verify_answer_tool_flags_short_answer():
    result = json.loads(await _service().verify_answer("Objetivo", "ok"))

    assert result["verification_findings"]


@pytest.mark.asyncio
async def test_recommend_tools_tool_detects_social_automation_tools():
    result = json.loads(await _service().recommend_tools("Automatizar Facebook e Instagram"))

    assert "browser_driver" in result["required_tools"]
