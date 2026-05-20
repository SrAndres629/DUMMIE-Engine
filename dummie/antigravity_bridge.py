from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any


class DummieAntigravityBridge:
    """
    Programmatic facade to interface with Antigravity CLI.
    Allows DUMMIE Engine to delegate complex tasks and subagent runs to Antigravity CLI.
    """

    def __init__(self, approval_mode: str = "yolo"):
        self.approval_mode = approval_mode
        self.binary_path = shutil.which("antigravity")

    def is_available(self) -> bool:
        return self.binary_path is not None

    def execute_command(self, args: list[str], cwd: str | None = None) -> dict[str, Any]:
        """
        Executes an Antigravity command with the configured approval mode.
        """
        if not self.is_available():
            return {
                "status": "FAIL",
                "error": "Antigravity CLI binary not found in PATH",
            }

        cmd = [self.binary_path] + args
        if "--approval-mode" not in args:
            cmd.append(f"--approval-mode={self.approval_mode}")

        env = dict(os.environ)
        env["ANTIGRAVITY_APPROVAL_MODE"] = self.approval_mode
        env["GEMINI_APPROVAL_MODE"] = self.approval_mode

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                cwd=cwd,
                check=False,
            )
            return {
                "status": "PASS" if result.returncode == 0 else "FAIL",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
            }
