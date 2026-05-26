"""Heartbeat Orchestrator — Autonomous dispatch from observation to execution.

Flow:
  1. Takes heartbeat's selected_action
  2. Classifies complexity via model_router
  3. If executable: creates worktree, writes task, waits for work
  4. Audits result with different model
  5. Merges (audit pass) or rollback (audit fail)
  6. Records outcome in heartbeat ledger

Production: Real git operations, real model calls for audit, real merges.
Token cost: Only audit phase uses cloud tokens if router says so; default local.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from heartbeat_worktree import WorktreeManager
from group_chat_coordinator import GroupChatCoordinator

logger = logging.getLogger(__name__)

AIWG_ROOT = Path("/opt/dummie-engine/.aiwg")


class HeartbeatOrchestrator:
    def __init__(self):
        self.worktree = WorktreeManager()
        self.coordinator = GroupChatCoordinator(AIWG_ROOT)
        self.state_file = AIWG_ROOT / "heartbeat" / "orchestrator_state.json"
        self.state = self._load_state()

    def dispatch(
        self,
        selected_action: dict,
        decision: str,
        dispatch_recommendation: str,
        blocked_actions: list,
    ) -> Dict[str, Any]:
        action_id = selected_action.get("action_id", "hb-unknown")
        action_type = selected_action.get("action_type", "unknown")

        logger.info("Orchestrator evaluating action: %s (%s)", action_id, action_type)

        can_execute, reason = self._can_execute(
            decision, dispatch_recommendation, blocked_actions, action_type
        )
        if not can_execute:
            logger.info("Action blocked: %s", reason)
            return {"status": "blocked", "reason": reason, "action_id": action_id}

        complexity = self._classify(action_type, selected_action)
        mode, model_id = self._select_mode_and_model(complexity)

        task_id = f"{action_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        instructions = self._build_instructions(
            selected_action, action_type, complexity
        )

        wt_state = self.worktree.create(task_id, instructions[:100])
        if wt_state.get("status") != "created":
            return {
                "status": "failed",
                "reason": "Worktree creation failed",
                "action_id": action_id,
                "error": wt_state.get("error"),
            }

        self.worktree.write_task_file(task_id, instructions, mode, model_id)

        self.state["active_task"] = {
            "task_id": task_id,
            "action_id": action_id,
            "action_type": action_type,
            "mode": mode,
            "model": model_id,
            "complexity": complexity,
            "worktree_path": wt_state.get("worktree_path"),
            "dispatched_at": datetime.now().isoformat(),
            "status": "executing",
        }
        self._save_state()

        logger.info(
            "Dispatched %s: mode=%s model=%s complexity=%s",
            task_id,
            mode,
            model_id,
            complexity,
        )

        return {
            "status": "dispatched",
            "task_id": task_id,
            "action_id": action_id,
            "mode": mode,
            "model": model_id,
            "complexity": complexity,
            "worktree_path": wt_state.get("worktree_path"),
            "task_file": str(AIWG_ROOT / "tasks" / task_id / "task.md"),
            "instructions_summary": instructions[:300],
        }

    def check_and_audit(self) -> Optional[Dict[str, Any]]:
        active_task = self.state.get("active_task")
        if not active_task or active_task["status"] != "executing":
            return None

        task_id = active_task["task_id"]
        if not self.worktree.is_work_done(task_id):
            return None

        logger.info("Work detected on %s, running audit...", task_id)
        active_task["status"] = "auditing"
        self._save_state()

        audit_result = self.worktree.audit(task_id)

        if audit_result.get("passed"):
            merge_result = self.worktree.merge(task_id)
            if merge_result.get("merged"):
                active_task["status"] = "completed"
                active_task["completed_at"] = datetime.now().isoformat()
                self._record_outcome("completed", active_task)
                logger.info("Task %s: COMPLETED (audited + merged)", task_id)
                self._save_state()
                return {"status": "completed", **active_task}
            else:
                active_task["status"] = "merge_failed"
                active_task["merge_error"] = merge_result.get("reason")
                self._save_state()
                return {"status": "merge_failed", **active_task}
        else:
            rollback_result = self.worktree.rollback(task_id)
            active_task["status"] = "rejected"
            active_task["audit_reason"] = audit_result.get("reason")
            self._record_outcome("rejected", active_task)
            logger.info("Task %s: REJECTED (audit failed)", task_id)
            self._save_state()
            return {"status": "rejected", **active_task}

    def active_task_status(self) -> Optional[Dict[str, Any]]:
        return self.state.get("active_task")

    def recently_completed(self, count: int = 5) -> list:
        outcomes_file = AIWG_ROOT / "heartbeat" / "orchestrator_outcomes.jsonl"
        if not outcomes_file.exists():
            return []
        outcomes = []
        for line in outcomes_file.read_text().strip().split("\n"):
            if line:
                outcomes.append(json.loads(line))
        return list(reversed(outcomes))[:count]

    SAFE_ACTIONS = {
        "generate_action_queue",
        "list",
        "status",
        "report",
        "generate",
        "index",
        "catalog",
        "audit",
        "scan",
        "classify",
        "categorize",
    }

    def _can_execute(
        self, decision: str, dispatch: str, blocked: list, action_type: str = ""
    ) -> tuple:
        at = action_type.lower()

        if any(safe in at for safe in self.SAFE_ACTIONS):
            return True, "Safe action — always allowed"

        if decision == "FAIL":
            return False, "Heartbeat decision is FAIL"
        if dispatch == "human_review":
            return False, "Dispatch recommends human_review"
        if blocked:
            for b in blocked:
                if "autonomous" in b:
                    return False, f"Autonomous action blocked: {b}"
        if "kuzu_degraded" in blocked:
            return False, "KuzuDB degraded — no writes possible"
        return True, "OK"

    def _classify(self, action_type: str, action: dict) -> str:
        critical_types = [
            "architect",
            "redesign",
            "migrate",
            "security",
            "cross-layer",
            "schema_change",
            "breaking_change",
            "merkle",
            "consensus",
            "repair_kuzu",
        ]
        complex_types = [
            "refactor",
            "multi-file",
            "integration",
            "pipeline",
            "orchestrator",
            "daemon",
            "transaction",
            "saga",
            "workflow",
            "deploy",
            "dependency",
        ]
        trivial_types = [
            "format",
            "lint",
            "typo",
            "comment",
            "rename",
            "log",
            "print",
            "status",
            "list",
            "show",
        ]

        at = action_type.lower()
        for ct in critical_types:
            if ct in at:
                return "CRITICAL"
        for ct in complex_types:
            if ct in at:
                return "COMPLEX"
        for ct in trivial_types:
            if ct in at:
                return "TRIVIAL"
        priority = action.get("priority", "medium")
        if priority == "critical":
            return "CRITICAL"
        elif priority == "low":
            return "ROUTINE"
        return "COMPLEX"

    def _select_mode_and_model(self, complexity: str) -> tuple:
        mapping = {
            "TRIVIAL": ("build", "ollama/qwen3.5:0.8b"),
            "ROUTINE": ("build", "ollama/smallthinker:3b"),
            "COMPLEX": ("plan", "ollama/gemma4:e4b"),
            "CRITICAL": ("plan", "ollama/gemma4:e4b"),
        }
        mode, model = mapping.get(complexity, ("plan", "ollama/smallthinker:3b"))
        if mode == "plan":
            model = "ollama/gemma4:e4b"
        return mode, model

    def _resolve_role_for_action(self, action_type: str, action: dict) -> str:
        description = action.get("description", action_type).lower()
        return self.coordinator.resolve_role(description)

    def _activate_group_chain(self, action: dict, action_type: str) -> dict:
        role = self._resolve_role_for_action(action_type, action)
        chain = self.coordinator.activate_role_chain(role)
        agent_configs = [self.coordinator.get_agent_config(r) for r in chain]

        group_state = self.coordinator.load_state()
        group_state["pipeline_status"] = "active"
        group_state["active_role"] = chain[0]
        group_state["pipeline_chain"] = chain
        self.coordinator.save_state(group_state)

        logger.info("Group chat chain activated: %s", " → ".join(chain))
        return {"status": "group_activated", "chain": chain, "entry_role": role}

    def _build_instructions(
        self, action: dict, action_type: str, complexity: str
    ) -> str:
        action_name = action_type.replace("_", " ").title()
        priority = action.get("priority", "medium")
        evidence = action.get("evidence_refs", [])
        context = ""
        if evidence:
            context = f"\nEvidence: {', '.join(evidence[:3])}"

        if complexity == "CRITICAL":
            scope = "This is a CRITICAL change. Plan thoroughly. Do NOT execute until plan is reviewed."
        elif complexity == "COMPLEX":
            scope = "This is a COMPLEX change. Think carefully about scope and impact."
        else:
            scope = "This is a routine change. Keep it simple and focused."

        return (
            f"Action: {action_name}\n"
            f"Priority: {priority}\n"
            f"Complexity: {complexity}\n"
            f"Scope: {scope}{context}\n\n"
            f"Execute this action in the worktree. Commit with a meaningful message. "
            f"When done, the system will automatically audit and merge."
        )

    def _record_outcome(self, status: str, task: dict):
        outcomes_file = AIWG_ROOT / "heartbeat" / "orchestrator_outcomes.jsonl"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            **{
                k: v
                for k, v in task.items()
                if k
                in (
                    "task_id",
                    "action_id",
                    "action_type",
                    "mode",
                    "model",
                    "complexity",
                    "worktree_path",
                    "dispatched_at",
                )
            },
        }
        with open(outcomes_file, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    def _load_state(self) -> dict:
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {"active_task": None}

    def _save_state(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2, default=str))


def run_orchestrator_cycle():
    heartbeats_dir = AIWG_ROOT / "heartbeat"
    latest_hb = heartbeats_dir / "latest_heartbeat.json"
    if not latest_hb.exists():
        logger.warning("No heartbeat data — skipping orchestration")
        return {"status": "skipped", "reason": "No heartbeat data"}

    hb = json.loads(latest_hb.read_text())
    decision = hb.get("decision", "UNKNOWN")
    dispatch = hb.get("dispatch_recommendation", "human_review")
    blocked = hb.get("blocked_actions", [])
    selected_action = hb.get("selected_action")

    if not selected_action:
        return {"status": "skipped", "reason": "No selected action"}

    orchestrator = HeartbeatOrchestrator()

    existing = orchestrator.active_task_status()
    if existing and existing["status"] in ("executing", "auditing"):
        audit_result = orchestrator.check_and_audit()
        if audit_result:
            return audit_result
        return {"status": "waiting", "active_task": existing}

    result = orchestrator.dispatch(selected_action, decision, dispatch, blocked)
    return result


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    result = run_orchestrator_cycle()
    print(json.dumps(result, indent=2, default=str))
