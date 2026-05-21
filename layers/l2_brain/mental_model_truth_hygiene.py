# Spec: 161_mental_model_truth_hygiene
# Spec: DE-V2-L2-161
"""Mental Model Truth Hygiene — Pack 5.2.2

Scans all stored mental models, classifies their health status, and
produces quarantine/lineage/hygiene reports.  Never deletes models.
"""

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Data contracts
# ---------------------------------------------------------------------------


@dataclass
class MentalModelHygieneFinding:
    model_id: str
    finding_type: str  # overconfidence_model | empty_relations_for_complex_intent | …
    message: str
    severity: str  # WARN | FAIL
    recommended_status: (
        str  # valid | stale | superseded | quarantined | unsafe_rejected | needs_review
    )


@dataclass
class MentalModelHygieneDecision:
    model_id: str
    previous_status: str
    new_status: str
    reason: str
    superseded_by: str = ""


@dataclass
class MentalModelTruthHygieneResult:
    decision: str  # PASS | PASS_WITH_WARNINGS | FAIL
    models_scanned: int = 0
    valid_count: int = 0
    stale_count: int = 0
    superseded_count: int = 0
    quarantined_count: int = 0
    unsafe_rejected_count: int = 0
    needs_review_count: int = 0
    findings: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_COMPLEX_KEYWORDS = frozenset(
    [
        "autonom",
        "synthesis",
        "kuzu",
        "degrad",
        "missing",
        "risk",
        "refactor",
        "plan",
        "scale",
        "scaling",
        "flywheel",
    ]
)

_PLANNING_KEYWORDS = frozenset(["plan", "decide", "what should", "next"])

_UNSAFE_MARKERS = frozenset(
    [
        "secret",
        "private_chain_of_thought",
        "credential",
        "api_key",
        "password",
        "token_secret",
    ]
)


def _intent_hash(intent: str) -> str:
    return hashlib.sha256(intent.strip().lower().encode()).hexdigest()[:12]


def _is_complex_intent(intent: str) -> bool:
    low = intent.lower()
    return any(k in low for k in _COMPLEX_KEYWORDS)


def _is_planning_intent(intent: str) -> bool:
    low = intent.lower()
    return any(k in low for k in _PLANNING_KEYWORDS)


def _is_kuzu_degraded(aiwg_root: Path) -> bool:
    readiness = aiwg_root / "reports" / "readiness_score_calibration_latest.json"
    if readiness.exists():
        try:
            data = json.loads(readiness.read_text(encoding="utf-8"))
            for f in data.get("findings", []):
                if (
                    "degraded" in f.get("id", "").lower()
                    or "degraded" in f.get("description", "").lower()
                ):
                    return True
        except Exception:
            pass
    return True  # conservative default


def _contains_unsafe(model: Dict[str, Any]) -> bool:
    blob = json.dumps(model).lower()
    return any(marker in blob for marker in _UNSAFE_MARKERS)


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------


