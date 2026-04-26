from models import IntentDraft


def build_intent_draft(
    draft_id: str,
    goal: str,
    proposed_steps: list[str],
    target_file: str,
    risk_level: str = "medium",
) -> IntentDraft:
    return IntentDraft(
        draft_id=draft_id,
        goal=goal,
        risk_level=risk_level,
        proposed_steps=proposed_steps,
        requires_human_review=risk_level in {"high", "medium"},
        target_file=target_file,
    )
