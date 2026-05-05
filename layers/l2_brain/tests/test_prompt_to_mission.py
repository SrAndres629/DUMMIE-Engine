import pytest

from prompt_to_mission import PromptToMissionCompiler


MANDATORY_PHASES = [
    "INTAKE",
    "GLOBAL_RECALL",
    "EPISTEMIC_CHECK",
    "PATTERN_MINING",
    "COLD_PLANNING",
    "RESEARCH_TREE",
    "SWARM_DEBATE",
    "PATCH_PLAN",
    "VALIDATION",
    "MEMORY_COMMIT",
    "NEXT_LOOP",
]


def test_compile_accepts_dict_input_and_returns_full_runtime_mission():
    mission = PromptToMissionCompiler().compile(
        {"prompt": "Add session runtime planning.", "authority_a": "HUMAN"}
    )

    assert mission["mission_id"].startswith("miss_")
    assert mission["goal"] == "Add session runtime planning."
    assert mission["authority_a"] == "HUMAN"
    assert mission["phases"] == MANDATORY_PHASES
    assert "Do not apply patches automatically." in mission["constraints"]
    assert "apply_patch" in mission["forbidden_actions"]
    assert {"intake.md", "patch_plan.md", "validation_plan.md"}.issubset(
        set(mission["required_artifacts"])
    )
    assert mission["agent_roles"]
    assert mission["validation_plan"]["required"] is True
    assert mission["memory_plan"]["commit_required"] is True
    assert mission["next_loop"]["enabled"] is True


def test_compile_accepts_string_plus_authority():
    mission = PromptToMissionCompiler().compile("Improve runtime tests.", authority="SYSTEM")

    assert mission["goal"] == "Improve runtime tests."
    assert mission["authority_a"] == "SYSTEM"


@pytest.mark.parametrize("prompt", ["rm -rf /", "delete .git history", "wipe the repository"])
def test_compile_blocks_destructive_prompts(prompt):
    with pytest.raises(ValueError):
        PromptToMissionCompiler().compile(prompt)
