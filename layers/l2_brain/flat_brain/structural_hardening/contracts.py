from __future__ import annotations

from enum import Enum
from typing import Dict, List

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
    path: str
    current_class: StructuralClass
    proposed_class: StructuralClass
    risk: RiskLevel
    recommendation: Recommendation
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence_refs: List[str] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list)
    related_specs: List[str] = Field(default_factory=list)
    related_tests: List[str] = Field(default_factory=list)
    related_runtime: List[str] = Field(default_factory=list)
    safe_to_change: bool = False
    requires_human_review: bool = True


class StructuralTriageReport(BaseModel):
    generated_at: str
    base_commit: str
    analysis_base_commit: str | None = None
    report_generated_at_commit: str | None = None
    head_commit: str | None = None
    pack_name: str
    pack_status: str
    repo_health_status: str
    files_analyzed: int
    findings: List[StructuralFinding]
    summary_counts: Dict[str, Dict[str, int]]
    explicit_metrics: Dict[str, int] = Field(default_factory=dict)
    top_actions: List[StructuralFinding]
    limitations: List[str]
    next_recommended_phase: str
