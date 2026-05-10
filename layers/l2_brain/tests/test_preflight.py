import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from preflight import build_intent_draft


def test_high_risk_intent_requires_human_review():
    draft = build_intent_draft(
        draft_id="draft-1",
        goal="Rewrite MCP proxy",
        proposed_steps=["change protocol", "run tests"],
        target_file="Simulations/TASK-001.md",
        risk_level="high",
    )

    assert draft.requires_human_review is True
    assert draft.risk_level == "high"
