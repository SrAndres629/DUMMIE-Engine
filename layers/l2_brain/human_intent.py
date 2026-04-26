from dataclasses import dataclass


@dataclass(frozen=True)
class HumanIntentClassification:
    kind: str
    authority: str
    rationale: str


def classify_human_artifact(text: str) -> HumanIntentClassification:
    lowered = text.lower()
    if "# decision" in lowered or "status: approved" in lowered:
        return HumanIntentClassification("decision", "HIGH", "explicit_decision_marker")
    if "# constraint" in lowered or "must" in lowered:
        return HumanIntentClassification("constraint", "HIGH", "normative_language")
    if "# experiment" in lowered:
        return HumanIntentClassification("experiment", "MEDIUM", "experiment_marker")
    if "# idea" in lowered or "maybe" in lowered:
        return HumanIntentClassification("idea", "LOW", "speculative_language")
    return HumanIntentClassification("note", "MEDIUM", "unclassified_human_note")
