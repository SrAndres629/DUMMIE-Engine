from __future__ import annotations

import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

logger = logging.getLogger(__name__)

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")

_FORBIDDEN_PATTERNS = [
    (re.compile(r"\.env\s*[=:]", re.I), "forbidden .env assignment"),
    (re.compile(r"secret\s*(is|[:=])", re.I), "forbidden secret value"),
    (re.compile(r"credential\s*(is|[:=])", re.I), "forbidden credential value"),
    (re.compile(r"token\s*[=:]", re.I), "forbidden token assignment"),
    (re.compile(r"password\s*[=:]", re.I), "forbidden password assignment"),
    (re.compile(r"chain_of_thought", re.I), "private reasoning"),
    (re.compile(r"private reasoning", re.I), "private reasoning"),
    (re.compile(r"private_reasoning", re.I), "private reasoning"),
]

MINIMUM_ARTIFACTS = {
    "objective.md",
    "user_order.md",
    "task_graph.yaml",
    "assumptions.json",
    "context_packet.json",
    "tool_plan.yaml",
    "decision_log.jsonl",
    "validation_report.md",
    "outcome_metrics.json",
    "learning_episode.json",
    "token_budget.json",
    "final_summary.md",
}


class MissionWorkbenchManager:
    def __init__(
        self,
        root: str | Path = ".aiwg/workbench",
        phase_ledger: Any = None,
        budget_manager: Any = None,
    ):
        self.root = Path(root)
        self.phase_ledger = phase_ledger
        self.budget_manager = budget_manager

    def create_workbench(self, mission_id: str, user_goal: str, phase_id: str = "") -> dict:
        self._validate_id("mission_id", mission_id)
        if phase_id:
            self._validate_id("phase_id", phase_id)

        target_dir = self._workbench_dir(mission_id)
        target_dir.mkdir(parents=True, exist_ok=True)

        self._write_text(target_dir / "objective.md", f"# Mission Objective\n\n{user_goal}\n")
        self._write_text(target_dir / "user_order.md", "# User Order\n\n(Initial order text)\n")
        self._write_text(target_dir / "task_graph.yaml", "tasks: []\n")
        self._write_json(target_dir / "assumptions.json", {"assumptions": []})
        self._write_json(target_dir / "context_packet.json", {"items": []})
        self._write_text(target_dir / "tool_plan.yaml", "tools: []\n")

        # decision_log.jsonl is created empty
        (target_dir / "decision_log.jsonl").touch()

        self._write_text(target_dir / "validation_report.md", "# Validation Report\n\n")
        self._write_json(target_dir / "outcome_metrics.json", {"metrics": {}})
        self._write_json(target_dir / "learning_episode.json", {"mission_id": mission_id})

        # Integration with Token Economy
        budget_info = {
            "mission_id": mission_id,
            "phase_id": phase_id,
        }
        if self.budget_manager:
            # We assume a default tier or current session tier if we could get it
            budget = self.budget_manager.allocate_budget("local_fast")
            budget_info.update({
                "budget_source": "ContextBudgetManager",
                "total_budget": budget.get("total_budget"),
                "token_ledger_ref": f".aiwg/missions/{mission_id}/token_cost_ledger.jsonl",
                "budget_pressure": "low", # Initial
            })
        else:
            budget_info.update({
                "budget_source": "unavailable",
                "budget_pressure": "unknown",
            })
        self._write_json(target_dir / "token_budget.json", budget_info)

        self._write_text(target_dir / "final_summary.md", "# Final Summary\n\n")

        meta = {
            "mission_id": mission_id,
            "user_goal": user_goal,
            "phase_id": phase_id,
            "created_at": _now(),
            "status": "active",
            "workbench_ref": str(target_dir) + "/",
        }
        self._write_json(target_dir / "workbench_metadata.json", meta)

        if self.phase_ledger:
            self.phase_ledger.append_event(mission_id, {
                "event_type": "WORKBENCH_CREATED",
                "phase_id": phase_id,
                "workbench_ref": meta["workbench_ref"],
            })

        return meta

    def write_artifact(self, mission_id: str, name: str, content: str, kind: str) -> dict:
        self._validate_id("mission_id", mission_id)
        # Artifact name might have dots but should be safe
        if ".." in name or "/" in name or "\\" in name:
             raise ValueError("Artifact name rejected: path traversal is not allowed")

        target_path = self._workbench_dir(mission_id) / name

        if name.endswith(".json"):
            try:
                payload = json.loads(content)
                self._write_json(target_path, payload)
            except json.JSONDecodeError:
                self._write_text(target_path, content)
        else:
            self._write_text(target_path, content)

        artifact = {
            "name": name,
            "kind": kind,
            "ref": str(target_path),
            "created_at": _now(),
        }

        if self.phase_ledger:
            self.phase_ledger.append_event(mission_id, {
                "event_type": "WORKBENCH_ARTIFACT_WRITTEN",
                "artifact": artifact,
            })

        return artifact

    def read_artifact(self, mission_id: str, name: str) -> dict:
        self._validate_id("mission_id", mission_id)
        path = self._workbench_dir(mission_id) / name
        if not path.exists():
            raise FileNotFoundError(f"Artifact {name} not found in workbench {mission_id}")

        content = path.read_text(encoding="utf-8")
        return {
            "name": name,
            "content": content,
            "ref": str(path),
        }

    def append_decision(self, mission_id: str, event: dict) -> dict:
        self._validate_id("mission_id", mission_id)
        self._reject_private(event)

        normalized = {
            "event_id": event.get("event_id") or f"dec-{uuid.uuid4().hex}",
            "timestamp": event.get("timestamp") or _now(),
            "claim": str(event.get("claim", "")),
            "evidence": list(event.get("evidence", []) or []),
            "objection": str(event.get("objection", "")),
            "decision": str(event.get("decision", "")),
            "required_test": str(event.get("required_test", "")),
            "next_action": str(event.get("next_action", "")),
        }

        log_path = self._workbench_dir(mission_id) / "decision_log.jsonl"
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(normalized, ensure_ascii=True, sort_keys=True) + "\n")
            handle.flush()
            try:
                os.fsync(handle.fileno())
            except OSError:
                pass

        return normalized

    def list_artifacts(self, mission_id: str) -> list[dict]:
        self._validate_id("mission_id", mission_id)
        target_dir = self._workbench_dir(mission_id)
        if not target_dir.exists():
            return []

        artifacts = []
        for item in target_dir.iterdir():
            if item.is_file() and not item.name.startswith("."):
                artifacts.append({
                    "name": item.name,
                    "ref": str(item),
                    "size": item.stat().st_size,
                })
        return artifacts

    def summarize_workbench(self, mission_id: str) -> dict:
        self._validate_id("mission_id", mission_id)
        artifacts = self.list_artifacts(mission_id)

        # Read decision log count
        decision_count = 0
        log_path = self._workbench_dir(mission_id) / "decision_log.jsonl"
        if log_path.exists():
            with log_path.open("r", encoding="utf-8") as h:
                decision_count = sum(1 for line in h if line.strip())

        return {
            "mission_id": mission_id,
            "artifact_count": len(artifacts),
            "decision_count": decision_count,
            "artifacts": artifacts,
        }

    def finalize_workbench(self, mission_id: str, outcome: dict) -> dict:
        self._validate_id("mission_id", mission_id)
        target_dir = self._workbench_dir(mission_id)
        meta_path = target_dir / "workbench_metadata.json"

        if not meta_path.exists():
             raise FileNotFoundError(f"Workbench metadata not found for {mission_id}")

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["status"] = "finalized"
        meta["finalized_at"] = _now()
        meta["outcome_summary"] = outcome.get("status", "unknown")

        self._write_json(meta_path, meta)

        self._write_json(target_dir / "outcome_metrics.json", outcome.get("metrics", {}))

        if self.phase_ledger:
            self.phase_ledger.append_event(mission_id, {
                "event_type": "WORKBENCH_FINALIZED",
                "outcome_status": meta["outcome_summary"],
            })

        return meta

    def _workbench_dir(self, mission_id: str) -> Path:
        self._validate_id("mission_id", mission_id)
        root = self.root.resolve()
        target = (self.root / mission_id).resolve()
        if os.path.commonpath([str(root), str(target)]) != str(root):
            raise ValueError("mission_id rejected: path traversal is not allowed")
        return target

    def _validate_id(self, field_name: str, value: str) -> None:
        if not value or ".." in value or "/" in value or "\\" in value:
            raise ValueError(f"{field_name} rejected: path traversal is not allowed")
        if not _SAFE_ID.match(value):
            raise ValueError(
                f"{field_name} rejected: only letters, numbers, hyphen, and underscore are allowed"
            )

    def _reject_private(self, value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                self._reject_private(str(key))
                self._reject_private(item)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                self._reject_private(item)
        elif isinstance(value, str):
            for pattern, reason in _FORBIDDEN_PATTERNS:
                if pattern.search(value):
                    raise ValueError(f"workbench payload contains {reason}")

    def _write_json(self, path: Path, payload: dict) -> None:
        self._reject_private(payload)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f".{path.name}.tmp")
        content = json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
        tmp.write_text(content, encoding="utf-8")
        with tmp.open("a", encoding="utf-8") as h:
            h.flush()
            try:
                os.fsync(h.fileno())
            except OSError:
                pass
        tmp.replace(path)

    def _write_text(self, path: Path, payload: str) -> None:
        self._reject_private(payload)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f".{path.name}.tmp")
        tmp.write_text(payload, encoding="utf-8")
        with tmp.open("a", encoding="utf-8") as h:
            h.flush()
            try:
                os.fsync(h.fileno())
            except OSError:
                pass
        tmp.replace(path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
