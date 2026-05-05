from __future__ import annotations

from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
from typing import Any
import hashlib
import math


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


@dataclass
class PatternEvidence:
    ref: str
    kind: str
    path: str | None = None
    timestamp: str | None = None
    lamport_t: int | None = None
    summary: str = ""
    weight: float = 0.5


@dataclass
class DetectedPattern:
    pattern_id: str
    kind: str
    name: str
    confidence: float
    severity: float
    recurrence: float
    semantic_distance: float
    temporal_anomaly: float
    safety_risk: float
    memory_risk: float
    affected_paths: list[str]
    evidence: list[PatternEvidence]
    hypothesis: str
    proposed_rule: str
    recommended_action: str
    coldplanner_metrics: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PatternMinerV2:
    def mine_patterns(
        self,
        events: list[dict[str, Any]],
        file_cards: list[dict[str, Any]] | None = None,
        graph_edges: list[dict[str, Any]] | None = None,
        session_artifacts: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        patterns: list[DetectedPattern] = []
        patterns.extend(self.detect_hotspots(events))
        patterns.extend(self.detect_contract_drift(events))
        patterns.extend(self.detect_semantic_decay(events, file_cards or [], graph_edges or []))
        patterns.extend(self.detect_temporal_anomalies(events, session_artifacts or []))

        return [p.to_dict() for p in sorted(patterns, key=lambda p: p.severity, reverse=True)]

    def detect_hotspots(self, events: list[dict[str, Any]]) -> list[DetectedPattern]:
        by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for ev in events:
            path = ev.get("path")
            if path:
                by_path[path].append(ev)

        out: list[DetectedPattern] = []
        for path, evs in by_path.items():
            if len(evs) < 4:
                continue

            recurrence = clamp01(len(evs) / 10)
            evidence = [
                PatternEvidence(
                    ref=ev.get("event_id") or ev.get("id") or f"{path}:{i}",
                    kind=ev.get("event_type") or ev.get("kind") or "event",
                    path=path,
                    lamport_t=ev.get("lamport_t")
                    or ev.get("six_d_context", {}).get("lamport_t"),
                    summary=ev.get("summary", ""),
                    weight=0.5,
                )
                for i, ev in enumerate(evs, start=1)
            ]

            out.append(
                DetectedPattern(
                    pattern_id=self._id("HOTSPOT", path),
                    kind="HOTSPOT",
                    name="Repeated file hotspot",
                    confidence=clamp01(0.45 + recurrence * 0.45),
                    severity=clamp01(0.40 + recurrence * 0.35),
                    recurrence=recurrence,
                    semantic_distance=0.0,
                    temporal_anomaly=0.0,
                    safety_risk=0.2,
                    memory_risk=0.2,
                    affected_paths=[path],
                    evidence=evidence,
                    hypothesis=f"{path} changes repeatedly and is likely unstable.",
                    proposed_rule="Require regression test coverage and owner review before further edits.",
                    recommended_action="STRENGTHEN_TESTS",
                    coldplanner_metrics={
                        "impact_on_mvp": 0.55,
                        "risk_reduction": 0.70,
                        "unblock_future_loops": 0.60,
                        "testability": 0.80,
                        "implementation_cost_inverse": 0.65,
                        "reversibility": 0.85,
                        "risk": 0.30,
                        "repeated_failure": recurrence,
                    },
                )
            )

        return out

    def detect_contract_drift(self, events: list[dict[str, Any]]) -> list[DetectedPattern]:
        by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for ev in events:
            if ev.get("path") and (ev.get("supports") is not None or ev.get("contradicts") is not None):
                by_path[ev["path"]].append(ev)

        out: list[DetectedPattern] = []
        for path, evs in by_path.items():
            support = [ev for ev in evs if ev.get("supports")]
            contradict = [ev for ev in evs if ev.get("contradicts")]
            if not support or not contradict:
                continue

            evidence_strength = clamp01((len(support) + len(contradict)) / 8)
            severity = clamp01(0.55 + evidence_strength * 0.35)

            out.append(
                DetectedPattern(
                    pattern_id=self._id("CONTRACT_DRIFT", path),
                    kind="CONTRACT_DRIFT",
                    name="Contract drift",
                    confidence=clamp01(0.60 + evidence_strength * 0.30),
                    severity=severity,
                    recurrence=clamp01(len(evs) / 8),
                    semantic_distance=0.65,
                    temporal_anomaly=0.0,
                    safety_risk=0.45,
                    memory_risk=0.50,
                    affected_paths=[path],
                    evidence=[
                        PatternEvidence(
                            ref=ev.get("event_id") or ev.get("id") or f"{path}:{i}",
                            kind=ev.get("type") or ev.get("kind") or "evidence",
                            path=path,
                            summary=ev.get("summary", ""),
                            weight=0.75,
                        )
                        for i, ev in enumerate(evs, start=1)
                    ],
                    hypothesis=f"{path} has contradictory support/contradiction evidence.",
                    proposed_rule="Reconcile executable contract, source code, spec, and tests before execution.",
                    recommended_action="RECONCILE_CONTRACT",
                    coldplanner_metrics={
                        "impact_on_mvp": 0.75,
                        "risk_reduction": 0.85,
                        "unblock_future_loops": 0.75,
                        "testability": 0.70,
                        "implementation_cost_inverse": 0.55,
                        "reversibility": 0.75,
                        "risk": 0.45,
                        "semantic_decay": 0.65,
                        "memory_risk": 0.50,
                    },
                )
            )

        return out

    def detect_semantic_decay(
        self,
        events: list[dict[str, Any]],
        file_cards: list[dict[str, Any]],
        graph_edges: list[dict[str, Any]],
    ) -> list[DetectedPattern]:
        out: list[DetectedPattern] = []

        cards_by_path = {
            card.get("path") or card.get("identity", {}).get("path"): card
            for card in file_cards
            if card.get("path") or card.get("identity", {}).get("path")
        }

        boundary_violations = Counter()
        for edge in graph_edges:
            if edge.get("edge_type") in {"boundary_violation", "contradicts"}:
                src = edge.get("source") or edge.get("from")
                if src:
                    boundary_violations[src] += 1

        for path, card in cards_by_path.items():
            risks = " ".join(map(str, card.get("risks", []))).lower()
            summary = str(card.get("summary") or card.get("retrieval_summary") or "").lower()

            workaround_frequency = sum(
                token in risks or token in summary
                for token in ["fallback", "bypass", "legacy", "compatibility", "sys.path", "todo", "fixme"]
            ) / 7

            missing_test_ratio = 1.0 if not card.get("tests") else 0.0
            boundary_violation = clamp01(boundary_violations[path] / 3)
            stale_spec_ratio = 1.0 if "stale" in risks or "deprecated" in risks else 0.0
            spec_distance = 1.0 if "contract drift" in risks or "contradict" in risks else 0.0

            score = clamp01(
                0.30 * spec_distance
                + 0.25 * boundary_violation
                + 0.20 * missing_test_ratio
                + 0.15 * stale_spec_ratio
                + 0.10 * workaround_frequency
            )

            if score < 0.55:
                continue

            out.append(
                DetectedPattern(
                    pattern_id=self._id("SEMANTIC_DECAY", path),
                    kind="SEMANTIC_DECAY",
                    name="Semantic decay",
                    confidence=score,
                    severity=clamp01(0.50 + score * 0.40),
                    recurrence=workaround_frequency,
                    semantic_distance=score,
                    temporal_anomaly=0.0,
                    safety_risk=boundary_violation,
                    memory_risk=stale_spec_ratio,
                    affected_paths=[path],
                    evidence=[
                        PatternEvidence(
                            ref=f"file_card:{path}",
                            kind="file_card",
                            path=path,
                            summary="File card indicates drift/workaround/stale or missing tests.",
                            weight=score,
                        )
                    ],
                    hypothesis=f"{path} appears to diverge from intended architecture or contract.",
                    proposed_rule="Add executable contract test and remove undocumented workaround.",
                    recommended_action="REPAIR_SEMANTIC_DECAY",
                    coldplanner_metrics={
                        "impact_on_mvp": 0.70,
                        "risk_reduction": 0.80,
                        "unblock_future_loops": 0.70,
                        "testability": 0.75,
                        "implementation_cost_inverse": 0.50,
                        "reversibility": 0.70,
                        "risk": clamp01(0.35 + boundary_violation * 0.35),
                        "semantic_decay": score,
                        "boundary_violation": boundary_violation,
                        "memory_risk": stale_spec_ratio,
                    },
                )
            )

        return out

    def detect_temporal_anomalies(
        self,
        events: list[dict[str, Any]],
        session_artifacts: list[dict[str, Any]],
    ) -> list[DetectedPattern]:
        repeated_action_rate = self._repeated_action_rate(events)
        validation_oscillation = self._validation_oscillation(events)
        no_progress = self._no_progress_ratio(events)
        blocker_recurrence = self._blocker_recurrence(events)
        compaction_lag = self._compaction_lag(events, session_artifacts)

        score = clamp01(
            0.25 * repeated_action_rate
            + 0.25 * validation_oscillation
            + 0.20 * no_progress
            + 0.20 * blocker_recurrence
            + 0.10 * compaction_lag
        )

        if score < 0.60:
            return []

        evidence = [
            PatternEvidence(
                ref="session:recent_events",
                kind="temporal_window",
                summary=(
                    f"repeated={repeated_action_rate:.2f}, "
                    f"oscillation={validation_oscillation:.2f}, "
                    f"no_progress={no_progress:.2f}, "
                    f"blockers={blocker_recurrence:.2f}, "
                    f"compaction_lag={compaction_lag:.2f}"
                ),
                weight=score,
            )
        ]

        return [
            DetectedPattern(
                pattern_id=self._id("TEMPORAL_LOOP", str(len(events))),
                kind="TEMPORAL_LOOP",
                name="Temporal anomaly / agent loop",
                confidence=score,
                severity=clamp01(0.55 + score * 0.35),
                recurrence=repeated_action_rate,
                semantic_distance=0.0,
                temporal_anomaly=score,
                safety_risk=0.35,
                memory_risk=clamp01(0.40 + compaction_lag * 0.40),
                affected_paths=[],
                evidence=evidence,
                hypothesis="The agent appears to be cycling without sufficient validated progress.",
                proposed_rule="Pause execution, compact session, re-run cold planning with blocker analysis.",
                recommended_action="PAUSE_AND_REPLAN",
                coldplanner_metrics={
                    "impact_on_mvp": 0.60,
                    "risk_reduction": 0.90,
                    "unblock_future_loops": 0.85,
                    "testability": 0.60,
                    "implementation_cost_inverse": 0.80,
                    "reversibility": 0.90,
                    "risk": 0.50,
                    "temporal_loop": score,
                    "memory_risk": clamp01(0.40 + compaction_lag * 0.40),
                },
            )
        ]

    def _repeated_action_rate(self, events: list[dict[str, Any]], window: int = 8) -> float:
        recent = events[-window:]
        actions = [
            ev.get("data", {}).get("recommended_action")
            or ev.get("data", {}).get("selected_action")
            or ev.get("event_type")
            for ev in recent
        ]
        actions = [str(a) for a in actions if a]
        if not actions:
            return 0.0
        return max(actions.count(a) for a in set(actions)) / len(actions)

    def _validation_oscillation(self, events: list[dict[str, Any]], window: int = 12) -> float:
        recent = [
            ev for ev in events[-window:]
            if ev.get("event_type") in {"VALIDATION", "VALIDATION_RECORDED"}
        ]
        statuses = [
            str(ev.get("data", {}).get("status") or ev.get("status") or "").upper()
            for ev in recent
        ]
        statuses = [s for s in statuses if s in {"PASS", "FAIL", "BLOCKED"}]
        if len(statuses) < 4:
            return 0.0
        flips = sum(1 for a, b in zip(statuses, statuses[1:]) if a != b)
        return flips / (len(statuses) - 1)

    def _no_progress_ratio(self, events: list[dict[str, Any]], window: int = 10) -> float:
        recent = events[-window:]
        if not recent:
            return 0.0
        progress_events = {
            "PATCH_APPLIED",
            "TEST_ADDED",
            "VALIDATION_PASS",
            "ARTIFACT_CREATED",
            "MEMORY_COMMIT",
        }
        progress = sum(1 for ev in recent if ev.get("event_type") in progress_events)
        return 1.0 - progress / len(recent)

    def _blocker_recurrence(self, events: list[dict[str, Any]], window: int = 12) -> float:
        recent = events[-window:]
        blockers = [
            ev.get("data", {}).get("blocker")
            or ev.get("data", {}).get("reason")
            for ev in recent
            if ev.get("event_type") in {"BLOCKED", "VALIDATION", "NEXT_LOOP"}
        ]
        blockers = [str(b) for b in blockers if b]
        if not blockers:
            return 0.0
        return max(blockers.count(b) for b in set(blockers)) / len(blockers)

    def _compaction_lag(
        self,
        events: list[dict[str, Any]],
        session_artifacts: list[dict[str, Any]],
    ) -> float:
        has_compact = any(
            "compact" in str(artifact.get("path") or artifact.get("name") or "").lower()
            for artifact in session_artifacts
        )
        if has_compact:
            return 0.0
        return clamp01(len(events) / 100)

    def _id(self, kind: str, key: str) -> str:
        digest = hashlib.sha256(f"{kind}:{key}".encode("utf-8")).hexdigest()[:12]
        return f"{kind.lower()}_{digest}"
