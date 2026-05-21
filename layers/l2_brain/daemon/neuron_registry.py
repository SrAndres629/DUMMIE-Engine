"""Neuron registry for DummieDaemon.

This module provides a simple file-backed registry that tracks "neurons" –
CLI or other agents that connect to the Dummie Engine. Each neuron receives a
unique hash identifier, a friendly name (Neuron N), a role, a list of
capabilities, a status and a last‑heartbeat timestamp. The registry is stored
as JSON under ``.aiwg/state/neuron_registry.json`` so that multiple daemon
instances can share a consistent view.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Path where the registry is persisted.  ``AIWG`` points to the .aiwg directory.
from dummie.paths import AIWG

REGISTRY_PATH = AIWG / "state" / "neuron_registry.json"


@dataclass
class NeuronMeta:
    """Metadata for a single neuron (CLI/agent)."""

    neuron_id: str  # UUID4 hex string, serves as primary key
    name: str  # Human‑friendly name, e.g. "Neuron 1"
    role: str  # Declared role – implementation, critique, etc.
    capabilities: List[str] = field(default_factory=list)
    status: str = "ACTIVE"  # ACTIVE, DEGRADED, OFFLINE
    last_heartbeat: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def heartbeat(self) -> None:
        """Update the heartbeat timestamp to now (UTC)."""
        self.last_heartbeat = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)


class NeuronRegistry:
    """File‑backed singleton registry for neurons.

    The registry is loaded on first use and written back whenever it is
    mutated.  It is deliberately simple – the goal is to give the daemon a
    reliable source of truth for session management without adding heavy
    dependencies.
    """

    _instance: Optional["NeuronRegistry"] = None

    def __init__(self, path: Path = REGISTRY_PATH) -> None:
        self.path = path
        self.neurons: Dict[str, NeuronMeta] = {}
        self._load()

    @classmethod
    def instance(cls) -> "NeuronRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def _load(self) -> None:
        if not self.path.exists():
            # Ensure parent directories exist for future writes.
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._save()
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            for nid, data in raw.get("neurons", {}).items():
                self.neurons[nid] = NeuronMeta(**data)
        except Exception as exc:
            # Corrupted registry – start fresh but log for debugging.
            logger = logging.getLogger("dummie.neuron_registry")
            logger.warning(
                f"Failed to load neuron registry ({self.path}): {exc}, starting empty."
            )
            self.neurons = {}
            self._save()

    def _save(self) -> None:
        payload = {
            "neurons": {nid: meta.to_dict() for nid, meta in self.neurons.items()}
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def _next_name(self) -> str:
        """Generate the next friendly name based on current count.

        The first neuron becomes "Neuron 1", the second "Neuron 2", etc.
        """
        existing = len(self.neurons)
        return f"Neuron {existing + 1}"

    def register(
        self,
        role: str = "generic",
        capabilities: Optional[List[str]] = None,
        name: Optional[str] = None,
    ) -> NeuronMeta:
        """Create a new neuron entry.

        Args:
            role: Declared functional role (implementation, critique, …).
            capabilities: Optional list of capability strings.
            name: If supplied, overrides the automatically generated friendly name.

        Returns:
            The freshly created :class:`NeuronMeta` instance.
        """
        neuron_id = uuid.uuid4().hex
        capabilities = capabilities or []
        friendly_name = name or self._next_name()
        meta = NeuronMeta(
            neuron_id=neuron_id,
            name=friendly_name,
            role=role,
            capabilities=capabilities,
        )
        self.neurons[neuron_id] = meta
        self._save()
        return meta

    def heartbeat(self, neuron_id: str) -> bool:
        """Refresh the heartbeat timestamp for ``neuron_id``.

        Returns ``True`` if the neuron existed, ``False`` otherwise.
        """
        meta = self.neurons.get(neuron_id)
        if meta is None:
            return False
        meta.heartbeat()
        self._save()
        return True

    def list(self) -> List[NeuronMeta]:
        """Return a list of all registered neurons (unsorted)."""
        return list(self.neurons.values())

    def set_status(self, neuron_id: str, status: str) -> bool:
        """Update the status field for a neuron.

        Accepted statuses are ``ACTIVE``, ``DEGRADED`` and ``OFFLINE``. The
        function does not enforce the enum – callers should validate.
        Returns ``True`` on success.
        """
        meta = self.neurons.get(neuron_id)
        if meta is None:
            return False
        meta.status = status
        self._save()
        return True

    def prune_offline(self, older_than_seconds: int = 300) -> None:
        """Remove neurons that have not sent a heartbeat for ``older_than_seconds``.
        This keeps the registry tidy for long‑running daemon processes.
        """
        cutoff = datetime.now(timezone.utc).timestamp() - older_than_seconds
        to_remove = []
        for nid, meta in self.neurons.items():
            try:
                hb_ts = datetime.fromisoformat(meta.last_heartbeat).timestamp()
                if hb_ts < cutoff:
                    to_remove.append(nid)
            except Exception:
                # If parsing fails, be defensive and remove.
                to_remove.append(nid)
        for nid in to_remove:
            del self.neurons[nid]
        if to_remove:
            self._save()
