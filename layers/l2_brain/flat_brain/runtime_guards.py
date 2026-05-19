from dataclasses import dataclass, field


@dataclass
class GuardInput:
    provider_ready: bool
    memory_locked: bool
    parent_spec_approved: bool
    l3_policy: str


@dataclass
class GuardDecision:
    status: str
    reasons: list[str] = field(default_factory=list)


def evaluate_runtime_guards(inputs: GuardInput) -> GuardDecision:
    reasons: list[str] = []
    if not inputs.provider_ready:
        reasons.append("provider_not_ready")
    if inputs.memory_locked:
        reasons.append("memory_locked")
    if not inputs.parent_spec_approved:
        reasons.append("parent_spec_not_approved")
    if inputs.l3_policy == "L3_INTERVENTION_REQUIRED":
        reasons.append("l3_intervention_required")

    if any(reason in reasons for reason in ["provider_not_ready", "memory_locked", "parent_spec_not_approved"]):
        return GuardDecision("BLOCK", reasons)
    if reasons:
        return GuardDecision("REVIEW", reasons)
    return GuardDecision("ALLOW", ["all_guards_passed"])
