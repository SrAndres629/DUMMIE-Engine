import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("dummie.brain.cognition.patterns")

class PatternMiner:
    """
    Detecta patrones recurrentes en los eventos y logs de decisión.
    """
    def mine_patterns(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        patterns: List[Dict[str, Any]] = []
        patterns.extend(self._mine_hotspots(events))
        patterns.extend(self._mine_contract_drift(events))
        return patterns

    def _mine_hotspots(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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

    def _mine_contract_drift(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect paths with contradicting evidence across source types."""
        patterns: List[Dict[str, Any]] = []
        path_evidence: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

        for ev in events:
            path = ev.get("path")
            if not path:
                continue
            ev_type = ev.get("type", ev.get("kind", "unknown"))
            supports = ev.get("supports")
            contradicts = ev.get("contradicts")
            if supports is None and contradicts is None:
                continue
            path_evidence.setdefault(path, {}).setdefault(ev_type, []).append(ev)

        for path, types in sorted(path_evidence.items()):
            supporting_types: List[str] = []
            contradicting_types: List[str] = []
            all_refs: List[str] = []

            for ev_type, evs in types.items():
                for ev in evs:
                    all_refs.append(ev.get("id", f"{path}:{ev_type}"))
                    if ev.get("contradicts"):
                        contradicting_types.append(ev_type)
                    elif ev.get("supports"):
                        supporting_types.append(ev_type)

            if supporting_types and contradicting_types:
                patterns.append({
                    "pattern_id": f"drift_{path.replace('/', '_')}",
                    "name": "Contract drift",
                    "confidence": min(0.90, round(0.50 + len(all_refs) * 0.08, 2)),
                    "evidence_refs": all_refs,
                    "hypothesis": (
                        f"{path} has contradicting evidence: "
                        f"supported by {', '.join(sorted(set(supporting_types)))} "
                        f"but contradicted by {', '.join(sorted(set(contradicting_types)))}."
                    ),
                    "proposed_rule": "Reconcile spec and implementation before further changes.",
                    "recommended_action": "RECONCILE_CONTRACT",
                })
        return patterns

