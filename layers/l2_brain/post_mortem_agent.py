import json
import logging
import fcntl
import os
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("post-mortem-agent")

class PostMortemAnalyst:
    """
    Agente de Confiabilidad Cognitiva (RE).
    Analiza fallas en el Ledger y genera parches de reparación seguros.
    """
    def __init__(self, ledger_path: str, skills_dir: str, state_path: str):
        self.ledger_path = ledger_path
        self.skills_dir = Path(skills_dir)
        self.state_path = Path(state_path)
        # Límites de Guardia (Guardrails) para evitar bucles de sobre-optimización
        self.guardrails = {
            "max_timeout": 60,
            "max_retries": 5,
            "allowed_patch_keys": ["timeout", "retry_policy", "concurrency"]
        }

    async def analyze_failures(self):
        """
        Analiza las entradas de fallo en el Ledger desde el último punto conocido.
        [Metacognición: Mitigación de Gasto de Tokens]
        """
        if not os.path.exists(self.ledger_path):
            return

        last_pos = self._get_last_position()
        
        with open(self.ledger_path, "r") as f:
            f.seek(last_pos)
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("status") == "FAILED":
                        await self._diagnose_and_propose(entry)
                except json.JSONDecodeError:
                    continue
            
            # Guardar nueva posición para el próximo ciclo
            self._save_position(f.tell())

    async def _diagnose_and_propose(self, entry: Dict[str, Any]):
        """
        Identifica la causa raíz y genera un Shadow Patch (.patch.json).
        """
        agent_name = entry.get("agent", "unknown")
        error_msg = entry.get("details", {}).get("error", "").lower()
        
        logger.info(f"Diagnosing failure for agent {agent_name}: {error_msg}")
        
        updates = {}
        reason = ""

        if "timeout" in error_msg:
            updates["timeout"] = 30 # Valor adaptativo sugerido
            reason = "Automatic timeout expansion due to execution failure."
        
        if updates:
            self._write_shadow_patch(agent_name, updates, reason)

    def _write_shadow_patch(self, agent_name: str, updates: Dict[str, Any], reason: str):
        """
        Escribe el parche con bloqueo de archivo para evitar colisiones con el SkillBinder.
        """
        patch_path = self.skills_dir / f"{agent_name}.patch.json"
        patch_data = {
            "agent": agent_name,
            "updates": updates,
            "metadata": {
                "reason": reason,
                "timestamp": str(os.times())
            }
        }

        with open(patch_path, "w") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX)
                json.dump(patch_data, f, indent=2)
                logger.warning(f"Shadow Patch CRYSTALLIZED for {agent_name}: {reason}")
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def _get_last_position(self) -> int:
        if not self.state_path.exists(): return 0
        try:
            return int(self.state_path.read_text())
        except: return 0

    def _save_position(self, pos: int):
        self.state_path.write_text(str(pos))
