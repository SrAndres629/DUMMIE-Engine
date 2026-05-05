import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("dummie.brain.cognition.patterns")

class PatternMiner:
    """
    Detecta patrones recurrentes en los eventos y logs de decisión.
    """
    def mine_patterns(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        patterns = []
        grouped: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
        for ev in events:
            path = ev.get("path")
            if path:
                key = (path, ev.get("kind", "event"))
                grouped.setdefault(key, []).append(ev)

        for (path, kind), matching_events in sorted(grouped.items()):
            if len(matching_events) >= 3:
                evidence_refs = [
                    ev.get("id", f"{path}:{index}")
                    for index, ev in enumerate(matching_events, start=1)
                ]
                patterns.append(
                    {
                    "pattern_id": f"hotspot_{path.replace('/', '_')}",
                    "name": "Repeated event hotspot",
                    "confidence": min(0.95, round(0.45 + len(matching_events) * 0.10, 2)),
                    "evidence_refs": evidence_refs,
                    "hypothesis": f"{path} has repeated {kind} events.",
                    "proposed_rule": "Require focused regression coverage before changing this path.",
                    "recommended_action": "STRENGTHEN_TESTS",
                    }
                )
        return patterns
