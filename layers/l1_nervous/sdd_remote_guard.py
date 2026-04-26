from dataclasses import dataclass
from typing import Any


MUTATING_KEYWORDS = {
    "write",
    "edit",
    "create",
    "delete",
    "remove",
    "move",
    "rename",
    "patch",
    "put",
    "append",
    "commit",
    "push",
    "merge",
}


@dataclass(frozen=True)
class RemoteAdmissionDecision:
    status: str
    reason: str


def evaluate_remote_tool_admission(
    server_name: str,
    tool_name: str,
    arguments: dict[str, Any],
) -> RemoteAdmissionDecision:
    if not _is_mutating_tool(tool_name):
        return RemoteAdmissionDecision("ALLOW", "read_only_tool")

    admission = arguments.get("sdd_admission")
    if not isinstance(admission, dict):
        return RemoteAdmissionDecision("BLOCK", "missing_sdd_admission")
    if admission.get("status") != "ALLOW":
        return RemoteAdmissionDecision("BLOCK", "sdd_admission_not_allow")
    if not admission.get("parent_spec_ids"):
        return RemoteAdmissionDecision("BLOCK", "missing_parent_spec_ids")
    return RemoteAdmissionDecision("ALLOW", "sdd_admission_allow")


def _is_mutating_tool(tool_name: str) -> bool:
    lowered = tool_name.lower()
    parts = lowered.replace("-", "_").split("_")
    return any(keyword in parts or lowered.startswith(keyword) for keyword in MUTATING_KEYWORDS)
