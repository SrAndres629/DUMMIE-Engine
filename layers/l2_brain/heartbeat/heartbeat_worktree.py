"""Heartbeat Worktree Manager — Git worktree isolation with multi-model audit.

Production: Creates real git worktrees for isolated execution.
Audit: Uses a different local model to review changes before merge.
Safety: Never merges to main unless audit passes.
"""

import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

AIWG_ROOT = Path("/opt/dummie-engine/.aiwg")
REPO_PATH = Path("/media/datasets/DUMMIE Engine")
WORKTREE_BASE = REPO_PATH / "worktrees"


class WorktreeManager:
    """Git worktree isolation manager.

    Flow:
    1. create(task_id) → creates isolated worktree
    2. is_work_done() → checks for commits
    3. audit() → reviews diff with local model
    4. merge_or_rollback() → merges to main OR cleans up
    """

    def __init__(self):
        self.state_dir = AIWG_ROOT / "worktrees"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def create(self, task_id: str, task_description: str) -> Dict[str, Any]:
        branch_name = f"worktree/{task_id}"
        worktree_path = WORKTREE_BASE / task_id

        try:
            existing = subprocess.run(
                ["git", "worktree", "list"],
                capture_output=True,
                text=True,
                cwd=REPO_PATH,
                timeout=10,
            )
            if str(worktree_path) in existing.stdout:
                logger.info("Worktree already exists: %s", worktree_path)
                return self._load_state(task_id)

            result = subprocess.run(
                [
                    "git",
                    "worktree",
                    "add",
                    "-b",
                    branch_name,
                    str(worktree_path),
                    "main",
                ],
                capture_output=True,
                text=True,
                cwd=REPO_PATH,
                timeout=60,
            )
            if result.returncode != 0:
                logger.error("Worktree creation failed: %s", result.stderr)
                return {"status": "failed", "error": result.stderr.strip()}

            state = {
                "task_id": task_id,
                "branch": branch_name,
                "worktree_path": str(worktree_path),
                "description": task_description,
                "status": "created",
                "created_at": datetime.now().isoformat(),
                "audit_passed": None,
                "merged_at": None,
            }
            self._save_state(task_id, state)
            logger.info("Worktree created: %s", worktree_path)
            return state

        except Exception as e:
            logger.exception("Worktree creation error: %s", e)
            return {"status": "failed", "error": str(e)}

    def is_work_done(self, task_id: str) -> bool:
        state = self._load_state(task_id)
        if not state or state["status"] != "created":
            return False
        worktree_path = Path(state["worktree_path"])
        if not worktree_path.exists():
            return False
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", f"main..{state['branch']}"],
                capture_output=True,
                text=True,
                cwd=REPO_PATH,
                timeout=10,
            )
            has_commits = bool(result.stdout.strip())
            if has_commits:
                state["status"] = "work_done"
                state["commits"] = result.stdout.strip().split("\n")
                self._save_state(task_id, state)
            return has_commits
        except Exception as e:
            logger.error("is_work_done check failed: %s", e)
            return False

    def get_diff(self, task_id: str) -> str:
        state = self._load_state(task_id)
        if not state:
            return ""
        try:
            result = subprocess.run(
                ["git", "diff", f"main...{state['branch']}"],
                capture_output=True,
                text=True,
                cwd=REPO_PATH,
                timeout=30,
            )
            return result.stdout[:50000]
        except Exception:
            return ""

    def audit(self, task_id: str) -> Dict[str, Any]:
        state = self._load_state(task_id)
        if not state or state["status"] not in ("work_done", "auditing"):
            return {"passed": False, "reason": "Worktree not ready for audit"}

        diff = self.get_diff(task_id)
        if not diff.strip():
            return {"passed": False, "reason": "No changes to audit"}

        state["status"] = "auditing"
        self._save_state(task_id, state)

        try:
            import httpx

            audit_prompt = (
                "You are DUMMIE Audit Engine. Review the following git diff.\n\n"
                "CRITERIA:\n"
                "1. Does this introduce security risks?\n"
                "2. Does it follow existing code patterns?\n"
                "3. Are there any obvious bugs?\n"
                "4. Is the change minimal and focused?\n\n"
                "Respond with PASS or FAIL followed by a brief reason.\n\n"
                f"DIFF:\n{diff[:15000]}"
            )

            r = httpx.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "smallthinker:3b",
                    "prompt": audit_prompt,
                    "stream": False,
                    "options": {"num_predict": 500},
                },
                timeout=120,
            )
            if r.status_code == 200:
                audit_result = r.json().get("response", "").strip()
                passed = audit_result.upper().startswith("PASS")
                state["audit_passed"] = passed
                state["audit_reason"] = audit_result[:500]
                state["audit_at"] = datetime.now().isoformat()
                self._save_state(task_id, state)
                logger.info("Audit %s: %s", "PASSED" if passed else "FAILED", task_id)
                return {"passed": passed, "reason": audit_result[:500]}
            else:
                return {"passed": False, "reason": f"Ollama error: {r.status_code}"}
        except Exception as e:
            logger.error("Audit model call failed: %s", e)
            return {"passed": False, "reason": f"Audit model error: {e}"}

    def merge(self, task_id: str) -> Dict[str, Any]:
        state = self._load_state(task_id)
        if not state or not state.get("audit_passed"):
            return {"merged": False, "reason": "Audit must pass before merge"}

        try:
            subprocess.run(
                ["git", "checkout", "main"],
                capture_output=True,
                text=True,
                cwd=REPO_PATH,
                timeout=15,
            )
            result = subprocess.run(
                [
                    "git",
                    "merge",
                    "--no-ff",
                    state["branch"],
                    "-m",
                    f"merge: {task_id} (audited)",
                ],
                capture_output=True,
                text=True,
                cwd=REPO_PATH,
                timeout=30,
            )
            if result.returncode == 0:
                state["status"] = "merged"
                state["merged_at"] = datetime.now().isoformat()
                self._save_state(task_id, state)
                logger.info("Merged worktree %s to main", task_id)
                return {"merged": True, "reason": result.stdout.strip()}
            else:
                return {"merged": False, "reason": result.stderr.strip()}
        except Exception as e:
            return {"merged": False, "reason": str(e)}

    def rollback(self, task_id: str) -> Dict[str, Any]:
        state = self._load_state(task_id)
        if not state:
            return {"rolled_back": False, "reason": "No state found"}
        try:
            subprocess.run(
                ["git", "checkout", "main"],
                capture_output=True,
                text=True,
                cwd=REPO_PATH,
                timeout=15,
            )
            subprocess.run(
                ["git", "worktree", "remove", "--force", state["worktree_path"]],
                capture_output=True,
                text=True,
                cwd=REPO_PATH,
                timeout=30,
            )
            subprocess.run(
                ["git", "branch", "-D", state["branch"]],
                capture_output=True,
                text=True,
                cwd=REPO_PATH,
                timeout=10,
            )
            state["status"] = "rolled_back"
            self._save_state(task_id, state)
            logger.info("Rolled back worktree %s", task_id)
            return {"rolled_back": True, "reason": "Rolled back"}
        except Exception as e:
            return {"rolled_back": False, "reason": str(e)}

    def list_active(self) -> List[Dict[str, Any]]:
        active = []
        for state_file in sorted(self.state_dir.glob("*.json")):
            state = json.loads(state_file.read_text())
            if state.get("status") not in ("merged", "rolled_back"):
                active.append(state)
        return active

    def write_task_file(
        self, task_id: str, instructions: str, mode: str, model_id: str
    ) -> Path:
        task_dir = AIWG_ROOT / "tasks" / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        task_file = task_dir / "task.md"
        content = (
            f"# Task: {task_id}\n\n"
            f"**Mode:** {mode}\n"
            f"**Model:** {model_id}\n"
            f"**Worktree:** {task_id}\n\n"
            f"## Instructions\n\n{instructions}\n\n"
            f"## Acceptance Criteria\n\n"
            f"- Changes are in worktree branch `worktree/{task_id}`\n"
            f"- At least one commit with meaningful message\n"
            f"- No secrets or keys in diff\n\n"
            f"## Status\n\n"
            f"- [ ] Work started\n"
            f"- [ ] Commits pushed to worktree\n"
            f"- [ ] Audit requested\n"
        )
        task_file.write_text(content)
        return task_file

    def _save_state(self, task_id: str, state: dict):
        (self.state_dir / f"{task_id}.json").write_text(json.dumps(state, indent=2))

    def _load_state(self, task_id: str) -> Optional[dict]:
        state_file = self.state_dir / f"{task_id}.json"
        if state_file.exists():
            return json.loads(state_file.read_text())
        return None
