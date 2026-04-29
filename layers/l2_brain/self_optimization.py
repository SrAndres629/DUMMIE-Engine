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


@dataclass(frozen=True)
class AutopoiesisSignal:
    ego_status: str
    cognitive_clock: int
    needs_refactor: bool
    action_intent: str


def trigger_autopoiesis(ego_status: str, clock: int, failure_count: int) -> AutopoiesisSignal:
    """
    Analiza el pulso cognitivo del sistema y determina si requiere autoreparación.
    Esta función materializa la Autopoiesis declarada formalmente en IDENTITY.md y SOUL.md.
    """
    needs_refactor = failure_count >= 1 or ego_status == "Degraded"
    intent = "RESTORE_OPTIMAL_STATE" if needs_refactor else "MAINTAIN_EQUILIBRIUM"
    return AutopoiesisSignal(
        ego_status=ego_status,
        cognitive_clock=clock,
        needs_refactor=needs_refactor,
        action_intent=intent
    )

