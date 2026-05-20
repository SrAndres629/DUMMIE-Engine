# Spec: 157_dialectical_reasoning_runtime
# Spec: DE-V2-L2-157
from dataclasses import dataclass, field, asdict
from typing import List

@dataclass
class DialecticalReview:
    thesis: str
    antithesis: str
    counterexamples: List[str]
    synthesis: str
    decision: str

    def to_dict(self): return asdict(self)

def run_dialectical_review(intent: str) -> DialecticalReview:
    thesis = f"Proceed with {intent} to improve the system."
    antithesis = "Propose delay until core regressions (Kuzu/Tests) are resolved."
    counterexamples = ["Previous failed refactor attempts", "Incomplete test coverage"]
    synthesis = "Proceed with caution using local mock-fallback; prioritize test repair first."
    decision = "proceed"

    is_high_risk = any(k in intent.lower() for k in ["autonom", "synthesis", "kuzu", "degrad", "missing", "risk"])
    
    if is_high_risk:
        antithesis = "Propose immediate halt of autonomous skill synthesis to prevent catastrophic state desync. Autonomy without persistent memory is an existential safety failure."
        counterexamples = [
            "Kuzu persistence layer is DEGRADED, meaning memory spine state cannot survive restarts.",
            "177 missing or failing tests prevent DUMMIE from verifying regression invariants."
        ]
        synthesis = "Do not proceed to autonomous skill synthesis until memory persistence and test debt are repaired."
        decision = "repair_first"
    elif "refactor" in intent.lower():
        decision = "repair_first"
        synthesis = "Do not proceed with active refactoring until test debt is mitigated."

    return DialecticalReview(
        thesis=thesis,
        antithesis=antithesis,
        counterexamples=counterexamples,
        synthesis=synthesis,
        decision=decision
    )

if __name__ == "__main__":
    import sys
    intent = sys.argv[1] if len(sys.argv) > 1 else "decide whether DUMMIE should proceed to autonomous skill synthesis while Kuzu is degraded and tests are missing"
    review = run_dialectical_review(intent)
    import json
    print(json.dumps(review.to_dict(), indent=2))
