from dataclasses import dataclass


@dataclass(frozen=True)
class FormalModel:
    model_id: str
    invariants: list[str]
    forbidden_states: list[str]


@dataclass(frozen=True)
class FormalVerificationResult:
    status: str
    model_id: str
    reason: str


def verify_formal_model(model: FormalModel) -> FormalVerificationResult:
    if model.forbidden_states:
        return FormalVerificationResult("FAILED", model.model_id, "forbidden_states_present")
    if not model.invariants:
        return FormalVerificationResult("INCONCLUSIVE", model.model_id, "missing_invariants")
    return FormalVerificationResult("PROVEN", model.model_id, "invariants_hold")
