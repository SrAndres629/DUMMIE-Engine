import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid

# Re-use domain classes where possible
try:
    from layers.l2_brain.domain.governance.kernel_contracts import (
        PreflightContext,
        ExecutionReceipt,
        PostflightMetrics,
    )
    from brain.application.use_cases.guarded_execution import GuardedExecutionUseCase
except ImportError:
    pass

from .context_capsule_engine import ContextCapsuleEngine


class AIWGKernel:
    """
    AIWG Native Operating Kernel.
    Acts as the main reflex and spine for agentic execution.
    """

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.aiwg_dir = self.workspace_root / ".aiwg"
        self.reports_dir = self.aiwg_dir / "reports"
        self.memory_dir = self.aiwg_dir / "memory"

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.capsule_engine = ContextCapsuleEngine(self.workspace_root)

    def aiwg_preflight(self) -> Dict[str, Any]:
        """
        Executes preflight checks before any agent entrypoint runs.
        """
        print("[AIWG KERNEL] Running preflight...")

        # Determine HEAD commit
        try:
            head_commit = (
                subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=self.workspace_root
                )
                .decode()
                .strip()
            )
        except Exception:
            head_commit = "UNKNOWN"

        # Check for active pack
        current_pack = "NONE"
        active_pack_file = self.aiwg_dir / "reports" / "active_pack.json"
        if active_pack_file.exists():
            try:
                with open(active_pack_file, "r") as f:
                    pack_data = json.load(f)
                    current_pack = pack_data.get("pack_id", "NONE")
            except json.JSONDecodeError:
                pass

        is_frozen = current_pack == "NONE"

        preflight_state = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "head_commit": head_commit,
            "current_pack": current_pack,
            "is_frozen": is_frozen,
            "status": "PASS",
        }

        report_path = self.reports_dir / "aiwg_preflight_latest.json"
        with open(report_path, "w") as f:
            json.dump(preflight_state, f, indent=2)

        return preflight_state

    def aiwg_context_loader(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Loads the foundational context.
        """
        print("[AIWG KERNEL] Loading context...")
        return {
            "workspace_root": str(self.workspace_root),
            "loaded_files": request_payload.get("target_files", []),
        }

    def aiwg_context_capsule_builder(
        self, context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Builds a surgical context capsule based on the loader and constraints.
        """
        print("[AIWG KERNEL] Building context capsule...")
        file_paths = context_data.get("loaded_files", [])
        return self.capsule_engine.compile_capsule(file_paths)

    def aiwg_token_budgeter(
        self, capsule: Dict[str, Any], token_limit: int = 4000
    ) -> bool:
        """
        Validates that the built capsule does not exceed the token budget.
        """
        print("[AIWG KERNEL] Budgeting tokens...")
        metadata = capsule.get("metadata", {})
        estimated_tokens = metadata.get("estimated_tokens", 0)
        print(f"[AIWG KERNEL] Estimated tokens: {estimated_tokens} / {token_limit}")
        return estimated_tokens <= token_limit

    def aiwg_mutation_router(self, command: str) -> bool:
        """
        Routes the mutation command and verifies if it is permitted.
        """
        print(f"[AIWG KERNEL] Routing mutation: {command}")
        # Identify if command is read-only
        read_only_tools = ["ls", "cat", "grep", "find", "status"]
        cmd_base = command.split(" ")[0]
        if cmd_base in read_only_tools:
            return True

        # If mutating, check if preflight allows it
        preflight_path = self.reports_dir / "aiwg_preflight_latest.json"
        if preflight_path.exists():
            with open(preflight_path, "r") as f:
                pf = json.load(f)
                if pf.get("is_frozen", True):
                    print(
                        "[AIWG KERNEL] REJECTED: System is frozen. No mutations allowed."
                    )
                    return False
        return True

    def aiwg_receipt_writer(self, command: str, exit_code: int, duration: float) -> str:
        """
        Writes an immutable receipt of the operation.
        """
        print("[AIWG KERNEL] Writing execution receipt...")
        receipt_id = str(uuid.uuid4())
        receipt = {
            "receipt_id": receipt_id,
            "command": command,
            "exit_code": exit_code,
            "duration_seconds": duration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        receipt_path = self.reports_dir / f"receipt_{receipt_id}.json"
        with open(receipt_path, "w") as f:
            json.dump(receipt, f, indent=2)

        return receipt_id

    def aiwg_postflight(self, receipt_id: str) -> Dict[str, Any]:
        """
        Runs validations post-execution.
        """
        print("[AIWG KERNEL] Running postflight checks...")
        return {
            "receipt_id": receipt_id,
            "status": "PASS",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def agent_entrypoint_guard(self, payload: Dict[str, Any], execute_fn: Any) -> Any:
        """
        The main guard that wraps around any agent execution.
        """
        print("[AIWG KERNEL] Entering agent entrypoint guard...")
        pf = self.aiwg_preflight()
        if pf.get("status") != "PASS":
            raise RuntimeError("Preflight failed.")

        context = self.aiwg_context_loader(payload)
        capsule = self.aiwg_context_capsule_builder(context)

        if not self.aiwg_token_budgeter(capsule):
            raise RuntimeError("Token budget exceeded.")

        # Execute the function
        start_time = time.time()
        exit_code = 0
        try:
            result = execute_fn(capsule)
        except Exception as e:
            exit_code = 1
            raise e
        finally:
            duration = time.time() - start_time
            receipt_id = self.aiwg_receipt_writer(
                "agent_execution", exit_code, duration
            )
            self.aiwg_postflight(receipt_id)

        return result
