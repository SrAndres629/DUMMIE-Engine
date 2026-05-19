from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class RepoManifest:
    repo_id: str
    root: str
    memory_root: str
    specs_root: str
    trust_level: str
    allowed_providers: list[str]
    default_orchestrator_model: str


@dataclass
class WorkRoom:
    workroom_id: str
    repo_id: str
    objective: str
    affected_paths: list[str]
    related_specs: list[str]
    status: str = "OPEN"
    agents: list = field(default_factory=list)
    decisions: list = field(default_factory=list)
    evidence: list = field(default_factory=list)


@dataclass
class AgentSession:
    session_id: str
    repo_id: str
    workroom_id: str
    role: str
    provider: str
    model: str
    can_edit: bool
    allowed_paths: list[str]
    context_packet_id: str
    expected_output: str
    status: str = "OPEN"


@dataclass
class ContextPacket:
    context_packet_id: str
    repo_id: str
    workroom_id: str
    role: str
    task: str
    constraints: list[str]
    files: list[str]
    specs: list[str]
    memory_refs: list[str]
    output_schema: str


@dataclass
class EvidencePacket:
    evidence_id: str
    repo_id: str
    workroom_id: str
    producer_session_id: str
    claim: str
    evidence: list[str]
    confidence: float
    verification_status: str = "PENDING"


@dataclass
class DecisionRecord:
    decision_id: str
    repo_id: str
    workroom_id: str
    decision: str
    rationale: str
    approved_by: str
    evidence_ids: list[str]
    status: str = "APPROVED"
