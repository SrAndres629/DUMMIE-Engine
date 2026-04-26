import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from consensus import build_consensus_decision


def test_consensus_decision_preserves_dissent_and_evidence():
    decision = build_consensus_decision(
        consensus_id="cons-1",
        topic="Provider opacity",
        participants=["planner", "critic"],
        decision="L2 must use ports",
        dissent=["critic: verify imports"],
        evidence_refs=["spec:OBS-001"],
    )

    assert decision.dissent == ["critic: verify imports"]
    assert decision.evidence_refs == ["spec:OBS-001"]
