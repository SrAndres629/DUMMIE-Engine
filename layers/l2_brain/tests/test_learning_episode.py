import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning_episode import LearningEpisode, LearningEpisodeMetrics  # noqa: E402


def test_learning_episode_serializes_json():
    episode = LearningEpisode(
        episode_id="episode-1",
        mission_id="mission-1",
        session_id="session-1",
        input_summary="User asked for cognitive hook slice",
        action_taken="Implemented tests first",
        outcome="partial",
        metrics=LearningEpisodeMetrics(
            input_tokens=100,
            cached_tokens=20,
            output_tokens=80,
            latency_ms=50,
            tests_passed=True,
            human_interventions=0,
        ),
        what_worked=["recovery audit"],
        what_failed=["industrial audit path points to /app"],
        recommended_next_improvement="Wire mission autonomy after Slice 1 is verified",
        capability_amplification_score=0.25,
        evidence_refs=[".aiwg/reports/post_reboot_recovery_audit.md"],
    )

    data = json.loads(episode.to_json())

    assert data["episode_id"] == "episode-1"
    assert data["metrics"]["tests_passed"] is True
    assert data["capability_amplification_score"] == 0.25


def test_learning_episode_round_trip_from_json():
    episode = LearningEpisode(
        episode_id="episode-2",
        mission_id="mission-2",
        session_id="session-2",
        input_summary="Analyze repo",
        action_taken="Created hook packet",
        outcome="success",
        metrics=LearningEpisodeMetrics(tests_passed=True),
    )

    restored = LearningEpisode.from_json(episode.to_json())

    assert restored == episode


def test_learning_episode_rejects_private_chain_of_thought_evidence():
    try:
        LearningEpisode(
            episode_id="episode-3",
            mission_id="mission-3",
            session_id="session-3",
            input_summary="Analyze repo",
            action_taken="Created hook packet",
            outcome="success",
            evidence_refs=["chain-of-thought: hidden reasoning"],
        )
    except ValueError as exc:
        assert "private reasoning" in str(exc)
    else:
        raise AssertionError("private chain-of-thought evidence was accepted")
