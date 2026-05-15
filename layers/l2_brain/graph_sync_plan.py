from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

_FORBIDDEN_PATTERNS = [
    (re.compile(r"chain_of_thought", re.I), "private reasoning"),
    (re.compile(r"private reasoning", re.I), "private reasoning"),
    (re.compile(r"secret\s*[=:]", re.I), "secrets"),
    (re.compile(r"token\s*[=:]", re.I), "credentials"),
]

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class GraphNode:
    node_id: str
    node_type: str
    memory_ref_id: str
    mission_id: str = ""
    phase_id: str = ""
    content_hash: str = ""
    properties: dict[str, Any] = field(default_factory=dict)

@dataclass
class GraphEdge:
    edge_id: str
    source: str
    target: str
    edge_type: str
    properties: dict[str, Any] = field(default_factory=dict)

@dataclass
class GraphSyncPlan:
    sync_id: str
    mode: str = "dry_run"
    source_refs: list[str] = field(default_factory=list)
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    blocked: bool = False
    created_at: str = field(default_factory=_now)

    def __post_init__(self):
        if self.mode not in {"dry_run", "apply"}:
            self.mode = "dry_run"
        self.validate()

    def validate(self) -> bool:
        """
        Runs safety checks and returns True if valid.
        """
        # Clear previous warnings if they were just safety blocks
        self.warnings = [w for w in self.warnings if not w.startswith("Blocked due to")]
        self.blocked = False
        
        data_str = json.dumps(asdict(self))
        for pattern, reason in _FORBIDDEN_PATTERNS:
            if pattern.search(data_str):
                self.blocked = True
                self.warnings.append(f"Blocked due to {reason}")
        
        return not self.blocked

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    @classmethod
    def create(cls, mode: str = "dry_run") -> GraphSyncPlan:
        return cls(sync_id=f"gsp-{uuid.uuid4().hex[:8]}", mode=mode)

    def add_memory_ref(self, ref: dict):
        mref_id = ref.get("memory_ref_id", "")
        chash = ref.get("content_hash", "")
        rtype = ref.get("ref_type", "Unknown")
        
        # Map ref types to Kuzu node types
        node_type_map = {
            "learning_episode": "LearningEpisode",
            "vault_entry": "VaultEntry",
            "workbench": "Workbench",
            "phase_event": "PhaseEvent",
            "token_ledger": "TokenLedger",
            "daemon_outcome": "DaemonOutcome"
        }
        node_type = node_type_map.get(rtype, "GenericNode")
        
        node = GraphNode(
            node_id=f"node-{chash[:12]}",
            node_type=node_type,
            memory_ref_id=mref_id,
            mission_id=ref.get("mission_id", ""),
            phase_id=ref.get("phase_id", ""),
            content_hash=chash,
            properties={"path": ref.get("path", "")}
        )
        self.nodes.append(node)
        self.source_refs.append(mref_id)

    def add_edge(self, source_id: str, target_id: str, edge_type: str, props: dict | None = None):
        # Deterministic edge ID
        edge_raw = f"{source_id}-{target_id}-{edge_type}"
        edge_hash = hashlib.sha256(edge_raw.encode()).hexdigest()[:12]
        
        edge = GraphEdge(
            edge_id=f"edge-{edge_hash}",
            source=source_id,
            target=target_id,
            edge_type=edge_type,
            properties=props or {}
        )
        self.edges.append(edge)
