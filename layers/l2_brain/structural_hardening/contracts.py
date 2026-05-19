# Spec Reference: 192_embedding_mesh_foundation
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StructuralClass(str, Enum):
    ACTIVE_RUNTIME = "ACTIVE_RUNTIME"
    ACTIVE_TEST = "ACTIVE_TEST"
    ACTIVE_SPEC = "ACTIVE_SPEC"
    GENERATED = "GENERATED"
    LEGACY = "LEGACY"
    EXPERIMENTAL = "EXPERIMENTAL"
    CONFIG = "CONFIG"
    REPORT = "REPORT"
    SHADOW_CANDIDATE = "SHADOW_CANDIDATE"
    ORPHAN_TEST_CANDIDATE = "ORPHAN_TEST_CANDIDATE"
    UNKNOWN = "UNKNOWN"


class EvidenceType(str, Enum):
    FILE_EXISTS = "FILE_EXISTS"
    IMPORTABLE = "IMPORTABLE"
    REFERENCED_BY_SPEC = "REFERENCED_BY_SPEC"
    REFERENCED_BY_TEST = "REFERENCED_BY_TEST"
    REFERENCES_RUNTIME = "REFERENCES_RUNTIME"
    REFERENCES_SPEC = "REFERENCES_SPEC"
    GENERATED_MARKER = "GENERATED_MARKER"
    LEGACY_PATH = "LEGACY_PATH"
    TEST_NAMING_MATCH = "TEST_NAMING_MATCH"
    SPEC_FRONTMATTER_MATCH = "SPEC_FRONTMATTER_MATCH"
    PHYSICAL_MAP_REFERENCE = "PHYSICAL_MAP_REFERENCE"
    CORE_SPEC_REFERENCE = "CORE_SPEC_REFERENCE"
    CLI_ENTRYPOINT = "CLI_ENTRYPOINT"
    PACKAGE_MANIFEST = "PACKAGE_MANIFEST"
    RUNTIME_IMPORT = "RUNTIME_IMPORT"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"


class Recommendation(str, Enum):
    KEEP_AND_TEST = "KEEP_AND_TEST"
    MAP_TO_SPEC = "MAP_TO_SPEC"
    MAP_TO_TEST = "MAP_TO_TEST"
    MAP_TO_RUNTIME = "MAP_TO_RUNTIME"
    MARK_GENERATED = "MARK_GENERATED"
    MARK_LEGACY = "MARK_LEGACY"
    MARK_EXPERIMENTAL = "MARK_EXPERIMENTAL"
    NEEDS_OWNER = "NEEDS_OWNER"
    NEEDS_IMPORT_CHECK = "NEEDS_IMPORT_CHECK"
    NEEDS_SECURITY_REVIEW = "NEEDS_SECURITY_REVIEW"
    NEEDS_DOC_CONTRACT = "NEEDS_DOC_CONTRACT"
    FREEZE_UNTIL_REVIEW = "FREEZE_UNTIL_REVIEW"
    NO_ACTION = "NO_ACTION"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class StructuralFinding(BaseModel):
    path: str = Field(..., description="File path relative to repository root")
    current_class: StructuralClass = Field(StructuralClass.UNKNOWN, description="Class assigned by semantic matrix")
    proposed_class: StructuralClass = Field(..., description="Calibrated class proposing ownership status")
    risk: RiskLevel = Field(RiskLevel.LOW, description="Safety risk of making structural refactors")
    recommendation: Recommendation = Field(Recommendation.NO_ACTION, description="Specific triage action to perform next")
    confidence: float = Field(1.0, description="Confidence of classification between 0.0 and 1.0")
    evidence_refs: List[str] = Field(default_factory=list, description="Descriptive evidence references justifying categorization")
    reasons: List[str] = Field(default_factory=list, description="Natural language reasoning steps")
    related_specs: List[str] = Field(default_factory=list, description="Specs directly mapping to or referencing this module")
    related_tests: List[str] = Field(default_factory=list, description="Tests validating or importing this module")
    related_runtime: List[str] = Field(default_factory=list, description="Runtime modules associated with this artifact")
    safe_to_change: bool = Field(True, description="True if safe to modify or clean up without regression risk")
    requires_human_review: bool = Field(False, description="True if high-risk or ambiguous requiring human eyes")


class StructuralTriageReport(BaseModel):
    generated_at: str = Field(..., description="ISO timestamp")
    base_commit: str = Field(..., description="Base commit hash of the triage analysis")
    pack_name: str = Field("Structural Hardening Pack 2", description="Verification phase name")
    pack_status: str = Field(..., description="triage_completed / triage_failed")
    repo_health_status: str = Field(..., description="PASS / FAIL based on critical shadow candidate counts")
    files_analyzed: int = Field(..., description="Total count of files processed")
    findings: List[StructuralFinding] = Field(..., description="Complete array of file findings")
    summary_counts: Dict[str, int] = Field(..., description="Count of findings per structural class")
    top_actions: List[Dict[str, Any]] = Field(..., description="Sorted highest risk/priority actions to perform")
    limitations: List[str] = Field(default_factory=list, description="Limitations of current analysis run")
    next_recommended_phase: str = Field("Structural Hardening Pack 2.1 — Physics Cleanup", description="Next evolutionary step")
