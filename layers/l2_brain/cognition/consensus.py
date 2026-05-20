from models import ConsensusDecision


def build_consensus_decision(
    consensus_id: str,
    topic: str,
    participants: list[str],
    decision: str,
    dissent: list[str] | None = None,
    evidence_refs: list[str] | None = None,
) -> ConsensusDecision:
    return ConsensusDecision(
        consensus_id=consensus_id,
        topic=topic,
        participants=participants,
        decision=decision,
        dissent=dissent or [],
        evidence_refs=evidence_refs or [],
    )
