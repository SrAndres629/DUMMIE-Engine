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
    if "refactor" in intent.lower():
        decision = "repair_first"
    
    return DialecticalReview(
        thesis=thesis,
        antithesis=antithesis,
        counterexamples=counterexamples,
        synthesis=synthesis,
        decision=decision
    )
