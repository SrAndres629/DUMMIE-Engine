"""
[L2_BRAIN] Learning Episode — serializable outcome memory contract.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


OUTCOMES = {"success", "partial", "failed", "blocked", "unknown"}


@dataclass
class LearningEpisodeMetrics:
    input_tokens: int = 0
    cached_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    local_model_calls: int = 0
    cloud_model_calls: int = 0
    tests_passed: bool = False
    human_interventions: int = 0
    safety_blocks: int = 0


@dataclass
class LearningEpisode:
    episode_id: str
    mission_id: str
    session_id: str
    input_summary: str
    action_taken: str
    outcome: str = "unknown"
    metrics: LearningEpisodeMetrics = field(default_factory=LearningEpisodeMetrics)
    what_worked: list[str] = field(default_factory=list)
    what_failed: list[str] = field(default_factory=list)
    recommended_next_improvement: str = ""
    capability_amplification_score: float = 0.0
    evidence_refs: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.outcome not in OUTCOMES:
            raise ValueError(f"outcome must be one of {sorted(OUTCOMES)}")
        if isinstance(self.metrics, dict):
            self.metrics = LearningEpisodeMetrics(**self.metrics)
        self.capability_amplification_score = max(-1.0, min(1.0, float(self.capability_amplification_score)))
        _reject_private_reasoning(self.evidence_refs)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_json(cls, raw: str) -> "LearningEpisode":
        data = json.loads(raw)
        if "metrics" in data and isinstance(data["metrics"], dict):
            data["metrics"] = LearningEpisodeMetrics(**data["metrics"])
        return cls(**data)


def _reject_private_reasoning(values: list[str]) -> None:
    private_terms = ("chain-of-thought", "chain_of_thought", "private reasoning", "internal monologue")
    for value in values:
        normalized = str(value).lower()
        if any(term in normalized for term in private_terms):
            raise ValueError("private reasoning artifacts are not accepted in LearningEpisode evidence_refs")