def run_mental_model_truth_hygiene(aiwg_root: Path = Path(".aiwg")) -> Dict[str, Any]:
    models_root = aiwg_root / "mental_models"
    jsonl_path = models_root / "runtime_models.jsonl"
    index_path = models_root / "runtime_model_index.json"
    reports_root = aiwg_root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    models_root.mkdir(parents=True, exist_ok=True)

    kuzu_degraded = _is_kuzu_degraded(aiwg_root)

    # Load all models --------------------------------------------------
    models: List[Dict[str, Any]] = []
    if jsonl_path.exists():
        for line in jsonl_path.read_text(encoding="utf-8").strip().splitlines():
            try:
                models.append(json.loads(line))
            except Exception:
                pass

    # Load old index ---------------------------------------------------
    old_index: Dict[str, Any] = {}
    if index_path.exists():
        try:
            old_index = json.loads(index_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Scan models ------------------------------------------------------
    findings: List[MentalModelHygieneFinding] = []
    decisions: List[MentalModelHygieneDecision] = []
    enriched_index: Dict[str, Dict[str, Any]] = {}
    quarantined: List[Dict[str, Any]] = []
    lineage: List[Dict[str, Any]] = []

    # Group by intent hash for supersession detection
    by_intent: Dict[str, List[Dict[str, Any]]] = {}
    for m in models:
        ih = _intent_hash(m.get("intent", ""))
        by_intent.setdefault(ih, []).append(m)

    for m in models:
        mid = m.get("model_id", "unknown")
        intent = m.get("intent", "")
        qs = m.get("quality_score", -1)
        rels = m.get("relations", [])
        asms = m.get("assumptions", [])
        decs = m.get("decisions", [])
        conts = m.get("contradictions", [])
        fals = m.get("falsification_tests", [])
        evidence = m.get("evidence_refs", [])
        is_complex = _is_complex_intent(intent)
        is_planning = _is_planning_intent(intent)

        status = "valid"
        finding_list: List[MentalModelHygieneFinding] = []

        # 1. Overconfidence with degraded Kuzu
        if qs >= 100 and kuzu_degraded:
            finding_list.append(
                MentalModelHygieneFinding(
                    mid,
                    "overconfidence_model",
                    f"quality_score={qs} while Kuzu is DEGRADED",
                    "FAIL",
                    "quarantined",
                )
            )
            status = "quarantined"

        # 2. Missing quality score entirely (legacy models)
        if qs == -1:
            finding_list.append(
                MentalModelHygieneFinding(
                    mid,
                    "stale_model",
                    "quality_score missing (legacy model without quality evaluation)",
                    "WARN",
                    "stale",
                )
            )
            if status == "valid":
                status = "stale"

        # 3. Empty relations for complex intent
        if is_complex and not rels:
            finding_list.append(
                MentalModelHygieneFinding(
                    mid,
                    "empty_relations_for_complex_intent",
                    f"No relations for complex intent: {intent[:60]}",
                    "FAIL",
                    "needs_review",
                )
            )
            if status in ("valid",):
                status = "needs_review"

        # 4. Empty assumptions for complex intent
        if is_complex and not asms:
            finding_list.append(
                MentalModelHygieneFinding(
                    mid,
                    "empty_assumptions_for_complex_intent",
                    f"No assumptions for complex intent: {intent[:60]}",
                    "WARN",
                    "needs_review",
                )
            )
            if status == "valid":
                status = "needs_review"

        # 5. Empty decisions for planning intent
        if is_planning and not decs:
            finding_list.append(
                MentalModelHygieneFinding(
                    mid,
                    "empty_decisions_for_planning_intent",
                    f"No decisions for planning intent: {intent[:60]}",
                    "WARN",
                    "needs_review",
                )
            )
            if status == "valid":
                status = "needs_review"

        # 6. Empty contradictions despite degraded evidence
        if kuzu_degraded and not conts and is_complex:
            finding_list.append(
                MentalModelHygieneFinding(
                    mid,
                    "empty_contradictions_despite_degraded_evidence",
                    "No contradictions despite Kuzu DEGRADED",
                    "WARN",
                    "needs_review",
                )
            )
            if status == "valid":
                status = "needs_review"

        # 7. Missing evidence refs
        if not evidence:
            finding_list.append(
                MentalModelHygieneFinding(
                    mid,
                    "missing_evidence_refs",
                    "No evidence references linked",
                    "WARN",
                    "needs_review" if is_complex else "stale",
                )
            )
            if status == "valid":
                status = "stale" if not is_complex else "needs_review"

        # 8. Missing falsification tests
        if not fals and is_complex:
            finding_list.append(
                MentalModelHygieneFinding(
                    mid,
                    "missing_falsification_tests",
                    "No falsification tests for complex intent",
                    "WARN",
                    "needs_review",
                )
            )
            if status == "valid":
                status = "needs_review"

        # 9. Unsafe content
        if _contains_unsafe(m):
            finding_list.append(
                MentalModelHygieneFinding(
                    mid,
                    "unsafe_content",
                    "Model contains unsafe markers (secrets/private reasoning)",
                    "FAIL",
                    "unsafe_rejected",
                )
            )
            status = "unsafe_rejected"

        # Supersession: newer model with same intent and higher quality supersedes older
        ih = _intent_hash(intent)
        peers = by_intent.get(ih, [])
        superseded_by = ""
        if len(peers) > 1:
            best = max(
                peers,
                key=lambda x: (x.get("quality_score", -1), len(x.get("relations", []))),
            )
            if best.get("model_id") != mid and m.get("quality_score", -1) < best.get(
                "quality_score", -1
            ):
                if status not in ("quarantined", "unsafe_rejected"):
                    status = "superseded"
                superseded_by = best.get("model_id", "")
                finding_list.append(
                    MentalModelHygieneFinding(
                        mid,
                        "duplicate_model",
                        f"Superseded by {superseded_by} with higher quality for same intent",
                        "WARN",
                        "superseded",
                    )
                )

        # Record ---
        findings.extend(finding_list)
        decisions.append(
            MentalModelHygieneDecision(
                model_id=mid,
                previous_status=old_index.get(mid, {}).get("status", "unknown")
                if isinstance(old_index.get(mid), dict)
                else "unknown",
                new_status=status,
                reason="; ".join(f.message for f in finding_list) or "No issues found",
                superseded_by=superseded_by,
            )
        )

        enriched_index[mid] = {
            "path": str(jsonl_path.relative_to(aiwg_root.parent))
            if aiwg_root.parent != Path(".")
            else str(jsonl_path),
            "status": status,
            "quality_score": qs,
            "created_at": m.get("created_at", ""),
            "intent_hash": ih,
            "superseded_by": superseded_by,
            "hygiene_findings": [asdict(f) for f in finding_list],
        }

        if status == "quarantined":
            quarantined.append(
                {
                    "model_id": mid,
                    "intent": intent,
                    "quality_score": qs,
                    "findings": [asdict(f) for f in finding_list],
                }
            )

        lineage.append(
            {
                "model_id": mid,
                "intent_hash": ih,
                "intent": intent[:80],
                "status": status,
                "quality_score": qs,
                "superseded_by": superseded_by,
                "created_at": m.get("created_at", ""),
            }
        )

    # Counters ---------------------------------------------------------
    counts = {
        "valid": 0,
        "stale": 0,
        "superseded": 0,
        "quarantined": 0,
        "unsafe_rejected": 0,
        "needs_review": 0,
    }
    for entry in enriched_index.values():
        s = entry["status"]
        if s in counts:
            counts[s] += 1

    overconfidence_count = sum(
        1 for f in findings if f.finding_type == "overconfidence_model"
    )

    decision = "PASS"
    if counts["quarantined"] > 0 or counts["unsafe_rejected"] > 0:
        decision = "PASS_WITH_WARNINGS"
    if counts["needs_review"] > len(models) * 0.5:
        decision = "FAIL"

    result = MentalModelTruthHygieneResult(
        decision=decision,
        models_scanned=len(models),
        valid_count=counts["valid"],
        stale_count=counts["stale"],
        superseded_count=counts["superseded"],
        quarantined_count=counts["quarantined"],
        unsafe_rejected_count=counts["unsafe_rejected"],
        needs_review_count=counts["needs_review"],
        findings=[asdict(f) for f in findings],
        decisions=[asdict(d) for d in decisions],
        summary={
            "models_scanned": len(models),
            "valid_count": counts["valid"],
            "stale_count": counts["stale"],
            "superseded_count": counts["superseded"],
            "quarantined_count": counts["quarantined"],
            "unsafe_rejected_count": counts["unsafe_rejected"],
            "needs_review_count": counts["needs_review"],
            "overconfidence_count": overconfidence_count,
            "kuzu_degraded": kuzu_degraded,
        },
    )

    # Write outputs ----------------------------------------------------
    index_path.write_text(json.dumps(enriched_index, indent=2), encoding="utf-8")
    (models_root / "runtime_model_hygiene.json").write_text(
        json.dumps(result.to_dict(), indent=2), encoding="utf-8"
    )
    (models_root / "runtime_model_quarantine.json").write_text(
        json.dumps(quarantined, indent=2), encoding="utf-8"
    )
    (models_root / "runtime_model_lineage.json").write_text(
        json.dumps(lineage, indent=2), encoding="utf-8"
    )
    (reports_root / "mental_model_truth_hygiene_latest.json").write_text(
        json.dumps(result.to_dict(), indent=2), encoding="utf-8"
    )
    (reports_root / "mental_model_truth_hygiene_latest.md").write_text(
        f"# Mental Model Truth Hygiene\n\nDecision: {decision}\n\n"
        f"Models scanned: {len(models)}\n"
        f"Valid: {counts['valid']} | Stale: {counts['stale']} | Superseded: {counts['superseded']}\n"
        f"Quarantined: {counts['quarantined']} | Unsafe rejected: {counts['unsafe_rejected']} | Needs review: {counts['needs_review']}\n",
        encoding="utf-8",
    )

    return result.to_dict()


if __name__ == "__main__":
    print(json.dumps(run_mental_model_truth_hygiene(), indent=2))
