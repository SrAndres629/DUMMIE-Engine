from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

from layers.l2_brain.models import AuthorityLevel, IntentType


OUTCOME_STATUSES = {"SUCCESS", "PARTIAL", "FAILED", "BLOCKED", "DEGRADED"}
METACOGNITION_STATUSES = {"READY", "DEGRADED", "MISSING"}
SENSOR_MODES = {"WARN", "BLOCK"}
SENSOR_DECISIONS = {"ALLOW", "WARN", "BLOCK"}
MEASUREMENT_TYPES = {"estimated", "runtime"}
AUTHORITY_LEVEL_VALUES = {item.value for item in AuthorityLevel}
INTENT_TYPE_VALUES = {item.value for item in IntentType}


@dataclass
class ModelRouteMetadata:
    tier: str = ""
    provider: str = ""
    reason: str = ""
    hook_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetacognitionStatus:
    status: str = "MISSING"
    error: str = ""
    enabled_hooks: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.status not in METACOGNITION_STATUSES:
            self.status = "DEGRADED" if self.status else "MISSING"


@dataclass
class SensorFirstStatus:
    mode: str = "WARN"
    decision: str = "ALLOW"
    reason: str = ""

    def __post_init__(self) -> None:
        if self.mode not in SENSOR_MODES:
            self.mode = "WARN"
        if self.decision not in SENSOR_DECISIONS:
            self.decision = "WARN"


@dataclass
class EfficiencyMetrics:
    input_tokens: int = 0
    cached_tokens: int = 0
    output_tokens: int = 0
    estimated_direct_tokens: int = 0
    estimated_gateway_tokens: int = 0
    token_reduction_ratio: float = 0.0
    measurement_type: str = "estimated"
    budget_pressure: str = "low"  # low, medium, high, extreme
    token_economy_summary: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.measurement_type not in MEASUREMENT_TYPES:
            self.measurement_type = "runtime" if str(self.measurement_type).startswith("runtime") else "estimated"


@dataclass
class TestExecutionSummary:
    __test__ = False

    commands: list[str] = field(default_factory=list)
    passed: int = 0
    failed: int = 0


@dataclass
class NextAction:
    recommended: str = ""
    reason: str = ""
    blocked_by: list[str] = field(default_factory=list)


@dataclass
class RecoveryHint:
    can_resume: bool = True
    resume_from: str = ""
    missing_context: list[str] = field(default_factory=list)


@dataclass
class DaemonOutcome:
    outcome_id: str
    status: str
    session_id: str = ""
    mission_id: str = ""
    phase_id: str = ""
    transaction_id: str = ""
    context_token: str = ""
    authority_level: str = ""
    intent_type: str = ""
    model_route: ModelRouteMetadata = field(default_factory=ModelRouteMetadata)
    metacognition: MetacognitionStatus = field(default_factory=MetacognitionStatus)
    sensor_first: SensorFirstStatus = field(default_factory=SensorFirstStatus)
    efficiency: EfficiencyMetrics = field(default_factory=EfficiencyMetrics)
    tests: TestExecutionSummary = field(default_factory=TestExecutionSummary)
    evidence_refs: list[str] = field(default_factory=list)
    next_action: NextAction = field(default_factory=NextAction)
    recovery_hint: RecoveryHint = field(default_factory=RecoveryHint)
    learning_episode_ref: str = ""
    memory_refs: list[str] = field(default_factory=list)
    retrieval_refs: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.status not in OUTCOME_STATUSES:
            raise ValueError(f"Unsupported daemon outcome status: {self.status}")
        if self.authority_level and self.authority_level not in AUTHORITY_LEVEL_VALUES:
            raise ValueError(f"Unsupported authority_level: {self.authority_level}")
        if self.intent_type and self.intent_type not in INTENT_TYPE_VALUES:
            raise ValueError(f"Unsupported intent_type: {self.intent_type}")
        self.evidence_refs = [_public_ref(ref) for ref in self.evidence_refs if _is_public_ref(ref)]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True, sort_keys=True)


def _is_public_ref(value: str) -> bool:
    lowered = str(value).lower()
    return "chain_of_thought" not in lowered and "private reasoning" not in lowered


def _public_ref(value: str) -> str:
    return str(value)
