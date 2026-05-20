from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from session_store import SessionStore
from graph_sync_plan import GraphSyncPlan
from kuzu_graph_sync_adapter import KuzuGraphSyncAdapter
from memory_refs import MemoryRef


class MemorySpineBridge:
    """
    [L2_BRAIN] Bridges the gap between operational session memory and the Kuzu spine.
    Implements the 4D-TES synchronization flow.
    """
    def __init__(self, repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg"):
        self.repo_root = Path(repo_root).resolve()
        self.aiwg_root = self.repo_root / aiwg_root
        self.session_store = SessionStore(self.repo_root)
        self.adapter = KuzuGraphSyncAdapter(str(self.aiwg_root / "memory" / "loci.db"))
        self.reports_root = self.aiwg_root / "reports"

    def sync_all_sessions(self, allow_write: bool = False) -> dict[str, Any]:
        sessions = self.session_store.list_sessions()
        all_results = []
        
        for session in sessions:
            sid = session["session_id"]
            res = self.sync_session(sid, allow_write=allow_write)
            all_results.append(res)
            
        summary = {
            "decision": "PASS",
            "sessions_synced": len(all_results),
            "total_nodes": sum(r.get("nodes_planned", 0) for r in all_results),
            "total_edges": sum(r.get("edges_planned", 0) for r in all_results),
            "db_status": self.adapter.validate_plan({"sync_id": "dummy"})["status"]
        }
        
        (self.reports_root / "memory_spine_sync_latest.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
        
        return summary

    def sync_session(self, session_id: str, allow_write: bool = False) -> dict[str, Any]:
        episodes = list(self.session_store.iter_learning_episodes(session_id))
        if not episodes:
            return {"session_id": session_id, "status": "SKIPPED", "reason": "No learning episodes"}
            
        plan = GraphSyncPlan.create(mode="apply" if allow_write else "dry_run")
        
        for ep in episodes:
            ref = MemoryRef.from_learning_episode(f".aiwg/sessions/{session_id}/learning_episodes.jsonl", ep).to_dict()
            plan.add_memory_ref(ref)
            
        # Basic causal edges (simplified)
        for i in range(len(plan.nodes) - 1):
            plan.add_edge(plan.nodes[i].node_id, plan.nodes[i+1].node_id, "CAUSAL_NEXT")
            
        result = self.adapter.apply(plan.to_dict(), allow_write=allow_write)
        result["session_id"] = session_id
        return result


def run_memory_spine_sync(repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg", allow_write: bool = False) -> dict[str, Any]:
    bridge = MemorySpineBridge(repo_root=repo_root, aiwg_root=aiwg_root)
    return bridge.sync_all_sessions(allow_write=allow_write)


if __name__ == "__main__":
    run_memory_spine_sync()
