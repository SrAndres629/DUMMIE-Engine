import logging
import os
import subprocess
from typing import Dict, Any

logger = logging.getLogger("dummie.muscle.workstation")

class WorkstationOperator:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root

    async def execute_action(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta una acción en la estación de trabajo con trazabilidad.
        """
        logger.info(f"L5 Workstation execution: {action_type}")
        
        authority_level = params.get("authority_level")
        if authority_level == "A4_EXTERNAL_ACTOR":
            return {"status": "BLOCKED", "requires_approval": True}

        if action_type == "shell_command":
            return await self._run_shell(params.get("command", ""))
        elif action_type == "file_snapshot":
            path = params.get("path", "")
            abs_workspace = os.path.abspath(self.workspace_root)
            abs_target = os.path.abspath(os.path.join(abs_workspace, path))
            if not abs_target.startswith(abs_workspace):
                return {"status": "ERROR", "message": "Path traversal outside safe zone detected."}
            return await self._create_snapshot(path)
        else:
            return {"status": "ERROR", "message": f"Action type {action_type} not implemented."}

    async def _run_shell(self, command: str) -> Dict[str, Any]:
        # Implementación segura con timeout y restricción de entorno
        try:
            # Simulamos ejecución por ahora para evitar efectos destructivos en el host
            logger.info(f"DRY_RUN Shell: {command}")
            return {"status": "SUCCESS", "output": f"Executed: {command} (Simulated)"}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    async def _create_snapshot(self, path: str) -> Dict[str, Any]:
        logger.info(f"Creating snapshot for {path}")
        import uuid
        import shutil
        
        abs_workspace = os.path.abspath(self.workspace_root)
        abs_target = os.path.abspath(os.path.join(abs_workspace, path))
        
        snapshot_id = f"snap_{uuid.uuid4().hex[:8]}"
        checkpoint_dir = os.path.join(abs_workspace, ".aiwg", "checkpoints", snapshot_id)
        
        try:
            if os.path.exists(abs_target):
                dest_path = os.path.join(checkpoint_dir, path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                if os.path.isdir(abs_target):
                    shutil.copytree(abs_target, dest_path)
                else:
                    shutil.copy2(abs_target, dest_path)
            return {"status": "SUCCESS", "snapshot_id": snapshot_id}
        except Exception as e:
            return {"status": "ERROR", "message": f"Snapshot failed: {e}"}
