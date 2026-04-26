from dataclasses import dataclass, field
from typing import Any


@dataclass
class CausalEvent:
    event_id: str
    lamport_t: int
    causal_hash: str
    parent_hash: str
    context: dict[str, Any]


@dataclass
class ReplayFrame:
    target_lamport_t: int
    head_hash: str
    event_ids: list[str]
    context: dict[str, Any] = field(default_factory=dict)


def replay_until(events: list[CausalEvent], target_lamport_t: int) -> ReplayFrame:
    ordered = sorted(
        [event for event in events if event.lamport_t <= target_lamport_t],
        key=lambda event: event.lamport_t,
    )
    context: dict[str, Any] = {}
    event_ids: list[str] = []
    head_hash = "GENESIS"
    for event in ordered:
        context.update(event.context)
        event_ids.append(event.event_id)
        head_hash = event.causal_hash
    return ReplayFrame(target_lamport_t, head_hash, event_ids, context)
