# Spec 125: Mission Orchestrator DAG

## Purpose
Convert mission plans into Directed Acyclic Graphs (DAGs) to govern execution order and dependency tracking.

## Scope
- Topological sorting of nodes.
- Cycle detection.
- Dependency tracking between phases (L2) and microphases (L3).
- Next executable node selection.

## Runtime Behavior
1. Read a `MissionPlan`.
2. Create DAG nodes for L1, L2, and L3 elements.
3. Link nodes based on sequential dependencies and parent relationships.
4. Perform cycle detection.
5. Identify nodes that are "ready" (all dependencies "done").
6. Produce `mission_orchestrator_dag_latest.json`.

## Safety Rules
- Fail if a cycle is detected.
- Do not grant mutation authority; this is a coordination layer.
