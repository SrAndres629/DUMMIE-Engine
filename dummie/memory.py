from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from dummie.paths import AIWG


class DummieMemory:
    def __init__(self):
        self.identity_dir = AIWG / "identity"
        self.identity_dir.mkdir(parents=True, exist_ok=True)
        self.goal_memory_path = self.identity_dir / "goal_memory.yaml"
        self.project_memory_path = self.identity_dir / "project_memory.yaml"

    def load_goal_memory(self) -> dict[str, Any]:
        return self._load_yaml(self.goal_memory_path, default={"goals": []})

    def load_project_memory(self) -> dict[str, Any]:
        return self._load_yaml(self.project_memory_path, default={"projects": []})

    def append_goal(self, goal_entry: dict[str, Any]) -> dict[str, Any]:
        data = self.load_goal_memory()
        goals = data.get("goals", [])
        if not isinstance(goals, list):
            goals = []

        if not any(
            isinstance(item, dict)
            and item.get("goal") == goal_entry.get("goal")
            and item.get("goal_type") == goal_entry.get("goal_type")
            for item in goals
        ):
            goals.append(goal_entry)
        data["goals"] = goals
        self.goal_memory_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        return data

    def status(self) -> dict[str, Any]:
        goals = self.load_goal_memory().get("goals", [])
        projects = self.load_project_memory().get("projects", [])
        return {
            "goal_count": len(goals) if isinstance(goals, list) else 0,
            "project_count": len(projects) if isinstance(projects, list) else 0,
            "goal_memory_path": str(self.goal_memory_path),
            "project_memory_path": str(self.project_memory_path),
        }

    @staticmethod
    def _load_yaml(path: Path, default: dict[str, Any]) -> dict[str, Any]:
        if not path.exists():
            return default
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
            return default
        except Exception:
            return default
