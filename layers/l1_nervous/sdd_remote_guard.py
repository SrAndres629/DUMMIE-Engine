from dataclasses import dataclass
from pathlib import Path
import os
import re
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
    repo_root: str | None = None,
) -> RemoteAdmissionDecision:
    if not _is_mutating_tool(tool_name):
        return RemoteAdmissionDecision("ALLOW", "read_only_tool")

    admission = arguments.get("sdd_admission")
    if not isinstance(admission, dict):
        auto = _auto_admit_from_repo_specs(arguments, repo_root)
        if auto.status == "ALLOW":
            return auto
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


def _auto_admit_from_repo_specs(
    arguments: dict[str, Any],
    repo_root: str | None,
) -> RemoteAdmissionDecision:
    target_path = _extract_target_path(arguments)
    if not target_path:
        return RemoteAdmissionDecision("BLOCK", "missing_target_path")

    root = Path(repo_root or os.environ.get("DUMMIE_ROOT", os.environ.get("DUMMIE_ROOT_DIR", os.getcwd())))
    specs_dir = root / "doc" / "specs"
    if not specs_dir.exists():
        return RemoteAdmissionDecision("BLOCK", "missing_specs_dir")

    normalized_target = _normalize_repo_relative_path(root, target_path)
    if not normalized_target:
        return RemoteAdmissionDecision("BLOCK", "target_path_outside_repo")
    for spec_path in specs_dir.glob("*.md"):
        text = spec_path.read_text(errors="ignore")
        if not _is_active_spec(text):
            continue
        evidence_paths = _extract_physical_evidence_paths(text)
        for evidence in evidence_paths:
            normalized_evidence = _normalize_repo_relative_path(root, evidence)
            if not normalized_evidence:
                continue
            if normalized_target == normalized_evidence or normalized_target.startswith(normalized_evidence.rstrip("/") + "/"):
                return RemoteAdmissionDecision("ALLOW", "auto_sdd_admission")
    return RemoteAdmissionDecision("BLOCK", "no_covering_active_spec")


def _extract_target_path(arguments: dict[str, Any]) -> str:
    for key in ("path", "filepath", "file_path", "target_file"):
        value = arguments.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _normalize_repo_relative_path(root: Path, value: str) -> str:
    try:
        candidate = (root / value.strip().lstrip("/")).resolve()
        resolved_root = root.resolve()
        candidate.relative_to(resolved_root)
        return candidate.relative_to(resolved_root).as_posix()
    except ValueError:
        return ""


def _is_active_spec(text: str) -> bool:
    lowered = text.lower()
    return (
        'status: "active"' in lowered
        or "status: active" in lowered
        or 'status: "stable"' in lowered
        or "status: stable" in lowered
        or 'status: "approved"' in lowered
        or "status: approved" in lowered
    )


def _extract_physical_evidence_paths(text: str) -> list[str]:
    paths: list[str] = []
    in_evidence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_evidence = stripped.lower() == "## physical evidence"
            continue
        if not in_evidence or not stripped.startswith("- "):
            continue
        match = re.search(r"`([^`]+)`", stripped)
        raw = match.group(1) if match else stripped[2:].strip()
        if raw and not raw.startswith("doc/specs/"):
            paths.append(raw.strip().rstrip("/"))
    return paths
