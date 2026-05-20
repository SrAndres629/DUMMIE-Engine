from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class ContextValueScore:
    ref: str
    value_score: float
    value_per_token: float
    decision: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ContextValueScorer:
    def score_context_item(self, item: Any, phase: str = "") -> ContextValueScore:
        ref = str(getattr(item, "ref", "") or "unknown_ref")
        truth_rank = int(getattr(item, "truth_rank", 0) or 0)
        freshness_status = str(getattr(item, "freshness_status", "unknown") or "unknown")
        token_role = str(getattr(item, "token_role", "summary_only") or "summary_only")
        required = bool(getattr(item, "required", False))
        estimated_tokens = int(getattr(item, "estimated_tokens", 0) or 0)
        evidence_refs = list(getattr(item, "evidence_refs", []) or [])
        risk_flags = list(getattr(item, "risk_flags", []) or [])
        source_path = str(getattr(item, "source_path", "") or "")
        summary = str(getattr(item, "summary", "") or "")

        score = float(truth_rank)
        reasons: list[str] = [f"base_truth_rank={truth_rank}"]

        if freshness_status == "fresh":
            score += 20.0
            reasons.append("freshness_bonus=20")
        elif freshness_status == "unknown":
            score -= 15.0
            reasons.append("unknown_penalty=15")
        elif freshness_status == "stale":
            score -= 35.0
            reasons.append("stale_penalty=35")
        elif freshness_status == "missing":
            score -= 50.0
            reasons.append("missing_penalty=50")

        if token_role == "summary_only":
            score += 5.0
            reasons.append("summary_bonus=5")
        elif token_role == "retrieval_candidate":
            score += 0.0

        if required:
            score += 40.0
            reasons.append("required_bonus=40")

        if evidence_refs:
            score += 8.0
            reasons.append("evidence_bonus=8")
        else:
            score -= 6.0
            reasons.append("missing_evidence_penalty=6")

        phase_lower = phase.lower()
        phase_relevant = bool(
            phase_lower
            and (
                phase_lower in ref.lower()
                or phase_lower in source_path.lower()
                or phase_lower in summary.lower()
            )
        )
        if phase_relevant:
            score += 10.0
            reasons.append("phase_relevance_bonus=10")

        risk_penalty = min(30.0, 10.0 * len(risk_flags))
        if risk_penalty:
            score -= risk_penalty
            reasons.append(f"risk_penalty={risk_penalty:g}")

        token_penalty = min(30.0, estimated_tokens / 200.0)
        if token_penalty:
            score -= token_penalty
            reasons.append(f"token_penalty={token_penalty:.2f}")

        value_per_token = score / max(1, estimated_tokens)

        if required:
            decision = "required"
        elif freshness_status in {"missing", "stale"} and not evidence_refs:
            decision = "drop"
        elif score >= 95 and value_per_token >= 0.08:
            decision = "keep"
        elif score >= 55 and value_per_token >= 0.02:
            decision = "compress"
        else:
            decision = "drop"

        return ContextValueScore(
            ref=ref,
            value_score=round(score, 4),
            value_per_token=round(value_per_token, 6),
            decision=decision,
            reason="; ".join(reasons),
        )

    def rank_context_items(self, items: list[Any], phase: str = "") -> list[ContextValueScore]:
        scores = [self.score_context_item(item, phase=phase) for item in items]
        return sorted(scores, key=lambda x: (x.value_per_token, x.value_score), reverse=True)


def score_context_item(item: Any, phase: str = "") -> ContextValueScore:
    return ContextValueScorer().score_context_item(item, phase=phase)


def rank_context_items(items: list[Any], phase: str = "") -> list[ContextValueScore]:
    return ContextValueScorer().rank_context_items(items, phase=phase)
