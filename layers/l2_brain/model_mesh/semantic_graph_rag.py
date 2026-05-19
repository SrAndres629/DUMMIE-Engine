from dataclasses import dataclass, field


@dataclass(frozen=True)
class GraphFact:
    kind: str
    subject: str
    predicate: str
    object: str


@dataclass(frozen=True)
class GraphAnswer:
    text: str
    evidence_refs: list[str] = field(default_factory=list)


def answer_why_decision(question: str, facts: list[GraphFact]) -> GraphAnswer:
    question_lower = question.lower()
    candidates = [
        fact for fact in facts if fact.kind == "rationale" and fact.subject.lower() in question_lower
    ]
    if not candidates:
        candidates = [fact for fact in facts if fact.kind == "rationale"]
    if not candidates:
        return GraphAnswer("No rationale found.", [])
    fact = candidates[0]
    return GraphAnswer(
        text=f"{fact.subject} was selected because {fact.object}.",
        evidence_refs=[f"{fact.subject}:{fact.predicate}"],
    )
