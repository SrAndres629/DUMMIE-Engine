"""
[L2_BRAIN] Learning Episode — serializable outcome memory contract.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


OUTCOMES = {"success", "partial", "failed", "blocked", "unknown"}

_FORBIDDEN_PATTERNS = [
    (re.compile(r"\.env\s*[=:]", re.I), "forbidden .env assignment"),
    (re.compile(r"secret\s*(is|[:=])", re.I), "forbidden secret value"),
    (re.compile(r"credential\s*(is|[:=])", re.I), "forbidden credential value"),
    (re.compile(r"token\s*[=:]", re.I), "forbidden token assignment"),
    (re.compile(r"password\s*[=:]", re.I), "forbidden password assignment"),
    (re.compile(r"chain_of_thought", re.I), "private reasoning"),
    (re.compile(r"chain-of-thought", re.I), "private reasoning"),
    (re.compile(r"private reasoning", re.I), "private reasoning"),
    (re.compile(r"private_reasoning", re.I), "private reasoning"),
    (re.compile(r"internal monologue", re.I), "private reasoning"),
]

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

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
    input_summary: str = "" # Defaulted for backward compatibility
    action_taken: str = ""  # Defaulted for backward compatibility
    outcome: str = "unknown"
    phase_id: str = ""
    outcome_id: str = ""
    workbench_ref: str = ""
    vault_refs: list[str] = field(default_factory=list)
    token_cost_summary: dict[str, Any] = field(default_factory=dict)
    context_budget_summary: dict[str, Any] = field(default_factory=dict)
    metrics: LearningEpisodeMetrics = field(default_factory=LearningEpisodeMetrics)
    what_worked: list[str] = field(default_factory=list)
    what_failed: list[str] = field(default_factory=list)
    recommended_next_improvement: str = ""
    capability_amplification_score: float = 0.0
    evidence_refs: list[str] = field(default_factory=list)
    memory_tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if self.outcome not in OUTCOMES:
            raise ValueError(f"outcome must be one of {sorted(OUTCOMES)}")
        if isinstance(self.metrics, dict):
            self.metrics = LearningEpisodeMetrics(**self.metrics)
        self.capability_amplification_score = max(-1.0, min(1.0, float(self.capability_amplification_score)))
        
        # Comprehensive safety check
        self._reject_private(self.to_dict())

    def _reject_private(self, value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                self._reject_private(str(key))
                self._reject_private(item)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                self._reject_private(item)
        elif isinstance(value, str):
            for pattern, reason in _FORBIDDEN_PATTERNS:
                if pattern.search(value):
                    raise ValueError(f"LearningEpisode payload contains {reason}")

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
