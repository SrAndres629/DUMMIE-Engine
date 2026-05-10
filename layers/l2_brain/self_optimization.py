from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class FailureSignal:
    locus: str
    category: str


@dataclass(frozen=True)
class SelfOptimizationProposal:
    target_locus: str
    failure_category: str
    proposed_action: str
    rationale: str


def propose_self_optimization(
    failures: list[FailureSignal],
    threshold: int = 3,
) -> SelfOptimizationProposal | None:
    counts = Counter((failure.locus, failure.category) for failure in failures)
    for (locus, category), count in counts.items():
        if count >= threshold:
            return SelfOptimizationProposal(
                target_locus=locus,
                failure_category=category,
                proposed_action="SPEC_REFACTOR",
                rationale=f"{count} repeated failures at {locus} ({category})",
            )
    return None
