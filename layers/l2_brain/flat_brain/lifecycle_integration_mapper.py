from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class LifecycleNode:
    name: str
    description: str
    layer: str
    file_path: str
    status: str  # OK|MISSING|DEGRADED
    dependencies: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LifecycleMap:
    nodes: list[LifecycleNode]
    data_flow_integrity: str  # SEALED|LEAKY|BROKEN
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LifecycleIntegrationMapper:
    def __init__(self, repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg"):
        self.repo_root = Path(repo_root).resolve()
        self.aiwg_root = self.repo_root / aiwg_root
        self.reports_root = self.aiwg_root / "reports"

    def run_mapping(self) -> dict[str, Any]:
        nodes = [
            LifecycleNode(
                "SENSORY_INPUT",
                "Ingesta de prompt y clasificación de intención",
                "L2",
                "layers/l2_brain/prompt_to_mission.py",
                self._check_file("layers/l2_brain/prompt_to_mission.py"),
                ["mission_planner.py"]
            ),
            LifecycleNode(
                "MISSION_PLANNING",
                "Descomposición de tareas en Mission DAG",
                "L2",
                "layers/l2_brain/mission_planner.py",
                self._check_file("layers/l2_brain/mission_planner.py"),
                ["daemon.py"]
            ),
            LifecycleNode(
                "EXECUTIVE_DAEMON",
                "Ejecución de misiones y gestión de herramientas",
                "L2",
                "layers/l2_brain/daemon.py",
                self._check_file("layers/l2_brain/daemon.py"),
                ["outcome_evaluator.py", "learning_episode.py"]
            ),
            LifecycleNode(
                "OUTCOME_EVALUATION",
                "Validación de resultados vs objetivos",
                "L2",
                "layers/l2_brain/outcome_evaluator.py",
                self._check_file("layers/l2_brain/outcome_evaluator.py"),
                ["learning_episode.py"]
            ),
            LifecycleNode(
                "LEARNING_PERSISTENCE",
                "Cierre de episodio de aprendizaje y guardado en 4D-TES",
                "L2",
                "layers/l2_brain/learning_episode.py",
                self._check_file("layers/l2_brain/learning_episode.py"),
                ["session_store.py"]
            ),
            LifecycleNode(
                "COGNITIVE_MEMORY",
                "Almacenamiento causal inmutable",
                "L2",
                "layers/l2_brain/session_store.py",
                self._check_file("layers/l2_brain/session_store.py"),
                []
            )
        ]

        # Basic integrity check
        all_ok = all(n.status == "OK" for n in nodes)
        integrity = "SEALED" if all_ok else "LEAKY"
        if any(n.status == "MISSING" for n in nodes):
            integrity = "BROKEN"

        lifecycle_map = LifecycleMap(
            nodes=nodes,
            data_flow_integrity=integrity,
            generated_at=self._utc_now()
        )

        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "lifecycle_integration_latest.json").write_text(
            json.dumps(lifecycle_map.to_dict(), indent=2) + "\n", encoding="utf-8"
        )
        
        return lifecycle_map.to_dict()

    def _check_file(self, rel_path: str) -> str:
        if (self.repo_root / rel_path).exists():
            return "OK"
        return "MISSING"

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_lifecycle_mapping(repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    mapper = LifecycleIntegrationMapper(repo_root=repo_root, aiwg_root=aiwg_root)
    return mapper.run_mapping()


if __name__ == "__main__":
    run_lifecycle_mapping()
