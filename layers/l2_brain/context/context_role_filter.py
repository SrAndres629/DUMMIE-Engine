from __future__ import annotations

from layers.l2_brain.context_package import ContextItem


ROLE_KIND_ALLOWLIST: dict[str, set[str]] = {
    "planner": {"phase_state", "phase_seed", "world_model", "coverage", "folder_note"},
    "executor": {"phase_state", "phase_seed", "folder_note"},
    "auditor": {"phase_state", "world_model", "coverage", "folder_note"},
}


def filter_context_items_by_role(
    items: list[ContextItem], session_role: str | None
) -> list[ContextItem]:
    role = (session_role or "").strip().lower()
    if not role or role not in ROLE_KIND_ALLOWLIST:
        return items

    allowed = ROLE_KIND_ALLOWLIST[role]
    kept = [item for item in items if item.required or item.kind in allowed]
    return kept
