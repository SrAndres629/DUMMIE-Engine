
import logging
from typing import Any, Dict, List

logger = logging.getLogger("dummie.brain.cognition.epistemic")

class EpistemicJudge:
    """
    Evalúa la veracidad de las afirmaciones basadas en la jerarquía de evidencia.
    """

    EVIDENCE_WEIGHTS = {
        "test": 1.0,
        "typed_schema": 0.9,
        "source_code": 0.85,
        "physical_map": 0.75,
        "core_spec": 0.70,
        "active_spec": 0.65,
        "generated_report": 0.45,
        "comment": 0.25
    }

    def evaluate_claim(self, claim: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not evidence:
            return {
                "claim": claim,
                "confidence": 0.0,
                "status": "INSUFFICIENT_EVIDENCE",
                "supporting_evidence": [],
                "contradicting_evidence": [],
                "required_next_check": "verify_source",
                "decision": "verify_source",
            }

        supporting_evidence: List[Dict[str, Any]] = []
        contradicting_evidence: List[Dict[str, Any]] = []

        for item in evidence:
            normalized = dict(item)
            normalized["_weight"] = self.EVIDENCE_WEIGHTS.get(item.get("type"), 0.1)
            if item.get("contradicts"):
                contradicting_evidence.append(normalized)
            elif item.get("supports") or item.get("contradicts") is False:
                supporting_evidence.append(normalized)

        supporting_evidence.sort(key=lambda item: item["_weight"], reverse=True)
        contradicting_evidence.sort(key=lambda item: item["_weight"], reverse=True)

        top_support = supporting_evidence[0]["_weight"] if supporting_evidence else 0.0
        top_contradiction = contradicting_evidence[0]["_weight"] if contradicting_evidence else 0.0

        if top_contradiction >= top_support and contradicting_evidence:
            status = "CONTRADICTED"
            confidence = top_contradiction
            decision = "reject"
            required_next_check = None
        elif supporting_evidence:
            confidence = top_support
            status = "SUPPORTED" if confidence >= 0.65 else "ASSUMPTION"
            decision = "trust" if status == "SUPPORTED" else "verify_source"
            required_next_check = None if status == "SUPPORTED" else "source_code_or_test"
        else:
            confidence = max(
                (self.EVIDENCE_WEIGHTS.get(item.get("type"), 0.1) for item in evidence),
                default=0.0,
            )
            status = "ASSUMPTION"
            decision = "verify_source"
            required_next_check = "source_code_or_test"

        return {
            "claim": claim,
            "confidence": confidence,
            "status": status,
            "supporting_evidence": [self._strip_weight(item) for item in supporting_evidence],
            "contradicting_evidence": [self._strip_weight(item) for item in contradicting_evidence],
            "required_next_check": required_next_check,
            "decision": decision,
        }

    def compare_sources(self, left: Dict[str, Any], right: Dict[str, Any]) -> int:
        """Compare two evidence sources by authority weight.

        Returns:
            1 if left outranks right, -1 if right outranks left, 0 if equal.
        """
        left_weight = self.EVIDENCE_WEIGHTS.get(left.get("type", ""), 0.1)
        right_weight = self.EVIDENCE_WEIGHTS.get(right.get("type", ""), 0.1)
        if left_weight > right_weight:
            return 1
        if right_weight > left_weight:
            return -1
        return 0

    @staticmethod
    def _strip_weight(item: Dict[str, Any]) -> Dict[str, Any]:
        clean = dict(item)
        clean.pop("_weight", None)
        return clean
