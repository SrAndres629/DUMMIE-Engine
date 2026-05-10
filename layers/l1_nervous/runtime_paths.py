from __future__ import annotations

import os
from pathlib import Path


def resolve_root_dir(root_dir: str | os.PathLike[str] | None = None) -> Path:
    if root_dir:
        return Path(root_dir)

    env_root = os.environ.get("DUMMIE_ROOT") or os.environ.get("DUMMIE_ROOT_DIR")
    if env_root:
        return Path(env_root)

    return Path.cwd()


def resolve_aiwg_dir(root_dir: str | os.PathLike[str] | None = None) -> Path:
    env_aiwg = os.environ.get("DUMMIE_AIWG") or os.environ.get("DUMMIE_AIWG_DIR")
    if env_aiwg:
        return Path(env_aiwg)

    return resolve_root_dir(root_dir) / ".aiwg"


def resolve_dummied_socket_path(root_dir: str | os.PathLike[str] | None = None) -> Path:
    explicit = os.environ.get("DUMMIE_DUMMIED_SOCKET_PATH")
    if explicit:
        return Path(explicit)

    return resolve_aiwg_dir(root_dir) / "sockets" / "dummied.sock"


def iter_dummied_socket_candidates(root_dir: str | os.PathLike[str] | None = None) -> tuple[Path, ...]:
    aiwg_dir = resolve_aiwg_dir(root_dir)
    candidates = (
        resolve_dummied_socket_path(root_dir),
        aiwg_dir / "dummied.sock",
        Path("/tmp/dummied.sock"),
    )

    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate not in seen:
            unique.append(candidate)
            seen.add(candidate)
    return tuple(unique)
