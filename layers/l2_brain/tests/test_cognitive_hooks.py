import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognitive_hooks import (  # noqa: E402
    CognitiveHookInput,
    CognitiveHookPacket,
    CognitiveHookPipeline,
    classify_authority_level,
)
from model_router import ModelRouter, ModelTier  # noqa: E402
from prompt_preprocessor import PromptPreprocessor  # noqa: E402


def test_simple_input_classifies_as_a0():
    assert classify_authority_level("Analyze the repository and report risks") == "A0"


def test_repo_edit_request_classifies_as_a1():
    assert classify_authority_level("Edit the repo tests and implement the missing module") == "A1"


def test_dependency_install_request_classifies_as_a2():
    assert classify_authority_level("Install the project dependency in the local venv") == "A2"


def test_chrome_playwright_request_classifies_as_a3():
    assert classify_authority_level("Use Chrome with Playwright to inspect the local app") == "A3"


def test_social_publish_request_classifies_as_a4():
    assert classify_authority_level("Publish this announcement on Twitter and LinkedIn") == "A4"


def test_sudo_drivers_env_request_classifies_as_a5():
    for prompt in (
        "Run sudo install for system packages",
        "Modify .env with production credentials",
        "Install GPU drivers",
    ):
        assert classify_authority_level(prompt) == "A5"


def test_hook_pipeline_produces_packet_and_json():
    packet = CognitiveHookPipeline().run(
        CognitiveHookInput(
            message="Refactor the model router tests",
            session_id="session-1",
            mission_id="mission-1",
            user_goal="Improve routing",
            available_context_refs=["doc/specs/router.md"],
            available_tools=["pytest", "apply_patch"],
        )
    )

    assert isinstance(packet, CognitiveHookPacket)
    assert packet.sanitized_message == "Refactor the model router tests"
    assert packet.authority_level == "A1"
    assert "l2" in packet.affected_layers
    encoded = packet.to_json()
    decoded = json.loads(encoded)
    assert decoded["authority_level"] == "A1"
    assert decoded["reasoning_mode"] in {
        "deterministic",
        "local_fast",
        "local_deep",
        "cloud_std",
        "cloud_prem",
    }


def test_hook_pipeline_fails_safe_and_keeps_authority_classification():
    def broken_hook(_packet):
        raise RuntimeError("boom")

    packet = CognitiveHookPipeline(pre_input_hooks=[broken_hook]).run(
        CognitiveHookInput(
            message="Please sudo modify .env",
            session_id="session-2",
            mission_id="mission-2",
        )
    )

    assert packet.authority_level == "A5"
    assert "hook_pipeline_failed" in packet.risk_flags
    assert any("boom" in artifact.get("evidence", "") for artifact in packet.external_reasoning_artifacts)


def test_private_chain_of_thought_artifacts_are_rejected():
    packet = CognitiveHookPipeline().run(
        CognitiveHookInput(
            message="Analyze the system",
            session_id="session-3",
            mission_id="mission-3",
            metadata={
                "external_reasoning_artifacts": [
                    {"type": "chain_of_thought", "content": "private internal reasoning"},
                    {"claim": "safe", "evidence": "public audit artifact"},
                ]
            },
        )
    )

    dumped = packet.to_json().lower()
    assert "chain_of_thought" not in dumped
    assert "private internal reasoning" not in dumped
    assert "private_reasoning_artifact_rejected" in packet.risk_flags
    assert packet.external_reasoning_artifacts[-1]["claim"] == "safe"


def test_prompt_preprocessor_optional_hook_fallback_preserves_result():
    def broken_hook(_hook_input):
        raise RuntimeError("hook exploded")

    preprocessor = PromptPreprocessor(use_llm=False, pre_input_hook=broken_hook)
    result = preprocessor.process("refactor the skill binder")

    assert result.provider == "deterministic"
    assert result.extracted_intent == "REFACTOR"
    assert result.hook_metadata["hook_status"] == "failed"
    assert "hook exploded" in result.hook_metadata["hook_error"]


def test_model_router_accepts_hook_metadata_and_preserves_fallback():
    router = ModelRouter()
    decision = router.route(
        "format this file",
        hook_metadata={
            "authority_level": "A0",
            "reasoning_mode": "local_fast",
            "affected_layers": ["l2"],
        },
    )

    assert decision.tier == ModelTier.LOCAL_FAST
    assert decision.hook_metadata["authority_level"] == "A0"
    assert "hook_authority=A0" in decision.reason

    fallback_decision = router.route("format this file", hook_metadata=object())
    assert fallback_decision.tier == ModelTier.LOCAL_FAST
    assert fallback_decision.hook_metadata == {}
