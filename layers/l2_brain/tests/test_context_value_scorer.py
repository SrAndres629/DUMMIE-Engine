from dataclasses import dataclass, field

from layers.l2_brain.context_value_scorer import ContextValueScorer


@dataclass
class DummyItem:
    ref: str
    truth_rank: int
    freshness_status: str
    token_role: str
    required: bool
    estimated_tokens: int
    evidence_refs: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    source_path: str = ""
    summary: str = ""


def test_context_value_scorer_prefers_fresh_high_truth():
    scorer = ContextValueScorer()

    fresh = DummyItem(
        ref="a",
        truth_rank=90,
        freshness_status="fresh",
        token_role="summary_only",
        required=False,
        estimated_tokens=120,
        evidence_refs=["ref1"],
        risk_flags=[],
    )
    stale = DummyItem(
        ref="b",
        truth_rank=30,
        freshness_status="stale",
        token_role="retrieval_candidate",
        required=False,
        estimated_tokens=120,
        evidence_refs=[],
        risk_flags=["risk"],
    )

    s_fresh = scorer.score_context_item(fresh, phase="P10")
    s_stale = scorer.score_context_item(stale, phase="P10")

    assert s_fresh.value_score > s_stale.value_score
    assert s_fresh.value_per_token > s_stale.value_per_token


def test_context_value_scorer_marks_required_items_as_required_decision():
    scorer = ContextValueScorer()
    item = DummyItem(
        ref="required_ref",
        truth_rank=10,
        freshness_status="stale",
        token_role="summary_only",
        required=True,
        estimated_tokens=300,
        evidence_refs=[],
        risk_flags=["risk"],
    )
    score = scorer.score_context_item(item)
    assert score.decision == "required"


def test_context_value_scorer_ranking_is_deterministic():
    scorer = ContextValueScorer()
    items = [
        DummyItem("x", 70, "fresh", "summary_only", False, 100, ["e1"]),
        DummyItem("y", 40, "unknown", "summary_only", False, 60, []),
        DummyItem("z", 80, "fresh", "retrieval_candidate", False, 300, ["e2"]),
    ]

    ranked = scorer.rank_context_items(items, phase="P10")
    assert [r.ref for r in ranked] == [r.ref for r in scorer.rank_context_items(items, phase="P10")]
