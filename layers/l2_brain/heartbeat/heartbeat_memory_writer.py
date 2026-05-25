from __future__ import annotations

import json
import time
from typing import Any, Dict


def append_heartbeat_node_safe(
    hb_id: str,
    mode: str,
    result: Dict[str, Any],
    max_attempts: int = 2,
    timeout_ms: int = 200,
) -> Dict[str, Any]:
    start = time.perf_counter()
    last_error = ""
    attempts = 0

    for _ in range(max_attempts):
        attempts += 1
        if (time.perf_counter() - start) * 1000 > timeout_ms:
            return {
                "success": False,
                "degraded": True,
                "error": "timeout",
                "attempts": attempts,
            }
        try:
            from brain.domain.context.models import (
                AuthorityLevel,
                IntentType,
                SixDimensionalContext,
            )
            from brain.infrastructure.adapters.kuzu_repository import KuzuRepository
            from layers.l2_brain.domain.memory.models import MemoryNode4DTES

            repo = KuzuRepository(db_path=".aiwg/memory/loci.db")
            last_hash = repo.get_last_leaf_hash(locus_x="l2.heartbeat")
            last_node = repo.get_by_hash(last_hash) if last_hash != "GENESIS" else None
            current_tick = (last_node.context.lamport_t + 1) if last_node else 1

            context = SixDimensionalContext(
                locus_x="l2.heartbeat",
                locus_y="heartbeat.lifecycle",
                locus_z="heartbeat.outcome",
                lamport_t=current_tick,
                authority_a=AuthorityLevel.AGENT,
                intent_i=IntentType.OBSERVATION,
            )
            payload = json.dumps(
                {
                    "heartbeat_id": hb_id,
                    "mode": mode,
                    "decision": result.get("decision", ""),
                }
            ).encode("utf-8")
            node = MemoryNode4DTES.generate(
                parent_hash=last_hash, context=context, payload=payload
            )
            ok = bool(repo.append(node))
            if ok:
                return {
                    "success": True,
                    "degraded": False,
                    "error": "",
                    "attempts": attempts,
                    "lamport_t": current_tick,
                }
            last_error = "append_failed"
        except Exception as exc:
            last_error = str(exc)

    return {
        "success": False,
        "degraded": True,
        "error": last_error or "unknown",
        "attempts": attempts,
    }
