import logging
import os
import subprocess
from typing import Dict, Any

logger = logging.getLogger("dummie.muscle.workstation")

class WorkstationOperator:
    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.abspath(workspace_root)

    async def execute_action(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta una acción física en la estación de trabajo.
        MANDATO: Ejecución real habilitada (NO MORE DRY RUNS).
        """
        logger.info(f"L5 Sovereign Execution: {action_type}")
        
        # Validar zona segura (Safe Zone) para evitar destrucción fuera del repo
        if action_type in {"shell_command", "file_snapshot", "write_file"}:
            target_path = params.get("path", "")
            if target_path:
                abs_target = os.path.abspath(os.path.join(self.workspace_root, target_path))
                if not abs_target.startswith(self.workspace_root):
                    return {"status": "ERROR", "message": "SOVEREIGN_VETO: Intento de escritura fuera de la zona segura."}

        if action_type == "shell_command":
            return await self._run_shell_real(params.get("command", ""))
        elif action_type == "file_snapshot":
            return await self._create_snapshot(params.get("path", ""))
        elif action_type == "write_file":
            return await self._write_file_real(params.get("path", ""), params.get("content", ""))
        else:
            return {"status": "ERROR", "message": f"Action type {action_type} not implemented for sovereign mode."}

    async def _run_shell_real(self, command: str) -> Dict[str, Any]:
        """Ejecución real de comandos shell con captura de salida."""
        try:
            logger.info(f"SVRN_EXEC Shell: {command}")
            # Ejecución en el CWD del workspace_root
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=self.workspace_root,
                timeout=60
            )
            
            status = "SUCCESS" if result.returncode == 0 else "FAILED"
            return {
                "status": status,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"status": "ERROR", "message": "TIMEOUT: La ejecución excedió el límite de 60s."}
        except Exception as e:
            return {"status": "ERROR", "message": f"EXECUTION_FAILURE: {str(e)}"}

    async def _write_file_real(self, path: str, content: str) -> Dict[str, Any]:
        """Escritura real de archivos en el disco."""
        try:
            abs_path = os.path.join(self.workspace_root, path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"status": "SUCCESS", "path": path}
        except Exception as e:
            return {"status": "ERROR", "message": f"WRITE_FAILURE: {str(e)}"}

    async def _create_snapshot(self, path: str) -> Dict[str, Any]:
        import uuid
        import shutil
        
        abs_target = os.path.abspath(os.path.join(self.workspace_root, path))
        snapshot_id = f"snap_{uuid.uuid4().hex[:8]}"
        checkpoint_dir = os.path.join(self.workspace_root, ".aiwg", "checkpoints", snapshot_id)
        
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
