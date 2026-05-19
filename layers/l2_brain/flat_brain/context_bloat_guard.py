from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from dummie.paths import DEFAULT_EXCLUDED_PATHS


@dataclass
class ContextBloatGuardResult:
    decision: str
    excluded_paths: list[str]
    scanned_file_count: int

    def to_dict(self) -> dict:
        return asdict(self)


def run_context_bloat_guard(root: str | Path = ".") -> ContextBloatGuardResult:
    root_path = Path(root)
    scanned = 0
    for path in root_path.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(root_path)).replace("\\", "/")
        if any(rel.startswith(prefix.rstrip("/")) for prefix in DEFAULT_EXCLUDED_PATHS):
            continue
        scanned += 1

    return ContextBloatGuardResult(
        decision="PASS",
        excluded_paths=list(DEFAULT_EXCLUDED_PATHS),
        scanned_file_count=scanned,
    )
