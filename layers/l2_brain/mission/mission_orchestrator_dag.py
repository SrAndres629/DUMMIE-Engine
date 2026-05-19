from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class DAGNode:
    node_id: str
    node_type: str  # L1|L2|L3|validation|report|commit
    title: str
    status: str = "pending"  # pending|ready|running|blocked|done|failed|skipped
    depends_on: list[str] = field(default_factory=list)
    produces: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    risk_level: str = "low"
    evidence_refs: list[str] = field(default_factory=list)


@dataclass
class MissionDAG:
    mission_id: str
    nodes: dict[str, DAGNode] = field(default_factory=dict)
    decision: str = "PASS"
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "nodes": {k: asdict(v) for k, v in self.nodes.items()},
            "decision": self.decision,
            "generated_at": self.generated_at,
        }


class MissionOrchestratorDAG:
    def __init__(self, root: str | Path = "."):
        self.root = Path(root)
        self.aiwg_root = self.root / ".aiwg"
        self.reports_root = self.aiwg_root / "reports"

    def build_dag_from_mission_plan(self, plan: Any) -> MissionDAG:
        nodes: dict[str, DAGNode] = {}
        
        # Root node
        nodes["START"] = DAGNode("START", "L1", f"Start {plan.mission_id}")
        nodes["START"].status = "ready"

        # Map L2 phases
        last_l2 = "START"
        for l2 in plan.l2_phases:
            node = DAGNode(
                node_id=l2.phase_id,
                node_type="L2",
                title=l2.title,
                depends_on=[last_l2],
                produces=l2.outputs
            )
            nodes[l2.phase_id] = node
            
            # Map L3 microphases
            last_l3 = last_l2
            for l3 in plan.l3_microphases:
                if l3.parent_phase_id == l2.phase_id:
                    m_node = DAGNode(
                        node_id=l3.microphase_id,
                        node_type="L3",
                        title=l3.title,
                        depends_on=[last_l3],
                        produces=l3.expected_file_changes,
                        tests=l3.tests_to_run
                    )
                    nodes[l3.microphase_id] = m_node
                    last_l3 = l3.microphase_id
            
            # Close L2 phase depends on its last L3
            node.depends_on = [last_l3]
            last_l2 = l2.phase_id

        # Final node
        nodes["END"] = DAGNode("END", "validation", "Final Mission Validation", depends_on=[last_l2])

        dag = MissionDAG(
            mission_id=plan.mission_id,
            nodes=nodes,
            generated_at=self._utc_now()
        )
        
        # Cycle detection
        if self._has_cycle(dag):
            dag.decision = "FAIL"
            
        return dag

    def _has_cycle(self, dag: MissionDAG) -> bool:
        visited = set()
        stack = set()
        
        def visit(node_id):
            if node_id in stack:
                return True
            if node_id in visited:
                return False
            
            stack.add(node_id)
            for dep in dag.nodes.get(node_id, DAGNode("", "", "")).depends_on:
                if visit(dep):
                    return True
            stack.remove(node_id)
            visited.add(node_id)
            return False

        for n_id in dag.nodes:
            if visit(n_id):
                return True
        return False

    def select_next_executable_node(self, dag: MissionDAG) -> DAGNode | None:
        for node in dag.nodes.values():
            if node.status in ["pending", "ready"]:
                # Check if all dependencies are done
                all_done = True
                for dep_id in node.depends_on:
                    dep = dag.nodes.get(dep_id)
                    if not dep or dep.status != "done":
                        all_done = False
                        break
                if all_done:
                    return node
        return None

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def write_dag(self, dag: MissionDAG) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "mission_orchestrator_dag_latest.json").write_text(
            json.dumps(dag.to_dict(), indent=2) + "\n", encoding="utf-8"
        )
        
        next_node = self.select_next_executable_node(dag)
        next_payload = {"next_node": asdict(next_node) if next_node else None, "generated_at": self._utc_now()}
        (self.reports_root / "next_executable_node_latest.json").write_text(
            json.dumps(next_payload, indent=2) + "\n", encoding="utf-8"
        )


def build_dag_from_mission_plan(plan: Any, root: str | Path = ".") -> MissionDAG:
    orchestrator = MissionOrchestratorDAG(root=root)
    dag = orchestrator.build_dag_from_mission_plan(plan)
    orchestrator.write_dag(dag)
    return dag


if __name__ == "__main__":
    from mission_planner import create_mission_plan
    plan = create_mission_plan()
    dag = build_dag_from_mission_plan(plan)
    print(f"Built DAG with {len(dag.nodes)} nodes")
