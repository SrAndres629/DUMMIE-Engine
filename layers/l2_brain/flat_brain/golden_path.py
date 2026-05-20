from dataclasses import dataclass


@dataclass(frozen=True)
class GoldenPath:
    parent_spec_id: str
    target_module: str
    allowed: bool
    steps: list[str]


def generate_golden_path(
    spec_id: str,
    approved: bool,
    target_module: str,
) -> GoldenPath:
    if not approved:
        return GoldenPath(spec_id, target_module, False, ["Block: parent spec is not approved"])
    return GoldenPath(
        parent_spec_id=spec_id,
        target_module=target_module,
        allowed=True,
        steps=[
            f"Write tests for {target_module}",
            f"Define interface for {target_module}",
            f"Implement minimal behavior for {target_module}",
            "Attach evidence packet",
            "Run architecture fitness functions",
        ],
    )
