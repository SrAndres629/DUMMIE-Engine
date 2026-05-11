import os
import subprocess
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger("nervous.repo_guard")

class RepoGuard:
    """
    [L1_NERVOUS] Atomic Evolution & Conflict Guard.
    Garantiza que las operaciones de Git sean atómicas, seguras y libres de conflictos.
    """
    def __init__(self, workspace_root: str, agent_id: str = "DUMMIE_CORE"):
        self.workspace_root = workspace_root
        self.agent_id = agent_id

    def _run_git(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.workspace_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {' '.join(e.cmd)} | Error: {e.stderr.strip()}")
            raise

    def sync_before_action(self):
        """
        Pulls the latest changes from main to ensure the agent is working on fresh code.
        """
        logger.info("[RepoGuard] Synchronizing with remote (pull --rebase)...")
        try:
            # Asegurar que estamos en main o la rama de trabajo
            # self._run_git(["checkout", "main"])
            self._run_git(["fetch", "origin"])
            self._run_git(["pull", "--rebase", "origin", "main"])
            logger.info("[RepoGuard] Workspace is up to date.")
        except Exception as e:
            logger.error(f"[RepoGuard] Sync failed: {e}")
            raise RuntimeError(f"Workspace synchronization failed: {e}")

    def commit_and_push_atomic(self, files: List[str], message: str):
        """
        Performs an atomic commit and push to main.
        """
        if not files:
            logger.warning("[RepoGuard] No files to commit.")
            return

        logger.info(f"[RepoGuard] Performing atomic commit for {len(files)} files...")
        try:
            # 1. Stage files
            self._run_git(["add"] + files)
            
            # 2. Commit
            full_message = f"🧠 [EVOLUTION] {message}\n\nAgent-ID: {self.agent_id}\nTimestamp: {datetime.utcnow().isoformat()}"
            self._run_git(["commit", "-m", full_message])
            
            # 3. Final Sync & Push
            logger.info("[RepoGuard] Final sync before push...")
            self._run_git(["pull", "--rebase", "origin", "main"])
            self._run_git(["push", "origin", "main"])
            
            logger.info("[RepoGuard] Atomic push successful.")
        except Exception as e:
            logger.error(f"[RepoGuard] Atomic push failed: {e}")
            # En caso de fallo en el push, podríamos intentar revertir el commit local
            # para no dejar el repo en estado inconsistente, pero el rebase suele resolverlo.
            raise RuntimeError(f"Atomic evolution push failed: {e}")

    def reserve_locus(self, files: List[str]):
        """
        [WAVE 10] Registra una reserva de archivos en el 4D-TES.
        (Stub para integración con mcp_gateway/event_store)
        """
        for f in files:
            logger.info(f"[RepoGuard] RESERVING LOCUS for: {f}")
            # Aquí se llamaría a dummie_execute_capability('local.crystallize', ...)
            # marcando el nodo como RESERVED.

    def release_locus(self, files: List[str]):
        """
        Libera la reserva de archivos.
        """
        for f in files:
            logger.info(f"[RepoGuard] RELEASING LOCUS for: {f}")

