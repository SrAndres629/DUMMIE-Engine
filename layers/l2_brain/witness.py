from dataclasses import dataclass


@dataclass(frozen=True)
class WitnessNode:
    causal_hash: str
    parent_hashes: list[str]
    lamport_t: int


@dataclass(frozen=True)
class WitnessResult:
    status: str
    reason: str


def validate_witness_chain(nodes: list[WitnessNode]) -> WitnessResult:
    previous_hash = "GENESIS"
    previous_lamport = 0
    for node in sorted(nodes, key=lambda n: n.lamport_t):
        if previous_hash not in node.parent_hashes:
            return WitnessResult("INVALID", "parent_hashes_mismatch")
        if node.lamport_t <= previous_lamport:
            return WitnessResult("INVALID", "lamport_not_monotonic")
        previous_hash = node.causal_hash
        previous_lamport = node.lamport_t
    return WitnessResult("VALID", "chain_contiguous")
