from dataclasses import dataclass, field


@dataclass(frozen=True)
class BranchMemory:
    branch_id: str
    decisions: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    transient_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MergeMemorySummary:
    branch_id: str
    promoted_items: list[str]
    discarded_items: list[str]


def promote_merge_summary(branch: BranchMemory) -> MergeMemorySummary:
    promoted = [*branch.decisions, *branch.failures]
    return MergeMemorySummary(
        branch_id=branch.branch_id,
        promoted_items=promoted,
        discarded_items=branch.transient_notes,
    )
