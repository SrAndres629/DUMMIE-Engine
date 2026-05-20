from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class MemoryRef:
    """
    [L2_BRAIN] Standardized reference for 4D-TES / Graph integration.
    """
    memory_ref_id: str
    ref_type: str
    path: str
    content_hash: str
    session_id: str = ""
    mission_id: str = ""
    phase_id: str = ""
    created_at: str = field(default_factory=_now)
    kuzu_ready: bool = False
    embedding_ready: bool = False

    def __post_init__(self):
        if self.ref_type not in {"learning_episode", "vault_entry", "workbench", "phase_event", "token_ledger", "daemon_outcome"}:
            raise ValueError(f"Invalid ref_type: {self.ref_type}")
        
        # Path safety validation
        if ".." in self.path or Path(self.path).is_absolute():
            raise ValueError("Path must be relative and cannot contain traversal components (..)")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_learning_episode(cls, path: str, episode: dict) -> "MemoryRef":
        content_hash = _calculate_hash(episode)
        ref_id = f"mref-ep-{content_hash[:8]}"
        
        return cls(
            memory_ref_id=ref_id,
            ref_type="learning_episode",
            path=path,
            content_hash=content_hash,
            session_id=episode.get("session_id", ""),
            mission_id=episode.get("mission_id", ""),
            phase_id=episode.get("phase_id", ""),
            kuzu_ready=True,
            embedding_ready=False
        )

    @classmethod
    def from_vault_entry(cls, path: str, entry: dict) -> "MemoryRef":
        content_hash = entry.get("content_hash") or _calculate_hash(entry)
        ref_id = f"mref-vlt-{content_hash[:8]}"
        
        return cls(
            memory_ref_id=ref_id,
            ref_type="vault_entry",
            path=path,
            content_hash=content_hash,
            mission_id=entry.get("mission_id", ""),
            kuzu_ready=True,
            embedding_ready=False
        )

def _calculate_hash(data: dict) -> str:
    encoded = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
