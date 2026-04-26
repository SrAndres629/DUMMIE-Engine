from dataclasses import dataclass


@dataclass(frozen=True)
class SpecEvolution:
    spec_id: str
    old_hash: str
    new_hash: str
    lamport_t: int


@dataclass(frozen=True)
class WorkSubscription:
    agent_id: str
    workroom_id: str
    spec_id: str
    seen_hash: str


@dataclass(frozen=True)
class NervousPulse:
    agent_id: str
    workroom_id: str
    spec_id: str
    severity: str
    message: str


def compute_stale_agent_pulses(
    evolutions: list[SpecEvolution],
    subscriptions: list[WorkSubscription],
) -> list[NervousPulse]:
    latest = {e.spec_id: e for e in evolutions}
    pulses: list[NervousPulse] = []
    for sub in subscriptions:
        evolution = latest.get(sub.spec_id)
        if evolution and sub.seen_hash != evolution.new_hash:
            pulses.append(
                NervousPulse(
                    agent_id=sub.agent_id,
                    workroom_id=sub.workroom_id,
                    spec_id=sub.spec_id,
                    severity="INTERRUPT",
                    message=f"Spec {sub.spec_id} evolved at Lamport {evolution.lamport_t}",
                )
            )
    return pulses
