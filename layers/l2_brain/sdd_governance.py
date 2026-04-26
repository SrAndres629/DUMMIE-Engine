from dataclasses import dataclass, field
from enum import Enum
from fnmatch import fnmatch
from pathlib import Path


class SpecStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    SUPERSEDED = "SUPERSEDED"


@dataclass
class SpecNode:
    spec_id: str
    path: str
    title: str
    status: SpecStatus
    owner: str = ""
    scopes: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)


@dataclass
class EvidencePacket:
    evidence_id: str
    claim: str
    kind: str
    refs: list[str]
    verified: bool = False


@dataclass
class ChangeRequest:
    change_id: str
    files: list[str]
    intent: str
    parent_spec_ids: list[str]
    evidence_ids: list[str]
    risk: str


@dataclass
class AdmissionDecision:
    status: str
    reason: str
    parent_spec_ids: list[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    status: str
    reason: str


@dataclass
class SpecContradiction:
    left_spec_id: str
    right_spec_id: str
    constraint: str
    opposing_constraint: str


@dataclass
class DecisionRecord:
    decision_id: str
    scope: str
    rationale: str
    lamport_t: int
    review_after_t: int
    superseded_by: str | None = None


@dataclass
class DecisionDecayResult:
    status: str
    reason: str


@dataclass
class SpecCoverageReport:
    covered_files: list[str]
    orphan_files: list[str]


@dataclass
class FailureRecord:
    category: str
    description: str


def compile_spec_document(path: str, text: str) -> SpecNode:
    lines = text.splitlines()
    title = next((line[2:].strip() for line in lines if line.startswith("# ")), Path(path).stem)
    metadata: dict[str, list[str]] = {}
    constraints: list[str] = []
    in_constraints = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_constraints = stripped.lower() == "## constraints"
            continue
        if in_constraints and stripped.startswith("- "):
            constraints.append(stripped[2:].strip())
            continue
        if ":" in stripped and not stripped.startswith("#"):
            key, value = stripped.split(":", 1)
            metadata.setdefault(key.strip().lower(), []).append(value.strip())

    spec_id = _clean_metadata_value(metadata.get("spec_id", [Path(path).stem])[0])
    status_value = _clean_metadata_value(metadata.get("status", ["DRAFT"])[0] or "DRAFT").upper()
    if status_value == "ACTIVE":
        status_value = "APPROVED"
    status = SpecStatus.__members__.get(status_value, SpecStatus.DRAFT)
    return SpecNode(
        spec_id=spec_id,
        path=path,
        title=title,
        status=status,
        owner=_clean_metadata_value(metadata.get("owner", [""])[0]),
        scopes=metadata.get("scope", []),
        constraints=constraints,
    )


def _clean_metadata_value(value: str) -> str:
    return value.strip().strip('"').strip("'")


def verify_evidence_packet(packet: EvidencePacket) -> ValidationResult:
    if not packet.verified:
        return ValidationResult("INVALID", "evidence_not_verified")
    if not packet.refs:
        return ValidationResult("INVALID", "missing_refs")
    if not packet.claim:
        return ValidationResult("INVALID", "missing_claim")
    return ValidationResult("VALID", "verified")


def admit_change(
    request: ChangeRequest,
    specs: list[SpecNode],
    evidence: list[EvidencePacket],
) -> AdmissionDecision:
    if not request.parent_spec_ids:
        return AdmissionDecision("BLOCK", "missing_parent_spec")

    spec_by_id = {spec.spec_id: spec for spec in specs}
    parents = [spec_by_id.get(spec_id) for spec_id in request.parent_spec_ids]
    if any(parent is None for parent in parents):
        return AdmissionDecision("BLOCK", "unknown_parent_spec")
    if any(parent.status != SpecStatus.APPROVED for parent in parents if parent):
        return AdmissionDecision("BLOCK", "parent_spec_not_approved")

    if not _files_match_parent_scopes(request.files, [p for p in parents if p]):
        return AdmissionDecision("REVIEW", "files_outside_parent_spec_scope", request.parent_spec_ids)

    evidence_by_id = {item.evidence_id: item for item in evidence}
    if request.evidence_ids:
        for evidence_id in request.evidence_ids:
            packet = evidence_by_id.get(evidence_id)
            if packet is None or verify_evidence_packet(packet).status != "VALID":
                return AdmissionDecision("REVIEW", "evidence_not_verified", request.parent_spec_ids)
    elif request.risk != "low":
        return AdmissionDecision("REVIEW", "missing_evidence", request.parent_spec_ids)

    return AdmissionDecision("ALLOW", "approved_spec_and_evidence", request.parent_spec_ids)


def _files_match_parent_scopes(files: list[str], specs: list[SpecNode]) -> bool:
    scopes = [scope for spec in specs for scope in spec.scopes]
    if not scopes:
        return True
    return all(any(fnmatch(path, scope) for scope in scopes) for path in files)


def detect_spec_contradictions(specs: list[SpecNode]) -> list[SpecContradiction]:
    contradictions: list[SpecContradiction] = []
    for left_index, left in enumerate(specs):
        for right in specs[left_index + 1 :]:
            for left_constraint in left.constraints:
                normalized_left = _normalize_constraint(left_constraint)
                for right_constraint in right.constraints:
                    normalized_right = _normalize_constraint(right_constraint)
                    if _are_opposites(normalized_left, normalized_right):
                        contradictions.append(
                            SpecContradiction(
                                left.spec_id,
                                right.spec_id,
                                left_constraint,
                                right_constraint,
                            )
                        )
    return contradictions


def _normalize_constraint(value: str) -> str:
    return value.lower().strip().rstrip(".")


def _are_opposites(left: str, right: str) -> bool:
    left_neg = " must not " in left or " cannot " in left
    right_neg = " must not " in right or " cannot " in right
    left_base = left.replace(" must not ", " must ").replace(" cannot ", " can ")
    right_base = right.replace(" must not ", " must ").replace(" cannot ", " can ")
    return left_base == right_base and left_neg != right_neg


def evaluate_decision_decay(
    decision: DecisionRecord,
    current_lamport_t: int,
) -> DecisionDecayResult:
    if decision.superseded_by:
        return DecisionDecayResult("SUPERSEDED", f"superseded_by:{decision.superseded_by}")
    if current_lamport_t - decision.lamport_t >= decision.review_after_t:
        return DecisionDecayResult("REVIEW_REQUIRED", "review_window_elapsed")
    return DecisionDecayResult("CURRENT", "within_review_window")


def calculate_spec_coverage(specs: list[SpecNode], files: list[str]) -> SpecCoverageReport:
    approved_scopes = [
        scope for spec in specs if spec.status == SpecStatus.APPROVED for scope in spec.scopes
    ]
    covered = [path for path in files if any(fnmatch(path, scope) for scope in approved_scopes)]
    orphans = [path for path in files if path not in covered]
    return SpecCoverageReport(covered, orphans)


def classify_failure(description: str) -> FailureRecord:
    lowered = description.lower()
    if "import" in lowered or "architecture" in lowered or "provider directly" in lowered:
        category = "architectural_violation"
    elif "spec" in lowered and "ambiguous" in lowered:
        category = "spec_ambiguity"
    elif "test" in lowered:
        category = "missing_or_failing_test"
    elif "dependency" in lowered:
        category = "bad_dependency"
    else:
        category = "unknown"
    return FailureRecord(category=category, description=description)
