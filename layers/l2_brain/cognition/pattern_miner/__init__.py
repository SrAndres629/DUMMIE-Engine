import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("dummie.brain.cognition.patterns")

class PatternEvidence:
    def __init__(self, ref: str, kind: str, path: str = None, summary: str = "", weight: float = 0.5):
        self.ref = ref
        self.kind = kind
        self.path = path
        self.summary = summary
        self.weight = weight

    def to_dict(self):
        return {
            "ref": self.ref,
            "kind": self.kind,
            "path": self.path,
            "summary": self.summary,
            "weight": self.weight
        }

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
                evidence_list = [
                    {"ref": ref, "kind": kind, "path": path, "summary": f"Repeated {kind} event", "weight": 0.5}
                    for ref in evidence_refs
                ]
                patterns.append(
                    {
                        "pattern_id": f"hotspot_{path.replace('/', '_')}",
                        "name": "Repeated event hotspot",
                        "confidence": min(0.95, round(0.45 + len(matching_events) * 0.10, 2)),
                        "evidence_refs": evidence_refs,
                        "evidence": evidence_list,
                        "hypothesis": f"{path} has repeated {kind} events.",
                        "proposed_rule": "Require focused regression coverage before changing this path.",
                        "recommended_action": "STRENGTHEN_TESTS",
                        # V2 fields for compatibility
                        "kind": "HOTSPOT",
                        "severity": min(0.95, round(0.40 + len(matching_events) * 0.10, 2)),
                        "recurrence": len(matching_events) / 10.0,
                        "semantic_distance": 0.0,
                        "temporal_anomaly": 0.0,
                        "safety_risk": 0.2,
                        "memory_risk": 0.2,
                        "affected_paths": [path],
                        "coldplanner_metrics": {
                            "impact_on_mvp": 0.55,
                            "risk_reduction": 0.70,
                            "unblock_future_loops": 0.60,
                            "testability": 0.80,
                            "implementation_cost_inverse": 0.65,
                            "reversibility": 0.85,
                            "risk": 0.30,
                        }
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
                evidence_list = [
                    {"ref": ref, "kind": "evidence", "path": path, "summary": "Contract evidence", "weight": 0.75}
                    for ref in all_refs
                ]
                patterns.append({
                    "pattern_id": f"drift_{path.replace('/', '_')}",
                    "name": "Contract drift",
                    "confidence": min(0.90, round(0.50 + len(all_refs) * 0.08, 2)),
                    "evidence_refs": all_refs,
                    "evidence": evidence_list,
                    "hypothesis": (
                        f"{path} has contradicting evidence: "
                        f"supported by {', '.join(sorted(set(supporting_types)))} "
                        f"but contradicted by {', '.join(sorted(set(contradicting_types)))}."
                    ),
                    "proposed_rule": "Reconcile spec and implementation before further changes.",
                    "recommended_action": "RECONCILE_CONTRACT",
                    # V2 fields for compatibility
                    "kind": "CONTRACT_DRIFT",
                    "severity": min(0.90, round(0.55 + len(all_refs) * 0.08, 2)),
                    "recurrence": len(all_refs) / 8.0,
                    "semantic_distance": 0.65,
                    "temporal_anomaly": 0.0,
                    "safety_risk": 0.45,
                    "memory_risk": 0.50,
                    "affected_paths": [path],
                    "coldplanner_metrics": {
                        "impact_on_mvp": 0.75,
                        "risk_reduction": 0.85,
                        "unblock_future_loops": 0.75,
                        "testability": 0.70,
                        "implementation_cost_inverse": 0.55,
                        "reversibility": 0.75,
                        "risk": 0.45,
                    }
                })
        return patterns
