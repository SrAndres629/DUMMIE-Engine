# Spec Reference: 130_trusted_workstation_mode
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

    def _run_git(
        self, args: List[str], check: bool = True
    ) -> subprocess.CompletedProcess:
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.workspace_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=check,
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Git command failed: {' '.join(e.cmd)} | Error: {e.stderr.strip()}"
            )
            raise

    def sync_before_action(self):
        """
        Pulls the latest changes from main to ensure the agent is working on fresh code.
        """
        logger.debug("[RepoGuard] Synchronizing with remote (pull --rebase)...")
        try:
            # Asegurar que estamos en main o la rama de trabajo
            # self._run_git(["checkout", "main"])
            self._run_git(["fetch", "origin"])
            self._run_git(["pull", "--rebase", "origin", "main"])
            logger.debug("[RepoGuard] Workspace is up to date.")
        except Exception as e:
            logger.error(f"[RepoGuard] Sync failed: {e}")
            raise RuntimeError(f"Workspace synchronization failed: {e}")

    def validate_state(self, files: List[str]):
        """
        [POLICY] Audita los archivos antes de permitir un commit.
        """
        for f in files:
            path = os.path.join(self.workspace_root, f)
            if not os.path.exists(path):
                continue

            with open(path, "r", errors="ignore") as file:
                content = file.read()

                # 1. Detectar Secretos
                if "ghp_" in content or "github_pat_" in content:
                    logger.critical(
                        f"[RepoGuard] SECURITY BLOCK: Hardcoded token detected in {f}"
                    )
                    raise RuntimeError(f"Security Violation: Hardcoded token in {f}")

                # 2. Detectar Marcadores de Conflicto
                if "<<<<<<<" in content or "=======" in content or ">>>>>>>" in content:
                    logger.critical(
                        f"[RepoGuard] INTEGRITY BLOCK: Unresolved conflict markers in {f}"
                    )
                    raise RuntimeError(f"Integrity Violation: Conflict markers in {f}")

        logger.debug("[RepoGuard] Validation passed.")

    def commit_and_push_atomic(self, files: List[str], message: str):
        """
        Realiza un commit y push atómico a main tras validación estricta.
        """
        if not files:
            logger.warning("[RepoGuard] No files to commit.")
            return

        # [NEW] Validación de Política
        self.validate_state(files)

        logger.debug(f"[RepoGuard] Performing atomic commit for {len(files)} files...")
        try:
            # 1. Stage files
            self._run_git(["add"] + files)

            # 2. Commit con metadatos de evolución
            full_message = f"🧠 [EVOLUTION] {message}\n\nAgent-ID: {self.agent_id}\nTimestamp: {datetime.utcnow().isoformat()}"
            self._run_git(["commit", "-m", full_message])

            # 3. Sincronización Final (Evitar Out-of-Sync)
            logger.debug("[RepoGuard] Final sync before push...")
            self._run_git(["pull", "--rebase", "origin", "main"])

            # 4. Push Seguro
            self._run_git(["push", "origin", "main"])

            logger.debug("[RepoGuard] Atomic push successful.")
        except Exception as e:
            logger.error(f"[RepoGuard] Atomic push failed: {e}")
            raise RuntimeError(f"Atomic evolution push failed: {e}")

    def self_heal_workspace(self):
        """
        [WAVE 10] Intenta resolver problemas comunes en el repositorio automáticamente.
        """
        logger.debug("[RepoGuard] Running self-healing routines...")
        # 1. Eliminar ramas locales huérfanas
        self._run_git(["remote", "prune", "origin"])
        # 2. Limpiar archivos no rastreados (excepto configuraciones críticas)
        # self._run_git(["clean", "-fd", "-e", "*.json"])
        logger.debug("[RepoGuard] Self-healing completed.")

    def reserve_locus(self, files: List[str]):
        """
        [WAVE 10] Registra una reserva de archivos en el 4D-TES.
        (Stub para integración con mcp_gateway/event_store)
        """
        for f in files:
            logger.debug(f"[RepoGuard] RESERVING LOCUS for: {f}")
            # Aquí se llamaría a dummie_execute_capability('local.crystallize', ...)
            # marcando el nodo como RESERVED.

    def release_locus(self, files: List[str]):
        """
        Libera la reserva de archivos.
        """
        for f in files:
            logger.debug(f"[RepoGuard] RELEASING LOCUS for: {f}")
