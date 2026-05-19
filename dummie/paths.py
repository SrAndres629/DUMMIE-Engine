from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AIWG = ROOT / ".aiwg"

DEFAULT_EXCLUDED_PATHS = [
    ".venv",
    "venv",
    "node_modules",
    "target",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".aiwg/workspaces",
    ".aiwg/memory",
    ".aiwg/tools/opencode-data",
]

CONTEXT_KILLER_PATTERNS = [
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "*.bin",
    "*.beam",
    "*.log",
    "*.tmp",
    "*.cache",
    "*.zip",
    "*.tar",
    "*.tar.gz",
]


def normalize_repo_path(path: str | Path) -> str:
    """Return a stable relative path rooted at workspace root."""
    p = Path(path).resolve()
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)
